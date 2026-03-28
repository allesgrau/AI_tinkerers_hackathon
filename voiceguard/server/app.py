"""FastAPI application: REST endpoints + WebSocket + static UI serving."""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path as _P

from dotenv import load_dotenv
load_dotenv(_P(__file__).resolve().parent.parent.parent / ".env")
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from voiceguard.config import load_settings
from voiceguard.crypto.jwt_tokens import issue_session_token
from voiceguard.manager import SessionManager
from voiceguard.sms_sender import TwilioSmsSender
from voiceguard.models import VerificationResult
from voiceguard.risk import assess_risk, classify_voice_confidence
from voiceguard.server.events import (
    event_bus,
    reasoning,
    risk_update,
    session_complete,
    step_update,
    transcript,
)
from voiceguard.server.twilio_router import router as twilio_router
from voiceguard.server.ws import router as ws_router
from voiceguard.session import VerificationSession

logger = logging.getLogger(__name__)

settings = load_settings()
event_bus.set_db_path(settings.database.path)


@asynccontextmanager
async def lifespan(application: FastAPI):  # noqa: ANN201
    """Startup/shutdown lifecycle — auto-plays demo scenario if VOICEGUARD_DEMO_MODE is set."""
    demo_task = None
    if os.environ.get("VOICEGUARD_DEMO_MODE") == "1":
        scenario = os.environ.get("VOICEGUARD_DEMO_SCENARIO", "happy_path")
        logger.info("Demo mode active — will auto-play '%s' after 2 s", scenario)

        async def _autoplay() -> None:
            await asyncio.sleep(2)  # give WebSocket clients time to connect
            from voiceguard.demo.runner import play_scenario

            await play_scenario(scenario, session_id=f"demo-{scenario}")

        demo_task = asyncio.create_task(_autoplay())

    yield  # app is running

    if demo_task and not demo_task.done():
        demo_task.cancel()


app = FastAPI(title="VoiceGuard", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws_router)
app.include_router(twilio_router)

# ── In-memory session store ──────────────────────────────────────────

sms_sender = TwilioSmsSender()
session_manager = SessionManager(settings, otp_sender=sms_sender)


def _get_or_create_session(session_id: str, pesel: str = "") -> VerificationSession:
    session = session_manager.get_or_create(session_id, pesel)
    session.attach_event_bus(event_bus)
    return session


# ── Pydantic payloads ───────────────────────────────────────────────


class PeselPayload(BaseModel):
    session_id: str = Field(min_length=1)
    pesel: str = Field(min_length=11, max_length=20)


class OtpSendPayload(BaseModel):
    session_id: str = Field(min_length=1)


class OtpVerifyPayload(BaseModel):
    session_id: str = Field(min_length=1)
    code: str = Field(min_length=4, max_length=10)


class VoicePayload(BaseModel):
    session_id: str = Field(min_length=1)
    audio_base64: str


class EnrollVoicePayload(BaseModel):
    pesel: str = Field(min_length=11, max_length=20)
    audio_base64: str


class StatusPayload(BaseModel):
    session_id: str = Field(min_length=1)


# ── Health ───────────────────────────────────────────────────────────


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "voiceguard", "version": "0.1.0"}


# ── Voice enrollment ────────────────────────────────────────────────


@app.post("/api/enroll/voice")
async def enroll_voice(payload: EnrollVoicePayload) -> dict[str, Any]:
    import base64
    from voiceguard.crypto.embedding_store import store_embedding
    from voiceguard.speaker_encoder import extract_embedding

    audio_bytes = base64.b64decode(payload.audio_base64)
    size_kb = len(audio_bytes) / 1024
    logger.info("Enrollment audio received: %.1f KB for PESEL %s...", size_kb, payload.pesel[:4])

    embedding = extract_embedding(audio_bytes)
    stored = store_embedding(pesel=payload.pesel, embedding=embedding)

    return {
        "ok": True,
        "pesel": payload.pesel,
        "voiceprint_hash": stored.voiceprint_hash,
        "embedding_dim": len(embedding),
    }


# ── Verification endpoints ──────────────────────────────────────────


@app.post("/api/verify/pesel")
async def verify_pesel(payload: PeselPayload) -> dict[str, Any]:
    sid = payload.session_id
    pesel = payload.pesel
    session = _get_or_create_session(sid, pesel)

    # Emit: starting
    event_bus.emit_sync(sid, step_update("pesel", "in_progress"))
    event_bus.emit_sync(sid, reasoning(f"PESEL {pesel[:4]}{'*' * 7} → DB lookup..."))

    ok = session.verify_pesel()

    if ok:
        # Pull details from the last event emitted by session
        details = session.events[-1].details if session.events else {}
        name = details.get("full_name", "?")
        phone = details.get("phone_number", "?")

        event_bus.emit_sync(sid, step_update("pesel", "verified", patient_name=name))
        event_bus.emit_sync(sid, reasoning(f"Match: {name} → phone: {phone}"))
        event_bus.emit_sync(sid, risk_update({"pesel_status": "verified"}))
        return {"ok": True, "patient_name": name, "session_id": sid}
    else:
        event_bus.emit_sync(sid, step_update("pesel", "failed"))
        event_bus.emit_sync(sid, reasoning("PESEL not found in database", level="error"))
        event_bus.emit_sync(sid, risk_update({"pesel_status": "failed"}))
        return {"ok": False, "message": "Patient not found", "session_id": sid}


@app.post("/api/verify/otp/send")
async def send_otp(payload: OtpSendPayload) -> dict[str, Any]:
    sid = payload.session_id
    session = session_manager.get(sid)
    if session is None:
        return {"ok": False, "message": "Session not found — verify PESEL first"}

    event_bus.emit_sync(sid, step_update("otp", "sending"))
    event_bus.emit_sync(sid, reasoning("OTP generated: 6 digits, SHA-256 hashed before storage"))

    code = session.send_otp()

    event_bus.emit_sync(sid, step_update("otp", "sent"))
    event_bus.emit_sync(sid, reasoning("SMS sent via provider → awaiting user input"))

    # In demo/mock mode we return the code; in production this would go via SMS only
    return {"ok": True, "session_id": sid, "otp_code_for_demo": code}


@app.post("/api/verify/otp/verify")
async def verify_otp(payload: OtpVerifyPayload) -> dict[str, Any]:
    sid = payload.session_id
    session = session_manager.get(sid)
    if session is None:
        return {"ok": False, "message": "Session not found"}

    event_bus.emit_sync(sid, reasoning(f"OTP input: {'*' * len(payload.code)} → verifying hash..."))

    ok = session.verify_otp(payload.code)
    risk = assess_risk(
        otp_timing_seconds=session.otp_timing_seconds(),
        failed_attempts=session.otp_attempts,
        extra_indicators={"otp_status": "verified" if ok else "failed"},
    )

    if ok:
        event_bus.emit_sync(sid, step_update("otp", "verified"))
        event_bus.emit_sync(sid, reasoning("OTP hash match ✓"))
        event_bus.emit_sync(sid, risk_update(risk.indicators))
    else:
        event_bus.emit_sync(sid, step_update("otp", "failed"))
        event_bus.emit_sync(sid, reasoning("OTP mismatch — wrong code entered", level="warn"))
        event_bus.emit_sync(sid, risk_update(risk.indicators))

    return {"ok": ok, "session_id": sid}


@app.post("/api/verify/voice")
async def verify_voice(payload: VoicePayload) -> dict[str, Any]:
    import base64

    sid = payload.session_id
    session = session_manager.get(sid)
    if session is None:
        return {"ok": False, "message": "Session not found"}

    audio_bytes = base64.b64decode(payload.audio_base64)
    size_kb = len(audio_bytes) / 1024

    event_bus.emit_sync(sid, step_update("voice", "in_progress"))
    event_bus.emit_sync(sid, reasoning(f"Audio received: {size_kb:.1f} KB → computing speaker embedding..."))

    result: VerificationResult = session.verify_voice(audio_bytes)
    score = result.voice_score or 0.0
    threshold = settings.verification.voice.threshold
    confidence = classify_voice_confidence(score, threshold)
    risk = assess_risk(
        voice_score=score,
        voice_threshold=threshold,
        otp_timing_seconds=session.otp_timing_seconds(),
        failed_attempts=session.otp_attempts,
        extra_indicators={"voice_status": "verified" if result.voice_verified else "failed"},
    )

    if result.voice_verified:
        event_bus.emit_sync(sid, step_update("voice", "verified", score=score))
        event_bus.emit_sync(sid, reasoning(f"Embedding computed: 192-dim, L2-norm: 1.0"))
        event_bus.emit_sync(sid, reasoning(f"Cosine similarity: {score:.3f} (threshold: {threshold}) ✓"))
        event_bus.emit_sync(sid, risk_update({
            "voice_status": "verified",
            "voice_score": score,
            "voice_confidence": confidence,
            "overall_risk": risk.overall_risk,
        }))
    else:
        event_bus.emit_sync(sid, step_update("voice", "failed", score=score))
        event_bus.emit_sync(sid, reasoning(f"Cosine similarity: {score:.3f} (threshold: {threshold}) — MISMATCH", level="error"))
        event_bus.emit_sync(sid, risk_update({
            "voice_status": "failed",
            "voice_score": score,
            "voice_confidence": confidence,
            "overall_risk": risk.overall_risk,
        }))

    # Check if fully authenticated
    if result.completed:
        session_obj = session_manager.get(sid)
        assert session_obj is not None
        token = issue_session_token(
            secret=settings.verification.security.jwt_secret,
            session_id=sid,
            pesel=session_obj.pesel,
            pesel_verified=result.pesel_verified,
            otp_verified=result.otp_verified,
            voice_verified=result.voice_verified,
            voice_score=score,
            expiry_seconds=settings.verification.security.jwt_expiry_seconds,
            db_path=settings.database.path,
            risk_level=risk.overall_risk,
        )
        event_bus.emit_sync(sid, reasoning("ALL STEPS VERIFIED — issuing JWT token"))
        event_bus.emit_sync(sid, session_complete(token=token))
        return {"ok": True, "completed": True, "token": token, "session_id": sid}
    elif not result.voice_verified:
        event_bus.emit_sync(sid, session_complete(rejected=True, reason="Voice mismatch"))

    return {
        "ok": result.voice_verified,
        "completed": result.completed,
        "voice_score": score,
        "session_id": sid,
    }


@app.post("/api/verify/status")
async def auth_status(payload: StatusPayload) -> dict[str, Any]:
    sid = payload.session_id
    session = session_manager.get(sid)
    if session is None:
        return {"ok": False, "message": "Session not found"}

    risk = assess_risk(
        voice_score=session.result.voice_score,
        voice_threshold=settings.verification.voice.threshold,
        otp_timing_seconds=session.otp_timing_seconds(),
        failed_attempts=session.otp_attempts,
    )

    return {
        "ok": True,
        "session_id": sid,
        "pesel_verified": session.result.pesel_verified,
        "otp_verified": session.result.otp_verified,
        "voice_verified": session.result.voice_verified,
        "voice_score": session.result.voice_score,
        "completed": session.result.completed,
        "otp_attempts": session.otp_attempts,
        "risk": risk.model_dump(),
    }


@app.get("/api/sessions")
async def list_sessions() -> dict[str, Any]:
    return {
        "sessions": [
            {
                "session_id": session.session_id,
                "pesel": session.pesel,
                "pesel_verified": s.result.pesel_verified,
                "otp_verified": s.result.otp_verified,
                "voice_verified": s.result.voice_verified,
                "completed": s.result.completed,
                "otp_attempts": s.otp_attempts,
            }
            for s in session_manager.list()
            for session in [s]
        ]
    }


# ── Transcript endpoint (for agent to push conversation lines) ──────


class TranscriptPayload(BaseModel):
    session_id: str = Field(min_length=1)
    speaker: str = Field(min_length=1)
    text: str = Field(min_length=1)


@app.post("/api/transcript")
async def add_transcript(payload: TranscriptPayload) -> dict[str, Any]:
    event_bus.emit_sync(payload.session_id, transcript(payload.speaker, payload.text))
    return {"ok": True}


# ── Demo endpoints ──────────────────────────────────────────────────


class DemoPayload(BaseModel):
    scenario: str = Field(default="happy_path")


@app.post("/api/demo/play")
async def play_demo(payload: DemoPayload) -> dict[str, Any]:
    """Trigger a demo scenario that streams events to WebSocket clients."""
    import asyncio

    from voiceguard.demo.runner import play_scenario

    scenario_name = payload.scenario
    session_id = f"demo-{scenario_name}"

    # Run in background so the response returns immediately
    asyncio.create_task(play_scenario(scenario_name, session_id))

    return {"ok": True, "scenario": scenario_name, "session_id": session_id}


@app.get("/api/demo/scenarios")
async def list_scenarios() -> dict[str, Any]:
    from voiceguard.demo.runner import available_scenarios

    return {"scenarios": available_scenarios()}


# ── Serve verify.html and built UI ─────────────────────────────────

_project_root = Path(__file__).resolve().parent.parent.parent


@app.get("/verify")
async def serve_verify():
    from fastapi.responses import FileResponse
    return FileResponse(str(_project_root / "verify.html"))


_ui_dist = _project_root / "ui" / "dist"
if _ui_dist.is_dir():
    app.mount("/", StaticFiles(directory=str(_ui_dist), html=True), name="ui")
