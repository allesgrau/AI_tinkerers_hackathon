from __future__ import annotations

import logging
from collections.abc import Callable

from voiceguard.speaker_encoder import cosine_similarity, extract_embedding

logger = logging.getLogger(__name__)

VoiceScoreFn = Callable[[bytes, list[float] | None], float]


def _real_score(audio_bytes: bytes, enrolled_embedding: list[float] | None = None) -> float:
    """Extract embedding from audio and compare against enrolled embedding."""
    if not audio_bytes:
        return 0.0
    if enrolled_embedding is None:
        logger.warning("No enrolled embedding — cannot verify voice")
        return 0.0

    live_embedding = extract_embedding(audio_bytes)
    score = cosine_similarity(live_embedding, enrolled_embedding)
    logger.info("Voice similarity score: %.4f", score)
    return score


class VoiceVerifier:
    def __init__(
        self,
        threshold: float = 0.72,
        scorer: VoiceScoreFn | None = None,
    ) -> None:
        self.threshold = threshold
        self._scorer = scorer or _real_score

    def verify(
        self,
        audio_bytes: bytes,
        enrolled_embedding: list[float] | None = None,
    ) -> tuple[bool, float]:
        score = float(self._scorer(audio_bytes, enrolled_embedding))
        return score >= self.threshold, score
