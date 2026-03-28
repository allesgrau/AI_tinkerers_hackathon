"""Twilio + Gemini Live routes — plugs into the VoiceGuard FastAPI app."""

from __future__ import annotations

import asyncio
import html
import json
import os
import uuid
from contextlib import suppress
from urllib.parse import parse_qs

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response

from app.gemini_live_bridge import GeminiLiveTwilioBridge
from app.live_call_registry import LiveCallRegistry
from voiceguard.server.events import Event, call_update, event_bus, reasoning

router = APIRouter()
call_registry = LiveCallRegistry()


# ── helpers ────────────────────────────────────────────────────────


def _infer_public_base_url(request: Request) -> str:
    configured = (
        os.environ.get("PUBLIC_BASE_URL")
        or os.environ.get("PUBLIC_WEBHOOK_BASE_URL")
        or os.environ.get("TWILIO_PUBLIC_BASE_URL")
    )
    if configured:
        return configured.rstrip("/")

    forwarded_proto = request.headers.get("x-forwarded-proto") or request.url.scheme
    forwarded_host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    return f"{forwarded_proto}://{forwarded_host}"


def _to_ws_url(base_url: str, path: str) -> str:
    if base_url.startswith("https://"):
        return f"wss://{base_url.removeprefix('https://')}{path}"
    if base_url.startswith("http://"):
        return f"ws://{base_url.removeprefix('http://')}{path}"
    return f"wss://{base_url}{path}"


async def _parse_request_params(request: Request) -> dict[str, str]:
    if request.method == "GET":
        return {key: value for key, value in request.query_params.items()}
    body = await request.body()
    parsed = parse_qs(body.decode("utf-8"))
    return {key: values[-1] for key, values in parsed.items() if values}


# ── Twilio webhook ─────────────────────────────────────────────────


@router.api_route("/twilio/voice", methods=["GET", "POST"])
async def twilio_voice(request: Request) -> Response:
    params = await _parse_request_params(request)
    call_sid = params.get("CallSid") or f"call-{uuid.uuid4().hex[:12]}"
    from_number = params.get("From")
    to_number = params.get("To")
    public_base_url = _infer_public_base_url(request)
    stream_url = _to_ws_url(public_base_url, "/twilio/media-stream")
    model = os.environ.get("GEMINI_LIVE_MODEL", "models/gemini-3.1-flash-live-preview")

    call_registry.upsert(
        call_sid,
        call_sid=call_sid,
        from_number=from_number,
        to_number=to_number,
        model=model,
        status="connecting",
    )
    event_bus.emit_sync(
        call_sid,
        call_update(
            "connecting",
            from_number=from_number,
            to_number=to_number,
            model=model,
        ),
    )
    event_bus.emit_sync(
        call_sid,
        reasoning("Inbound Twilio call accepted. Opening bidirectional media stream."),
    )

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="{html.escape(stream_url, quote=True)}">
      <Parameter name="callSid" value="{html.escape(call_sid, quote=True)}" />
      <Parameter name="from" value="{html.escape(from_number or '', quote=True)}" />
      <Parameter name="to" value="{html.escape(to_number or '', quote=True)}" />
    </Stream>
  </Connect>
</Response>"""
    return Response(content=twiml, media_type="application/xml")


@router.api_route("/twilio/status", methods=["POST"])
async def twilio_status(request: Request) -> JSONResponse:
    params = await _parse_request_params(request)
    call_sid = params.get("CallSid") or f"call-{uuid.uuid4().hex[:12]}"
    status = params.get("CallStatus", "unknown")
    call_registry.upsert(call_sid, call_sid=call_sid, status=status)
    event_bus.emit_sync(call_sid, call_update(status))
    return JSONResponse({"ok": True})


@router.websocket("/twilio/media-stream")
async def twilio_media_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    bridge: GeminiLiveTwilioBridge | None = None
    bridge_task: asyncio.Task[None] | None = None
    call_sid = ""

    try:
        while True:
            raw_message = await websocket.receive_text()
            payload = json.loads(raw_message)
            event_type = payload.get("event")

            if event_type == "connected":
                continue

            if event_type == "start":
                start_payload = payload.get("start", {})
                custom_params = start_payload.get("customParameters") or {}
                call_sid = (
                    start_payload.get("callSid")
                    or custom_params.get("callSid")
                    or f"call-{uuid.uuid4().hex[:12]}"
                )
                stream_sid = payload.get("streamSid") or start_payload.get("streamSid") or ""
                from_number = custom_params.get("from")
                to_number = custom_params.get("to")

                call_registry.upsert(
                    call_sid,
                    call_sid=call_sid,
                    from_number=from_number,
                    to_number=to_number,
                    stream_sid=stream_sid,
                    model=os.environ.get("GEMINI_LIVE_MODEL", "models/gemini-3.1-flash-live-preview"),
                    status="stream_started",
                )
                event_bus.emit_sync(
                    call_sid,
                    call_update(
                        "stream_started",
                        stream_sid=stream_sid,
                        from_number=from_number,
                        to_number=to_number,
                    ),
                )

                bridge = GeminiLiveTwilioBridge(
                    websocket=websocket,
                    session_id=call_sid,
                    stream_sid=stream_sid,
                    from_number=from_number,
                    to_number=to_number,
                    event_bus=event_bus,
                    registry=call_registry,
                )
                bridge_task = asyncio.create_task(bridge.run())
                continue

            if event_type == "media":
                media_payload = payload.get("media", {})
                if bridge is not None and media_payload.get("payload"):
                    await bridge.enqueue_twilio_payload(media_payload["payload"])
                continue

            if event_type == "dtmf":
                digits = payload.get("dtmf", {}).get("digits", "")
                if call_sid:
                    event_bus.emit_sync(call_sid, Event("call.dtmf", {"digits": digits}))
                continue

            if event_type == "stop":
                if bridge is not None:
                    await bridge.close()
                if call_sid:
                    call_registry.end(call_sid, "stopped")
                    event_bus.emit_sync(call_sid, call_update("stopped"))
                break
    except WebSocketDisconnect:
        if call_sid:
            call_registry.end(call_sid, "disconnected")
            event_bus.emit_sync(call_sid, call_update("disconnected"))
    finally:
        if bridge is not None:
            await bridge.close()
        if bridge_task is not None and not bridge_task.done():
            bridge_task.cancel()
            with suppress(asyncio.CancelledError):
                await bridge_task


# ── Live-call query endpoints ──────────────────────────────────────


@router.get("/api/live-calls")
def live_calls() -> JSONResponse:
    return JSONResponse({"items": call_registry.list_sessions()})


@router.get("/api/live-calls/{call_id}")
def live_call(call_id: str) -> JSONResponse:
    item = call_registry.get(call_id)
    if item is None:
        return JSONResponse({"ok": False, "message": "Call not found."}, status_code=404)
    return JSONResponse({"ok": True, "item": item})
