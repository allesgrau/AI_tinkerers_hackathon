from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from voiceguard.exceptions import ConfigurationError


class VerificationSecuritySettings(BaseModel):
    max_attempts: int = 3
    audit: str = "hash_chain"


class VerificationVoiceSettings(BaseModel):
    model: str = "ecapa-tdnn"
    threshold: float = 0.72
    min_audio_seconds: int = 3


class VerificationOtpSettings(BaseModel):
    provider: str = "mock"
    expiry_seconds: int = 300
    length: int = 6


class VerificationSettings(BaseModel):
    steps: list[str] = Field(default_factory=lambda: ["pesel", "otp", "voice"])
    voice: VerificationVoiceSettings = Field(default_factory=VerificationVoiceSettings)
    otp: VerificationOtpSettings = Field(default_factory=VerificationOtpSettings)
    security: VerificationSecuritySettings = Field(default_factory=VerificationSecuritySettings)


class DatabaseSettings(BaseModel):
    path: str = "hospital_agent.db"


class UISettings(BaseModel):
    theme: str = "dark"
    show_reasoning: bool = True


class VoiceGuardSettings(BaseModel):
    verification: VerificationSettings = Field(default_factory=VerificationSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    ui: UISettings = Field(default_factory=UISettings)


def load_settings(path: str | Path = "voiceguard.yml") -> VoiceGuardSettings:
    config_path = Path(path)
    if not config_path.exists():
        return VoiceGuardSettings()

    try:
        import yaml
    except ImportError as exc:
        raise ConfigurationError(
            "PyYAML is required to load voiceguard.yml. Install project dependencies first."
        ) from exc

    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return VoiceGuardSettings.model_validate(data)
