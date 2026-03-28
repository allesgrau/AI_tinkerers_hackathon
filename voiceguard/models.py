from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class StepStatus(BaseModel):
    step: Literal["pesel", "otp", "voice"]
    status: Literal["pending", "in_progress", "verified", "failed"] = "pending"
    details: dict[str, Any] = Field(default_factory=dict)


class VerificationEvent(BaseModel):
    ts: datetime = Field(default_factory=datetime.utcnow)
    step: str
    status: str
    details: dict[str, Any] = Field(default_factory=dict)
    level: Literal["info", "warn", "error"] = "info"


class VerificationResult(BaseModel):
    session_id: str
    pesel_verified: bool = False
    otp_verified: bool = False
    voice_verified: bool = False
    voice_score: float | None = None
    completed: bool = False
