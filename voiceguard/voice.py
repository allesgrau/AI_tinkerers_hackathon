from __future__ import annotations


class VoiceVerifier:
    def __init__(self, threshold: float = 0.72) -> None:
        self.threshold = threshold

    def verify(self, audio_bytes: bytes, enrolled_embedding: list[float] | None = None) -> tuple[bool, float]:
        # Placeholder for SpeechBrain pipeline integration.
        del audio_bytes
        del enrolled_embedding
        score = 0.0
        return score >= self.threshold, score
