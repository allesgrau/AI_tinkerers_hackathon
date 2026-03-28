from __future__ import annotations

import json
import logging
from pathlib import Path

from app.config import settings
from app.db import get_connection


logger = logging.getLogger(__name__)
MODEL_NAME = "speechbrain/spkrec-ecapa-voxceleb"


class VoiceVerifier:
    def __init__(self) -> None:
        self._classifier = None
        self._np = None
        self._torch = None
        self._torchaudio = None

    def _load_numpy(self) -> bool:
        if self._np is not None:
            return True
        try:
            import numpy as np  # type: ignore[import-not-found]
        except Exception:
            logger.warning("Numpy not available. Voice verification will be skipped.")
            return False
        self._np = np
        return True

    def _load_ml_dependencies(self) -> bool:
        if self._torch is not None and self._torchaudio is not None:
            return True
        try:
            import torch  # type: ignore[import-not-found]
            import torchaudio  # type: ignore[import-not-found]
        except Exception:
            logger.warning("Torch/Torchaudio not available. Voice verification will be skipped.")
            return False
        self._torch = torch
        self._torchaudio = torchaudio
        return True

    def _get_classifier(self):
        if not self._load_ml_dependencies():
            return None
        if self._classifier is None:
            from speechbrain.inference.speaker import EncoderClassifier  # type: ignore[import-not-found]

            self._classifier = EncoderClassifier.from_hparams(source=MODEL_NAME)
        return self._classifier

    def _load_audio(self, audio_path: Path):
        if not self._load_ml_dependencies():
            raise RuntimeError("Audio dependencies are unavailable")
        waveform, sample_rate = self._torchaudio.load(str(audio_path))
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        if sample_rate != 16000:
            waveform = self._torchaudio.functional.resample(waveform, sample_rate, 16000)
        return waveform

    def _compute_embedding(self, audio_path: Path) -> list[float]:
        if not self._load_numpy():
            raise RuntimeError("Numpy unavailable")
        classifier = self._get_classifier()
        if classifier is None:
            raise RuntimeError("SpeechBrain classifier unavailable")
        waveform = self._load_audio(audio_path)
        with self._torch.inference_mode():
            embedding = classifier.encode_batch(waveform).squeeze().cpu().numpy()
        return embedding.astype(self._np.float32).tolist()

    def _cosine_similarity(self, first: list[float], second: list[float]) -> float:
        if not self._load_numpy():
            raise RuntimeError("Numpy unavailable")
        a = self._np.array(first, dtype=self._np.float32)
        b = self._np.array(second, dtype=self._np.float32)
        score = float(self._np.dot(a, b) / (self._np.linalg.norm(a) * self._np.linalg.norm(b) + 1e-8))
        return score

    def _read_cached_embedding(self, patient_pesel: str) -> list[float] | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT embedding_json
                FROM voiceprints
                WHERE patient_pesel = ?
                ORDER BY created_at DESC, voiceprint_id DESC
                LIMIT 1
                """,
                (patient_pesel,),
            ).fetchone()
        if row is None:
            return None
        return json.loads(row["embedding_json"])

    def _store_embedding(self, patient_pesel: str, embedding: list[float]) -> None:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO voiceprints (patient_pesel, embedding_json, model_name)
                VALUES (?, ?, ?)
                """,
                (patient_pesel, json.dumps(embedding), MODEL_NAME),
            )
            connection.commit()

    def verify(self, patient_pesel: str, call_audio_path: Path, enrolled_audio_path: Path | None) -> tuple[str, float | None]:
        if not call_audio_path.exists():
            return "failed", None

        try:
            call_embedding = self._compute_embedding(call_audio_path)
        except Exception:
            logger.exception("Unable to compute call embedding for %s", call_audio_path)
            return "failed", None

        enrolled_embedding = self._read_cached_embedding(patient_pesel)
        if enrolled_embedding is None:
            if enrolled_audio_path is None or not enrolled_audio_path.exists():
                return "skipped", None
            try:
                enrolled_embedding = self._compute_embedding(enrolled_audio_path)
                self._store_embedding(patient_pesel, enrolled_embedding)
            except Exception:
                logger.exception("Unable to compute enrolled embedding for %s", enrolled_audio_path)
                return "failed", None

        similarity = self._cosine_similarity(call_embedding, enrolled_embedding)
        status = "passed" if similarity >= settings.voice_similarity_threshold else "failed"
        return status, similarity
