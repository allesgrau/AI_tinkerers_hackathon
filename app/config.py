from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    db_path: Path = ROOT_DIR / "hospital_agent.db"
    audio_buffer_dir: Path = ROOT_DIR / "audio_buffer"
    voice_similarity_threshold: float = float(os.getenv("VOICE_SIMILARITY_THRESHOLD", "0.72"))
    sms_provider: str = os.getenv("SMS_PROVIDER", "mock").lower()
    twilio_account_sid: str | None = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token: str | None = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_from_number: str | None = os.getenv("TWILIO_FROM_NUMBER")


settings = Settings()
