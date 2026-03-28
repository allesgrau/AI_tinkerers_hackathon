from __future__ import annotations

import sqlite3
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database.seed_data import APPOINTMENT_SLOTS, DOCTORS, PATIENTS

DB_PATH = ROOT_DIR / "hospital_agent.db"
SCHEMA_PATH = ROOT_DIR / "database" / "schema.sql"


def create_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def apply_schema(connection: sqlite3.Connection) -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    connection.executescript(schema)


def ensure_schema_compatibility(connection: sqlite3.Connection) -> None:
    # Lightweight migration for databases created before voice-auth fields existed.
    patient_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(patients)").fetchall()
    }
    if "enrolled_voice_sample" not in patient_columns:
        connection.execute(
            "ALTER TABLE patients ADD COLUMN enrolled_voice_sample TEXT"
        )


def seed_patients(connection: sqlite3.Connection) -> None:
    connection.executemany(
        """
        INSERT INTO patients (
            pesel,
            full_name,
            phone_number,
            enrolled_voice_sample,
            verification_zip
        )
        VALUES (
            :pesel,
            :full_name,
            :phone_number,
            :enrolled_voice_sample,
            :verification_zip
        )
        ON CONFLICT(pesel) DO UPDATE SET
            full_name = excluded.full_name,
            phone_number = excluded.phone_number,
            enrolled_voice_sample = excluded.enrolled_voice_sample,
            verification_zip = excluded.verification_zip
        """,
        PATIENTS,
    )


def seed_doctors(connection: sqlite3.Connection) -> None:
    connection.executemany(
        """
        INSERT INTO doctors (full_name, specialty)
        VALUES (:full_name, :specialty)
        ON CONFLICT(full_name) DO UPDATE SET specialty = excluded.specialty
        """,
        DOCTORS,
    )


def lookup_doctor_ids(connection: sqlite3.Connection) -> dict[str, int]:
    rows = connection.execute("SELECT doctor_id, full_name FROM doctors").fetchall()
    return {row["full_name"]: row["doctor_id"] for row in rows}


def seed_appointments(connection: sqlite3.Connection) -> None:
    doctor_ids = lookup_doctor_ids(connection)
    appointment_rows = []
    for slot in APPOINTMENT_SLOTS:
        appointment_rows.append(
            {
                "doctor_id": doctor_ids[slot["doctor_full_name"]],
                "patient_pesel": slot["patient_pesel"],
                "appointment_datetime": slot["appointment_datetime"],
                "status": slot["status"],
            }
        )

    connection.executemany(
        """
        INSERT INTO appointments (doctor_id, patient_pesel, appointment_datetime, status)
        VALUES (:doctor_id, :patient_pesel, :appointment_datetime, :status)
        ON CONFLICT(doctor_id, appointment_datetime) DO UPDATE SET
            patient_pesel = excluded.patient_pesel,
            status = excluded.status
        """,
        appointment_rows,
    )


def print_summary(connection: sqlite3.Connection) -> None:
    patients_count = connection.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    doctors_count = connection.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
    appointments_count = connection.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    available_count = connection.execute(
        "SELECT COUNT(*) FROM appointments WHERE status = 'Available'"
    ).fetchone()[0]

    print(f"Database ready at: {DB_PATH}")
    print(f"Patients: {patients_count}")
    print(f"Doctors: {doctors_count}")
    print(f"Appointments: {appointments_count}")
    print(f"Available slots: {available_count}")


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with create_connection() as connection:
        apply_schema(connection)
        ensure_schema_compatibility(connection)
        seed_patients(connection)
        seed_doctors(connection)
        seed_appointments(connection)
        connection.commit()
        print_summary(connection)


if __name__ == "__main__":
    main()
