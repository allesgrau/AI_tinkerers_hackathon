"""WebSocket endpoint for real-time verification streaming."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from voiceguard.server.events import event_bus

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def verification_ws(ws: WebSocket) -> None:
    """
    WebSocket handler for real-time verification UI.

    Client can send:
        {"action": "subscribe", "session_id": "abc123"}
        {"action": "ping"}
        {"action": "history", "session_id": "abc123"}

    Server pushes:
        {"type": "step.update",      "session_id": "...", "step": "pesel", "status": "verified", ...}
        {"type": "reasoning.add",    "session_id": "...", "text": "...", "level": "info"}
        {"type": "transcript.add",   "session_id": "...", "speaker": "agent", "text": "..."}
        {"type": "risk.update",      "session_id": "...", "indicators": {...}}
        {"type": "session.complete", "session_id": "...", "token": "eyJ...", ...}
    """
    await ws.accept()
    subscribed_session = "*"

    try:
        await event_bus.subscribe(ws, "*")
        await ws.send_text(json.dumps({"type": "connected", "status": "ok"}))
        logger.info("WebSocket client connected (global)")

        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_text(json.dumps({"error": "invalid JSON"}))
                continue

            action = msg.get("action")

            if action == "subscribe":
                session_id = msg.get("session_id", "*")
                await event_bus.unsubscribe(ws, subscribed_session)
                await event_bus.subscribe(ws, session_id)
                subscribed_session = session_id
                await ws.send_text(
                    json.dumps({"type": "subscribed", "session_id": session_id})
                )
                logger.info("Client subscribed to session %s", session_id)

            elif action == "history":
                session_id = msg.get("session_id", subscribed_session)
                history = event_bus.get_history(session_id)
                await ws.send_text(
                    json.dumps({"type": "history", "session_id": session_id, "events": history})
                )

            elif action == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))

            else:
                await ws.send_text(json.dumps({"error": f"unknown action: {action}"}))

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    finally:
        await event_bus.unsubscribe(ws, subscribed_session)
        await event_bus.unsubscribe(ws, "*")
