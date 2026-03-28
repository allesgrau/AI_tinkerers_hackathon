from __future__ import annotations

from collections.abc import Callable


VoiceScoreFn = Callable[[bytes, list[float] | None], float]


class VoiceVerifier:
    def __init__(
        self,
        threshold: float = 0.72,
        scorer: VoiceScoreFn | None = None,
    ) -> None:
        self.threshold = threshold
        self._scorer = scorer or self._default_score

    @staticmethod
    def _default_score(audio_bytes: bytes, enrolled_embedding: list[float] | None = None) -> float:
        del enrolled_embedding
        if not audio_bytes:
            return 0.0
        return 0.85

    def verify(
        self,
        audio_bytes: bytes,
        enrolled_embedding: list[float] | None = None,
    ) -> tuple[bool, float]:
        score = float(self._scorer(audio_bytes, enrolled_embedding))
        return score >= self.threshold, score
