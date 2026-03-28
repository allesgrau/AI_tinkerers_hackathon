from __future__ import annotations

from voiceguard.db import sqlite_connection


def lookup_patient(pesel: str, db_path: str = "hospital_agent.db") -> dict | None:
    with sqlite_connection(db_path) as connection:
        row = connection.execute(
            "SELECT pesel, full_name, phone_number FROM patients WHERE pesel = ?",
            (pesel,),
        ).fetchone()

    if row is None:
        return None

    return {
        "pesel": row["pesel"],
        "full_name": row["full_name"],
        "phone_number": row["phone_number"],
    }
