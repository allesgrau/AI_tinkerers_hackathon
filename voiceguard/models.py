from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


VerificationStepName = Literal["pesel", "otp", "voice"]
VerificationStatus = Literal["pending", "in_progress", "sent", "verified", "failed"]
VerificationLevel = Literal["info", "warn", "error"]


class PatientRecord(BaseModel):
    pesel: str
    full_name: str
    phone_number: str
    verification_zip: str | None = None
    enrolled_voice_sample: str | None = None


class StepStatus(BaseModel):
    step: VerificationStepName
    status: VerificationStatus = "pending"
    details: dict[str, Any] = Field(default_factory=dict)


class VerificationEvent(BaseModel):
    ts: datetime = Field(default_factory=datetime.utcnow)
    step: str
    status: str
    details: dict[str, Any] = Field(default_factory=dict)
    level: VerificationLevel = "info"


class VerificationResult(BaseModel):
    session_id: str
    pesel_verified: bool = False
    otp_verified: bool = False
    voice_verified: bool = False
    voice_score: float | None = None
    completed: bool = False


class SessionSnapshot(BaseModel):
    session_id: str
    pesel: str
    steps: list[StepStatus]
    result: VerificationResult


class RiskSnapshot(BaseModel):
    voice_confidence: str | None = None
    otp_timing: str | None = None
    attempt_history: str | None = None
    overall_risk: str = "low"
    indicators: dict[str, Any] = Field(default_factory=dict)
