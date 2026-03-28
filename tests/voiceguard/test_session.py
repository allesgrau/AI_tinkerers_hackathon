from voiceguard.session import VerificationSession


def test_session_initializes() -> None:
    session = VerificationSession(pesel="02211312345")
    assert session.pesel == "02211312345"
