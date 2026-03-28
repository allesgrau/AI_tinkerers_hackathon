"""Event bus: routes verification events from sessions to WebSocket clients."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import WebSocket

from voiceguard.crypto.audit_chain import append_stream_event

logger = logging.getLogger(__name__)


class Event:
    """A single verification event emitted by the pipeline."""

    __slots__ = ("type", "data", "ts")

    def __init__(self, type: str, data: dict[str, Any] | None = None) -> None:
        self.type = type
        self.data = data or {}
        self.ts = datetime.now(timezone.utc).strftime("%H:%M:%S")

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "ts": self.ts, **self.data}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class EventBus:
    """
    Async pub/sub for verification events.

    Sessions emit events -> EventBus broadcasts to all connected WebSocket
    clients subscribed to that session (or globally via '*').
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, set[WebSocket]] = {}
        self._global_subscribers: set[WebSocket] = set()
        self._lock = asyncio.Lock()
        self._history: dict[str, list[dict[str, Any]]] = {}
        self._db_path = "hospital_agent.db"

    def set_db_path(self, db_path: str) -> None:
        self._db_path = db_path

    def _record_event(self, session_id: str, event: Event) -> tuple[dict[str, Any], str]:
        event_dict = event.to_dict()
        event_dict["session_id"] = session_id
        msg = json.dumps(event_dict, ensure_ascii=False)

        try:
            append_stream_event(event_dict, db_path=self._db_path)
        except Exception:
            logger.exception("Failed to append event to audit chain")

        self._history.setdefault(session_id, []).append(event_dict)
        return event_dict, msg

    async def _broadcast(self, session_id: str, msg: str) -> None:
        targets: list[WebSocket] = []
        async with self._lock:
            targets.extend(self._global_subscribers)
            if session_id in self._subscribers:
                targets.extend(self._subscribers[session_id])

        stale: list[tuple[WebSocket, str]] = []
        for ws in targets:
            try:
                await ws.send_text(msg)
            except Exception:
                stale.append((ws, session_id))

        for ws, sid in stale:
            await self.unsubscribe(ws, sid)
            await self.unsubscribe(ws, "*")

    async def subscribe(self, ws: WebSocket, session_id: str = "*") -> None:
        async with self._lock:
            if session_id == "*":
                self._global_subscribers.add(ws)
            else:
                self._subscribers.setdefault(session_id, set()).add(ws)

    async def unsubscribe(self, ws: WebSocket, session_id: str = "*") -> None:
        async with self._lock:
            if session_id == "*":
                self._global_subscribers.discard(ws)
            else:
                subs = self._subscribers.get(session_id)
                if subs:
                    subs.discard(ws)
                    if not subs:
                        del self._subscribers[session_id]

    async def emit(self, session_id: str, event: Event) -> None:
        """Broadcast an event to all subscribers for this session + global."""
        _, msg = self._record_event(session_id, event)
        await self._broadcast(session_id, msg)

    def emit_sync(self, session_id: str, event: Event) -> None:
        """Record immediately, then fire-and-forget WebSocket broadcast when possible."""
        _, msg = self._record_event(session_id, event)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._broadcast(session_id, msg))
        except RuntimeError:
            logger.debug("No event loop; dropping event %s", event.type)

    def get_history(self, session_id: str) -> list[dict[str, Any]]:
        """Return all past events for a session (for late-joining clients)."""
        return list(self._history.get(session_id, []))

    def clear_history(self, session_id: str) -> None:
        self._history.pop(session_id, None)


# ── Singleton ────────────────────────────────────────────────────────

event_bus = EventBus()


# ── Event factory helpers ────────────────────────────────────────────


def step_update(step: str, status: str, **details: Any) -> Event:
    return Event("step.update", {"step": step, "status": status, **details})


def reasoning(text: str, level: str = "info") -> Event:
    return Event("reasoning.add", {"text": text, "level": level})


def transcript(speaker: str, text: str) -> Event:
    return Event("transcript.add", {"speaker": speaker, "text": text})


def tool_call(name: str, arguments: dict[str, Any] | None = None) -> Event:
    return Event("tool.call", {"name": name, "arguments": arguments or {}})


def tool_result(
    name: str,
    result: dict[str, Any] | None = None,
    success: bool | None = None,
) -> Event:
    payload = {"name": name, "result": result or {}}
    if success is not None:
        payload["success"] = success
    return Event("tool.result", payload)


def call_update(status: str, **details: Any) -> Event:
    return Event("call.update", {"status": status, **details})


def risk_update(indicators: dict[str, Any]) -> Event:
    return Event("risk.update", {"indicators": indicators})


def session_complete(token: str | None = None, rejected: bool = False, reason: str = "") -> Event:
    return Event(
        "session.complete",
        {"token": token, "rejected": rejected, "reason": reason},
    )
