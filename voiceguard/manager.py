from __future__ import annotations

from voiceguard.config import VoiceGuardSettings
from voiceguard.session import VerificationSession


class SessionManager:
    def __init__(self, settings: VoiceGuardSettings) -> None:
        self.settings = settings
        self._sessions: dict[str, VerificationSession] = {}

    def get_or_create(self, session_id: str, pesel: str = "") -> VerificationSession:
        if session_id not in self._sessions:
            session = VerificationSession(pesel=pesel, settings=self.settings)
            session.session_id = session_id
            self._sessions[session_id] = session
        else:
            session = self._sessions[session_id]
            if pesel:
                session.pesel = pesel
        return session

    def get(self, session_id: str) -> VerificationSession | None:
        return self._sessions.get(session_id)

    def list(self) -> list[VerificationSession]:
        return list(self._sessions.values())
