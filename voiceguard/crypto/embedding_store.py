from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime

from voiceguard.db import sqlite_connection


@dataclass(frozen=True)
class StoredEmbedding:
    patient_pesel: str
    embedding: list[float]
    model_name: str
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


def store_embedding(
    pesel: str,
    embedding: list[float],
    db_path: str = "hospital_agent.db",
    model_name: str = "ecapa-tdnn",
) -> StoredEmbedding:
    payload = _serialize_embedding(embedding)
    created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    with sqlite_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO voiceprints (patient_pesel, embedding_json, model_name)
            VALUES (?, ?, ?)
            """,
            (pesel, payload, model_name),
        )
        connection.commit()

    return StoredEmbedding(
        patient_pesel=pesel,
        embedding=_deserialize_embedding(payload),
        model_name=model_name,
        created_at=created_at,
    )


def get_latest_embedding(
    pesel: str,
    db_path: str = "hospital_agent.db",
) -> StoredEmbedding | None:
    with sqlite_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT patient_pesel, embedding_json, model_name, created_at
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
        model_name=str(row["model_name"] or "ecapa-tdnn"),
        created_at=str(row["created_at"]),
    )


def delete_embeddings_for_pesel(pesel: str, db_path: str = "hospital_agent.db") -> int:
    with sqlite_connection(db_path) as connection:
        cursor = connection.execute(
            "DELETE FROM voiceprints WHERE patient_pesel = ?",
            (pesel,),
        )
        connection.commit()
        return int(cursor.rowcount or 0)
