from __future__ import annotations

from voiceguard.db import sqlite_connection


def store_embedding(pesel: str, embedding: list[float], db_path: str = "hospital_agent.db") -> None:
    payload = ",".join(f"{value:.10f}" for value in embedding)
    with sqlite_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO voiceprints (patient_pesel, embedding_json, model_name)
            VALUES (?, ?, ?)
            """,
            (pesel, f"[{payload}]", "ecapa-tdnn"),
        )
        connection.commit()
