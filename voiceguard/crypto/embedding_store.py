from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime

from voiceguard.db import sqlite_connection


@dataclass(frozen=True)
class StoredEmbedding:
    patient_pesel: str
    embedding: list[float]
    voiceprint_hash: str
    model_name: str
    speaker_id: str | None
    created_at: str


def _serialize_embedding(embedding: list[float]) -> str:
    return json.dumps([round(float(value), 10) for value in embedding], separators=(",", ":"))


def _deserialize_embedding(payload: str) -> list[float]:
    values = json.loads(payload)
    return [float(value) for value in values]


def wipe_audio_buffer(buffer: bytearray) -> None:
    for index in range(len(buffer)):
        buffer[index] = 0


def wipe_embedding_buffer(embedding: list[float]) -> None:
    for index in range(len(embedding)):
        embedding[index] = 0.0


def compute_voiceprint_hash(embedding: list[float]) -> str:
    payload = _serialize_embedding(embedding)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def store_embedding(
    pesel: str,
    embedding: list[float],
    db_path: str = "hospital_agent.db",
    model_name: str = "ecapa-tdnn",
    speaker_id: str | None = None,
) -> StoredEmbedding:
    payload = _serialize_embedding(embedding)
    voiceprint_hash = compute_voiceprint_hash(embedding)
    created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    with sqlite_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO voiceprints (
                patient_pesel,
                voiceprint_hash,
                embedding_json,
                speaker_id,
                model_name,
                last_updated
            )
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (pesel, voiceprint_hash, payload, speaker_id, model_name),
        )
        connection.commit()

    return StoredEmbedding(
        patient_pesel=pesel,
        embedding=_deserialize_embedding(payload),
        voiceprint_hash=voiceprint_hash,
        model_name=model_name,
        speaker_id=speaker_id,
        created_at=created_at,
    )


def enroll_embedding(
    pesel: str,
    embedding: list[float],
    db_path: str = "hospital_agent.db",
    model_name: str = "ecapa-tdnn",
    speaker_id: str | None = None,
) -> StoredEmbedding:
    """Enrollment API for Stage 2 pipeline (stores only derived embedding)."""
    return store_embedding(
        pesel=pesel,
        embedding=embedding,
        db_path=db_path,
        model_name=model_name,
        speaker_id=speaker_id,
    )


def get_latest_embedding(
    pesel: str,
    db_path: str = "hospital_agent.db",
) -> StoredEmbedding | None:
    with sqlite_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT patient_pesel, voiceprint_hash, embedding_json, speaker_id, model_name, created_at
            FROM voiceprints
            WHERE patient_pesel = ?
            ORDER BY created_at DESC, voiceprint_id DESC
            LIMIT 1
            """,
            (pesel,),
        ).fetchone()

    if row is None:
        return None

    return StoredEmbedding(
        patient_pesel=str(row["patient_pesel"]),
        embedding=_deserialize_embedding(str(row["embedding_json"])),
        voiceprint_hash=str(row["voiceprint_hash"] or ""),
        model_name=str(row["model_name"] or "ecapa-tdnn"),
        speaker_id=(str(row["speaker_id"]) if row["speaker_id"] is not None else None),
        created_at=str(row["created_at"]),
    )


def get_latest_embedding_vector(pesel: str, db_path: str = "hospital_agent.db") -> list[float] | None:
    record = get_latest_embedding(pesel=pesel, db_path=db_path)
    if record is None:
        return None
    return list(record.embedding)


def delete_embeddings_for_pesel(pesel: str, db_path: str = "hospital_agent.db") -> int:
    with sqlite_connection(db_path) as connection:
        cursor = connection.execute(
            "DELETE FROM voiceprints WHERE patient_pesel = ?",
            (pesel,),
        )
        connection.commit()
        return int(cursor.rowcount or 0)
