from __future__ import annotations

from voiceguard.db import PatientRepository, SQLitePatientRepository
from voiceguard.models import PatientRecord


def normalize_pesel(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def is_valid_pesel_format(value: str) -> bool:
    normalized = normalize_pesel(value)
    return len(normalized) == 11 and normalized.isdigit()


def lookup_patient(
    pesel: str,
    db_path: str = "hospital_agent.db",
    patient_repository: PatientRepository | None = None,
) -> PatientRecord | None:
    repository = patient_repository or SQLitePatientRepository(db_path)
    return repository.get_by_pesel(normalize_pesel(pesel))
