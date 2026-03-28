"""WebSocket endpoint for real-time verification streaming."""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import suppress

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
        {"action": "history", "session_id": "abc123"}
        {"action": "ping"}
        {"type": "scenario.start", "scenario": "happy_path"}

    Server pushes:
        {"type": "connected", "status": "ok"}
        {"type": "scenario.list", "items": [...]}
        {"type": "subscribed", "session_id": "..."}
        {"type": "history", "session_id": "...", "events": [...]}
        ...verification events from the event bus...
    """
    await ws.accept()
    subscribed_session = "*"
    current_demo_task: asyncio.Task[None] | None = None

    try:
        await event_bus.subscribe(ws, subscribed_session)
        await ws.send_text(json.dumps({"type": "connected", "status": "ok"}))

        from voiceguard.demo.runner import available_scenarios
        await ws.send_text(json.dumps({"type": "scenario.list", "items": available_scenarios()}))
        logger.info("WebSocket client connected (session=%s)", subscribed_session)

        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_text(json.dumps({"error": "invalid JSON"}))
                continue

            action = msg.get("action")
            msg_type = msg.get("type")

            if action == "subscribe":
                session_id = msg.get("session_id", "*")
                await event_bus.unsubscribe(ws, subscribed_session)
                subscribed_session = session_id
                await event_bus.subscribe(ws, subscribed_session)
                await ws.send_text(
                    json.dumps({"type": "subscribed", "session_id": subscribed_session})
                )
                logger.info("Client subscribed to session %s", subscribed_session)

            elif action == "history":
                session_id = msg.get("session_id", subscribed_session)
                history = event_bus.get_history(session_id)
                await ws.send_text(
                    json.dumps(
                        {"type": "history", "session_id": session_id, "events": history}
                    )
                )

            elif action == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))

            elif msg_type == "scenario.start":
                scenario_name = msg.get("scenario", "happy_path")
                scenario_session_id = f"demo-{scenario_name}"

                if current_demo_task and not current_demo_task.done():
                    current_demo_task.cancel()
                    with suppress(asyncio.CancelledError):
                        await current_demo_task

                await event_bus.unsubscribe(ws, subscribed_session)
                subscribed_session = scenario_session_id
                await event_bus.subscribe(ws, subscribed_session)

                from voiceguard.demo.runner import play_scenario

                event_bus.clear_history(scenario_session_id)
                await ws.send_text(
                    json.dumps({"type": "session.reset", "scenario": scenario_name})
                )
                await ws.send_text(
                    json.dumps({"type": "subscribed", "session_id": scenario_session_id})
                )
                current_demo_task = asyncio.create_task(
                    play_scenario(scenario_name, session_id=scenario_session_id)
                )

            else:
                await ws.send_text(
                    json.dumps({"error": f"unknown action: {action or msg_type}"})
                )

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    finally:
        if current_demo_task and not current_demo_task.done():
            current_demo_task.cancel()
            with suppress(asyncio.CancelledError):
                await current_demo_task
        await event_bus.unsubscribe(ws, subscribed_session)
        await event_bus.unsubscribe(ws, "*")
