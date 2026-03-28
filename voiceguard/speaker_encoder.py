"""Speaker embedding extraction using SpeechBrain ECAPA-TDNN."""

from __future__ import annotations

import io
import logging
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

_model: Any = None


def _get_model() -> Any:
    global _model
    if _model is not None:
        return _model
    try:
        from speechbrain.inference.speaker import EncoderClassifier
        _model = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir=str(Path.home() / ".cache" / "speechbrain" / "spkrec-ecapa-voxceleb"),
        )
        logger.info("SpeechBrain ECAPA-TDNN model loaded")
        return _model
    except Exception as exc:
        logger.warning("SpeechBrain not available (%s) — using mock embeddings", exc)
        return None


def extract_embedding(audio_bytes: bytes) -> list[float]:
    """Extract a 192-dim speaker embedding from raw audio bytes (WAV/WebM/OGG)."""
    model = _get_model()
    if model is None:
        # Mock: return a deterministic-ish 192-dim vector based on audio content
        rng = np.random.RandomState(abs(hash(audio_bytes[:100])) % (2**31))
        emb = rng.randn(192).astype(np.float64)
        emb = emb / np.linalg.norm(emb)
        return emb.tolist()

    import torchaudio

    # Write audio to temp file (SpeechBrain needs a file path or tensor)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp_path = f.name
        # Try to convert to WAV if needed
        try:
            import subprocess
            # Use ffmpeg to convert any format to 16kHz mono WAV
            result = subprocess.run(
                ["ffmpeg", "-i", "pipe:0", "-ar", "16000", "-ac", "1", "-f", "wav", "pipe:1"],
                input=audio_bytes,
                capture_output=True,
                timeout=10,
            )
            if result.returncode == 0:
                f.write(result.stdout)
            else:
                f.write(audio_bytes)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            f.write(audio_bytes)

    try:
        waveform, sample_rate = torchaudio.load(tmp_path)
        if sample_rate != 16000:
            waveform = torchaudio.functional.resample(waveform, sample_rate, 16000)
        embedding = model.encode_batch(waveform)
        emb = embedding.squeeze().cpu().numpy()
        emb = emb / np.linalg.norm(emb)
        return emb.tolist()
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two embedding vectors."""
    a_arr = np.array(a)
    b_arr = np.array(b)
    dot = np.dot(a_arr, b_arr)
    norm = np.linalg.norm(a_arr) * np.linalg.norm(b_arr)
    if norm == 0:
        return 0.0
    return float(dot / norm)
