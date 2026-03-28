from __future__ import annotations

from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.auth_service import AuthService
from app.voice_monitor import get_conversation, list_conversations
from voiceguard.server.ws import router as voiceguard_ws_router


app = FastAPI(title="Hospital Voice Auth Agent", version="0.1.0")
app.include_router(voiceguard_ws_router)
auth_service = AuthService()


class PeselPayload(BaseModel):
    call_id: str = Field(min_length=1)
    pesel: str = Field(min_length=11, max_length=20)


class SmsSendPayload(BaseModel):
    call_id: str = Field(min_length=1)


class SmsVerifyPayload(BaseModel):
    call_id: str = Field(min_length=1)
    code: str = Field(min_length=4, max_length=10)


class AudioPayload(BaseModel):
    call_id: str = Field(min_length=1)
    audio_base64: str
    extension: str = Field(default="wav")


class StatusPayload(BaseModel):
    call_id: str = Field(min_length=1)


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/vapi/tools/collect-pesel")
def collect_pesel(payload: PeselPayload, background_tasks: BackgroundTasks) -> dict:
    result = auth_service.attach_pesel(payload.call_id, payload.pesel)
    if result.get("ok"):
        background_tasks.add_task(auth_service.verify_voice_in_background, payload.call_id)
    return result


@app.post("/vapi/tools/send-sms")
def send_sms(payload: SmsSendPayload) -> dict:
    return auth_service.send_sms(payload.call_id)


@app.post("/vapi/tools/verify-sms")
def verify_sms(payload: SmsVerifyPayload) -> dict:
    return auth_service.verify_sms(payload.call_id, payload.code)


@app.post("/vapi/media/audio")
def media_audio(payload: AudioPayload, background_tasks: BackgroundTasks) -> dict:
    result = auth_service.ingest_audio(payload.call_id, payload.audio_base64, payload.extension)
    background_tasks.add_task(auth_service.verify_voice_in_background, payload.call_id)
    return result


@app.post("/vapi/tools/auth-status")
def auth_status(payload: StatusPayload) -> dict:
    return auth_service.get_status(payload.call_id)


@app.get("/api/voice-monitor/conversations")
def voice_monitor_conversations() -> JSONResponse:
    return JSONResponse({"items": list_conversations()})


@app.get("/api/voice-monitor/conversations/{call_id}")
def voice_monitor_conversation(call_id: str) -> JSONResponse:
    conversation = get_conversation(call_id)
    if conversation is None:
        return JSONResponse({"ok": False, "message": "Conversation not found."}, status_code=404)
    return JSONResponse({"ok": True, "item": conversation})
