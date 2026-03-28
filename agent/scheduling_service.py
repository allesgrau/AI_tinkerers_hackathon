from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from database.client import create_connection


@dataclass(slots=True)
class DoctorAvailability:
    doctor_id: int
    doctor_name: str
    specialty: str
    appointment_datetime: str
    status: str


class SchedulingService:
    def verify_patient(
        self,
        pesel: str,
        verification_zip: str,
        full_name: str | None = None,
    ) -> dict[str, Any]:
        with create_connection() as connection:
            row = connection.execute(
                """
                SELECT pesel, full_name, phone_number, verification_zip
                FROM patients
                WHERE pesel = ?
                """,
                (pesel,),
            ).fetchone()

        if row is None:
            return {"verified": False, "reason": "Patient not found."}

        if row["verification_zip"] != verification_zip:
            return {"verified": False, "reason": "ZIP code does not match our records."}

        if full_name and row["full_name"].casefold() != full_name.casefold():
            return {"verified": False, "reason": "Full name does not match our records."}

        return {
            "verified": True,
            "patient": {
                "pesel": row["pesel"],
                "full_name": row["full_name"],
                "phone_number": row["phone_number"],
                "verification_zip": row["verification_zip"],
            },
        }

    def find_availability(
        self,
        specialty: str | None = None,
        doctor_name: str | None = None,
        limit: int = 5,
    ) -> dict[str, Any]:
        filters = ["a.status = 'Available'"]
        params: list[Any] = []

        if specialty:
            filters.append("d.specialty = ?")
            params.append(specialty)

        if doctor_name:
            filters.append("d.full_name = ?")
            params.append(doctor_name)

        params.append(limit)
        where_clause = " AND ".join(filters)

        with create_connection() as connection:
            rows = connection.execute(
                f"""
                SELECT
                    d.doctor_id,
                    d.full_name AS doctor_name,
                    d.specialty,
                    a.appointment_datetime,
                    a.status
                FROM appointments a
                JOIN doctors d ON d.doctor_id = a.doctor_id
                WHERE {where_clause}
                ORDER BY a.appointment_datetime ASC
                LIMIT ?
                """,
                params,
            ).fetchall()

        matches = [asdict(DoctorAvailability(**row)) for row in rows]
        return {"matches": matches, "count": len(matches)}

    def book_appointment(
        self,
        patient_pesel: str,
        doctor_name: str,
        appointment_datetime: str,
    ) -> dict[str, Any]:
        with create_connection() as connection:
            patient = connection.execute(
                "SELECT pesel, full_name FROM patients WHERE pesel = ?",
                (patient_pesel,),
            ).fetchone()
            if patient is None:
                return {"success": False, "reason": "Patient not found."}

            doctor = connection.execute(
                "SELECT doctor_id, full_name, specialty FROM doctors WHERE full_name = ?",
                (doctor_name,),
            ).fetchone()
            if doctor is None:
                return {"success": False, "reason": "Doctor not found."}

            appointment = connection.execute(
                """
                SELECT appointment_id, status, patient_pesel
                FROM appointments
                WHERE doctor_id = ? AND appointment_datetime = ?
                """,
                (doctor["doctor_id"], appointment_datetime),
            ).fetchone()

            if appointment is None:
                return {"success": False, "reason": "Appointment slot not found."}

            if appointment["status"] != "Available":
                return {"success": False, "reason": "Appointment slot is no longer available."}

            cursor = connection.execute(
                """
                UPDATE appointments
                SET patient_pesel = ?, status = 'Booked'
                WHERE appointment_id = ? AND status = 'Available'
                """,
                (patient_pesel, appointment["appointment_id"]),
            )
            if cursor.rowcount != 1:
                connection.rollback()
                return {"success": False, "reason": "Appointment slot was taken during confirmation."}
            connection.commit()

        return {
            "success": True,
            "appointment": {
                "doctor_name": doctor["full_name"],
                "specialty": doctor["specialty"],
                "appointment_datetime": appointment_datetime,
                "patient_pesel": patient_pesel,
                "patient_name": patient["full_name"],
                "status": "Booked",
            },
        }
