class VoiceGuardError(Exception):
    """Base exception for voiceguard package."""


class VerificationStepError(VoiceGuardError):
    """Raised when a verification step fails."""


class ConfigurationError(VoiceGuardError):
    """Raised when package configuration is invalid."""
