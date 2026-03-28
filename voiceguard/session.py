from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from voiceguard.config import VoiceGuardSettings, load_settings
from voiceguard.db import PatientRepository, SQLitePatientRepository
from voiceguard.exceptions import VerificationStepError
from voiceguard.models import (
    SessionSnapshot,
    StepStatus,
    VerificationEvent,
    VerificationResult,
)
from voiceguard.otp import OtpService
from voiceguard.pesel import is_valid_pesel_format, lookup_patient, normalize_pesel
from voiceguard.providers import OtpSender
from voiceguard.voice import VoiceVerifier

if TYPE_CHECKING:
    from voiceguard.server.events import EventBus


class VerificationSession:
    def __init__(
        self,
        pesel: str,
        *,
        db_path: str | None = None,
        settings: VoiceGuardSettings | None = None,
        patient_repository: PatientRepository | None = None,
        otp_service: OtpService | None = None,
        otp_sender: OtpSender | None = None,
        voice_verifier: VoiceVerifier | None = None,
    ) -> None:
        self.session_id = str(uuid.uuid4())
        self.settings = settings or load_settings()
        self.db_path = db_path or self.settings.database.path
        self.pesel = normalize_pesel(pesel)
        self.patient_repository = patient_repository or SQLitePatientRepository(self.db_path)
        self.otp_service = otp_service or OtpService(self.settings.verification.otp.length)
        self.otp_sender = otp_sender
        self.voice_verifier = voice_verifier or VoiceVerifier(
            threshold=self.settings.verification.voice.threshold
        )

        self.events: list[VerificationEvent] = []
        self.result = VerificationResult(session_id=self.session_id)
        self.patient = None
        self._otp_hash: str | None = None
        self._event_bus: EventBus | None = None
        self.otp_sent_at: datetime | None = None
        self.last_otp_attempt_at: datetime | None = None
        self.otp_attempts: int = 0
        self._steps: dict[str, StepStatus] = {
            "pesel": StepStatus(step="pesel"),
            "otp": StepStatus(step="otp"),
            "voice": StepStatus(step="voice"),
        }

    def attach_event_bus(self, bus: EventBus) -> None:
        self._event_bus = bus

    def _emit(
        self,
        step: str,
        status: str,
        details: dict | None = None,
        level: str = "info",
    ) -> None:
        payload = details or {}
        event = VerificationEvent(
            ts=datetime.utcnow(),
            step=step,
            status=status,
            details=payload,
            level=level,
        )
        self.events.append(event)
        if step in self._steps:
            self._steps[step].status = status
            self._steps[step].details = payload
        # Note: WebSocket broadcasting is handled by the server layer (app.py),
        # not here, to avoid duplicate events and keep a single source of truth.

    def snapshot(self) -> SessionSnapshot:
        return SessionSnapshot(
            session_id=self.session_id,
            pesel=self.pesel,
            steps=list(self._steps.values()),
            result=self.result,
        )

    def verify_pesel(self) -> bool:
        if not is_valid_pesel_format(self.pesel):
            self.result.pesel_verified = False
            self._emit("pesel", "failed", {"reason": "invalid_pesel_format"}, level="warn")
            return False

        patient = lookup_patient(
            self.pesel,
            db_path=self.db_path,
            patient_repository=self.patient_repository,
        )
        if patient is None:
            self.result.pesel_verified = False
            self._emit("pesel", "failed", {"reason": "patient_not_found"}, level="warn")
            return False

        self.patient = patient
        self.result.pesel_verified = True
        masked_phone = (
            f"{patient.phone_number[:6]}***"
            if len(patient.phone_number) > 6
            else "***"
        )
        self._emit(
            "pesel",
            "verified",
            {
                "full_name": patient.full_name,
                "phone_number": masked_phone,
                "pesel": patient.pesel,
            },
        )
        return True

    def send_otp(self) -> str:
        if not self.result.pesel_verified or self.patient is None:
            raise VerificationStepError("PESEL must be verified before sending OTP.")

        code = self.otp_service.issue_code()
        self._otp_hash = self.otp_service.store_hash(code)
        self.otp_sent_at = datetime.utcnow()
        self.last_otp_attempt_at = None
        self.otp_attempts = 0
        if self.otp_sender is not None:
            self.otp_sender.send_code(self.patient.phone_number, code)

        self._emit(
            "otp",
            "sent",
            {
                "otp_hash_stored": True,
                "provider": self.settings.verification.otp.provider,
            },
        )
        return code

    def verify_otp(self, code: str) -> bool:
        if self._otp_hash is None:
            self.result.otp_verified = False
            self._emit("otp", "failed", {"reason": "otp_not_generated"}, level="warn")
            return False

        self.last_otp_attempt_at = datetime.utcnow()
        ok = self.otp_service.verify_code(code, self._otp_hash)
        if not ok:
            self.otp_attempts += 1
        self.result.otp_verified = ok
        self._emit(
            "otp",
            "verified" if ok else "failed",
            {} if ok else {"attempts": self.otp_attempts},
        )
        return ok

    def verify_voice(self, audio_bytes: bytes) -> VerificationResult:
        verified, score = self.voice_verifier.verify(audio_bytes=audio_bytes)
        self.result.voice_verified = verified
        self.result.voice_score = score
        self._emit("voice", "verified" if verified else "failed", {"score": score})
        self.result.completed = (
            self.result.pesel_verified and self.result.otp_verified and self.result.voice_verified
        )
        return self.result

    def otp_timing_seconds(self) -> float | None:
        if self.otp_sent_at is None or self.last_otp_attempt_at is None:
            return None
        return max(0.0, (self.last_otp_attempt_at - self.otp_sent_at).total_seconds())
