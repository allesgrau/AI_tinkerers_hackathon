from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from voiceguard.models import VerificationEvent, VerificationResult
from voiceguard.otp import generate_otp, hash_otp, verify_otp
from voiceguard.pesel import lookup_patient
from voiceguard.voice import VoiceVerifier

if TYPE_CHECKING:
    from voiceguard.server.events import EventBus


class VerificationSession:
    def __init__(self, pesel: str, db_path: str = "hospital_agent.db") -> None:
        self.session_id = str(uuid.uuid4())
        self.pesel = pesel
        self.db_path = db_path
        self.events: list[VerificationEvent] = []
        self.result = VerificationResult(session_id=self.session_id)
        self._otp_hash: str | None = None
        self._voice_verifier = VoiceVerifier()
        self._event_bus: EventBus | None = None

    def attach_event_bus(self, bus: EventBus) -> None:
        """Attach an EventBus so _emit also broadcasts to WebSocket clients."""
        self._event_bus = bus

    def _emit(self, step: str, status: str, details: dict | None = None, level: str = "info") -> None:
        self.events.append(
            VerificationEvent(
                ts=datetime.utcnow(),
                step=step,
                status=status,
                details=details or {},
                level=level,
            )
        )
        # Broadcast to WebSocket clients if event bus is attached
        if self._event_bus is not None:
            from voiceguard.server.events import Event

            self._event_bus.emit_sync(
                self.session_id,
                Event("step.update", {"step": step, "status": status, **(details or {})}),
            )

    def verify_pesel(self) -> bool:
        patient = lookup_patient(self.pesel, db_path=self.db_path)
        if patient is None:
            self._emit("pesel", "failed", {"reason": "patient_not_found"}, level="warn")
            self.result.pesel_verified = False
            return False

        masked_phone = f"{patient['phone_number'][:6]}***"
        self._emit("pesel", "verified", {"full_name": patient["full_name"], "phone_number": masked_phone})
        self.result.pesel_verified = True
        return True

    def send_otp(self) -> str:
        code = generate_otp()
        self._otp_hash = hash_otp(code)
        self._emit("otp", "sent", {"otp_hash_stored": True})
        return code

    def verify_otp(self, code: str) -> bool:
        if self._otp_hash is None:
            self._emit("otp", "failed", {"reason": "otp_not_generated"}, level="warn")
            return False

        ok = verify_otp(code, self._otp_hash)
        self.result.otp_verified = ok
        self._emit("otp", "verified" if ok else "failed")
        return ok

    def verify_voice(self, audio_bytes: bytes) -> VerificationResult:
        verified, score = self._voice_verifier.verify(audio_bytes=audio_bytes)
        self.result.voice_verified = verified
        self.result.voice_score = score
        self._emit("voice", "verified" if verified else "failed", {"score": score})

        self.result.completed = (
            self.result.pesel_verified
            and self.result.otp_verified
            and self.result.voice_verified
        )
        return self.result
