from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Protocol

from voiceguard.models import PatientRecord


@contextmanager
def sqlite_connection(db_path: str | Path = "hospital_agent.db") -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


class PatientRepository(Protocol):
    def get_by_pesel(self, pesel: str) -> PatientRecord | None:
        """Return the patient record for a PESEL, or None if missing."""


class SQLitePatientRepository:
    def __init__(self, db_path: str | Path = "hospital_agent.db") -> None:
        self.db_path = Path(db_path)

    def get_by_pesel(self, pesel: str) -> PatientRecord | None:
        with sqlite_connection(self.db_path) as connection:
            patient_columns = {
                row["name"] for row in connection.execute("PRAGMA table_info(patients)").fetchall()
            }
            voice_column = (
                ", enrolled_voice_sample" if "enrolled_voice_sample" in patient_columns else ""
            )
            row = connection.execute(
                f"""
                SELECT pesel, full_name, phone_number, verification_zip{voice_column}
                FROM patients
                WHERE pesel = ?
                """,
                (pesel,),
            ).fetchone()

        if row is None:
            return None

        payload = {
            "pesel": row["pesel"],
            "full_name": row["full_name"],
            "phone_number": row["phone_number"],
            "verification_zip": row["verification_zip"],
            "enrolled_voice_sample": row["enrolled_voice_sample"]
            if "enrolled_voice_sample" in row.keys()
            else None,
        }
        return PatientRecord.model_validate(payload)
