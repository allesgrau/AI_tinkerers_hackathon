from __future__ import annotations

from voiceguard.models import RiskSnapshot


def classify_voice_confidence(score: float, threshold: float = 0.72) -> str:
    if score > 0.8:
        return "green"
    if score >= threshold:
        return "yellow"
    return "red"


def classify_otp_timing(seconds: float | None) -> str | None:
    if seconds is None:
        return None
    if seconds < 2:
        return "suspicious"
    if seconds > 300:
        return "expired"
    return "normal"


def classify_attempt_history(attempts: int) -> str:
    if attempts > 2:
        return "high"
    if attempts > 1:
        return "medium"
    return "low"


def overall_risk_level(
    *,
    voice_confidence: str | None,
    otp_timing: str | None,
    attempt_history: str | None,
) -> str:
    if voice_confidence == "red" or otp_timing == "suspicious" or attempt_history == "high":
        return "high"
    if voice_confidence == "yellow" or otp_timing == "expired" or attempt_history == "medium":
        return "medium"
    return "low"


def assess_risk(
    *,
    voice_score: float | None = None,
    voice_threshold: float = 0.72,
    otp_timing_seconds: float | None = None,
    failed_attempts: int = 0,
    extra_indicators: dict | None = None,
) -> RiskSnapshot:
    voice_confidence = (
        classify_voice_confidence(voice_score, voice_threshold)
        if voice_score is not None
        else None
    )
    otp_timing = classify_otp_timing(otp_timing_seconds)
    attempt_history = classify_attempt_history(failed_attempts)
    overall = overall_risk_level(
        voice_confidence=voice_confidence,
        otp_timing=otp_timing,
        attempt_history=attempt_history,
    )

    indicators = dict(extra_indicators or {})
    if voice_score is not None:
        indicators["voice_score"] = voice_score
    if voice_confidence is not None:
        indicators["voice_confidence"] = voice_confidence
    if otp_timing is not None:
        indicators["otp_timing"] = otp_timing
    indicators["attempt_history"] = attempt_history
    indicators["overall_risk"] = overall

    return RiskSnapshot(
        voice_confidence=voice_confidence,
        otp_timing=otp_timing,
        attempt_history=attempt_history,
        overall_risk=overall,
        indicators=indicators,
    )
