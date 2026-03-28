from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class LiveCallSession:
    session_id: str
    call_sid: str
    from_number: str | None = None
    to_number: str | None = None
    stream_sid: str | None = None
    model: str | None = None
    status: str = "created"
    started_at: str = field(default_factory=_utc_now)
    last_event_at: str = field(default_factory=_utc_now)
    tool_count: int = 0
    transcript_count: int = 0
    last_tool_name: str | None = None
    last_error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LiveCallRegistry:
    def __init__(self) -> None:
        self._sessions: dict[str, LiveCallSession] = {}
        self._lock = Lock()

    def upsert(
        self,
        session_id: str,
        *,
        call_sid: str | None = None,
        from_number: str | None = None,
        to_number: str | None = None,
        stream_sid: str | None = None,
        model: str | None = None,
        status: str | None = None,
    ) -> LiveCallSession:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                session = LiveCallSession(
                    session_id=session_id,
                    call_sid=call_sid or session_id,
                    from_number=from_number,
                    to_number=to_number,
                    stream_sid=stream_sid,
                    model=model,
                    status=status or "created",
                )
                self._sessions[session_id] = session
            else:
                if call_sid:
                    session.call_sid = call_sid
                if from_number:
                    session.from_number = from_number
                if to_number:
                    session.to_number = to_number
                if stream_sid:
                    session.stream_sid = stream_sid
                if model:
                    session.model = model
                if status:
                    session.status = status
                session.last_event_at = _utc_now()
            return session

    def record_transcript(self, session_id: str) -> None:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                session = LiveCallSession(session_id=session_id, call_sid=session_id)
                self._sessions[session_id] = session
            session.transcript_count += 1
            session.last_event_at = _utc_now()

    def record_tool(self, session_id: str, tool_name: str) -> None:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                session = LiveCallSession(session_id=session_id, call_sid=session_id)
                self._sessions[session_id] = session
            session.tool_count += 1
            session.last_tool_name = tool_name
            session.last_event_at = _utc_now()

    def record_error(self, session_id: str, message: str) -> None:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                session = LiveCallSession(session_id=session_id, call_sid=session_id)
                self._sessions[session_id] = session
            session.last_error = message
            session.status = "error"
            session.last_event_at = _utc_now()

    def end(self, session_id: str, status: str = "completed") -> None:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                session = LiveCallSession(session_id=session_id, call_sid=session_id)
                self._sessions[session_id] = session
            session.status = status
            session.last_event_at = _utc_now()

    def list_sessions(self) -> list[dict[str, Any]]:
        with self._lock:
            sessions = sorted(
                (session.to_dict() for session in self._sessions.values()),
                key=lambda item: item["last_event_at"],
                reverse=True,
            )
        return sessions

    def get(self, session_id: str) -> dict[str, Any] | None:
        with self._lock:
            session = self._sessions.get(session_id)
            return session.to_dict() if session is not None else None

