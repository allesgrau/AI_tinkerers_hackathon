from voiceguard.db import PatientRepository
from voiceguard.models import PatientRecord
from voiceguard.session import VerificationSession


def test_session_initializes() -> None:
    session = VerificationSession(pesel="02211312345")
    assert session.pesel == "02211312345"


class InMemoryPatientRepository(PatientRepository):
    def get_by_pesel(self, pesel: str) -> PatientRecord | None:
        if pesel != "02211312345":
            return None
        return PatientRecord(
            pesel=pesel,
            full_name="John Smith",
            phone_number="+12025550101",
            verification_zip="10001",
        )


def test_session_happy_path() -> None:
    session = VerificationSession(
        pesel="02211312345",
        patient_repository=InMemoryPatientRepository(),
    )

    assert session.verify_pesel() is True
    code = session.send_otp()
    assert session.verify_otp(code) is True

    result = session.verify_voice(b"fake-audio")
    assert result.completed is True
    assert result.voice_verified is True
    assert result.voice_score is not None
