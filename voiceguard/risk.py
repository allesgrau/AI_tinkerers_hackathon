from __future__ import annotations


def classify_voice_confidence(score: float, threshold: float = 0.72) -> str:
    if score > 0.8:
        return "green"
    if score >= threshold:
        return "yellow"
    return "red"
