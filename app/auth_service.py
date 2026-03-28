from __future__ import annotations

import base64
import random
from pathlib import Path

from app.config import settings
from app.db import get_connection, utc_now_iso
from app.sms import SmsService
from app.voice_verifier import VoiceVerifier


class AuthService:
    def __init__(self) -> None:
        settings.audio_buffer_dir.mkdir(parents=True, exist_ok=True)
        self.sms_service = SmsService()
        self.voice_verifier = VoiceVerifier()

    def _ensure_session(self, call_id: str) -> None:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO auth_sessions (call_id, created_at, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(call_id) DO UPDATE SET
                    updated_at = excluded.updated_at
                """,
                (call_id, utc_now_iso(), utc_now_iso()),
            )
            connection.commit()

    def _session_audio_path(self, call_id: str, extension: str = "wav") -> Path:
        safe_call_id = "".join(ch for ch in call_id if ch.isalnum() or ch in ("-", "_"))
        return settings.audio_buffer_dir / f"{safe_call_id}.{extension}"

    def attach_pesel(self, call_id: str, pesel: str) -> dict:
        self._ensure_session(call_id)
        pesel = "".join(ch for ch in pesel if ch.isdigit())

        with get_connection() as connection:
            patient = connection.execute(
                """
                SELECT pesel, full_name, phone_number, enrolled_voice_sample
                FROM patients
                WHERE pesel = ?
                """,
                (pesel,),
            ).fetchone()

            if patient is None:
                return {"ok": False, "message": "Nie znaleziono pacjenta o podanym PESEL."}

            connection.execute(
                """
                UPDATE auth_sessions
                SET patient_pesel = ?, updated_at = ?
                WHERE call_id = ?
                """,
                (pesel, utc_now_iso(), call_id),
            )
            connection.commit()

        return {
            "ok": True,
            "message": f"PESEL zweryfikowany dla: {patient['full_name']}.",
            "patient": {
                "pesel": patient["pesel"],
                "full_name": patient["full_name"],
                "phone_number": patient["phone_number"],
            },
        }

    def send_sms(self, call_id: str) -> dict:
        self._ensure_session(call_id)

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT p.phone_number, a.patient_pesel
                FROM auth_sessions a
                LEFT JOIN patients p ON p.pesel = a.patient_pesel
                WHERE a.call_id = ?
                """,
                (call_id,),
            ).fetchone()

            if row is None or row["patient_pesel"] is None:
                return {"ok": False, "message": "Najpierw podaj poprawny PESEL."}

            code = f"{random.randint(100000, 999999)}"
            provider_result = self.sms_service.send_code(row["phone_number"], code)

            connection.execute(
                """
                UPDATE auth_sessions
                SET sms_code = ?, sms_sent_at = ?, sms_verified = 0, updated_at = ?
                WHERE call_id = ?
                """,
                (code, utc_now_iso(), utc_now_iso(), call_id),
            )
            connection.commit()

        return {
            "ok": True,
            "message": "Kod SMS został wysłany. Poproś użytkownika o odczytanie kodu.",
            "provider_result": provider_result,
        }

    def verify_sms(self, call_id: str, code: str) -> dict:
        self._ensure_session(call_id)
        clean_code = "".join(ch for ch in code if ch.isdigit())

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT sms_code
                FROM auth_sessions
                WHERE call_id = ?
                """,
                (call_id,),
            ).fetchone()

            if row is None or row["sms_code"] is None:
                return {"ok": False, "message": "Kod SMS nie został jeszcze wygenerowany."}

            if row["sms_code"] != clean_code:
                return {"ok": False, "message": "Kod SMS jest niepoprawny."}

            connection.execute(
                """
                UPDATE auth_sessions
                SET sms_verified = 1, updated_at = ?
                WHERE call_id = ?
                """,
                (utc_now_iso(), call_id),
            )
            connection.commit()

        return {"ok": True, "message": "Kod SMS poprawny."}

    def ingest_audio(self, call_id: str, audio_base64: str, extension: str = "wav") -> dict:
        self._ensure_session(call_id)
        audio_bytes = base64.b64decode(audio_base64)
        target_path = self._session_audio_path(call_id, extension=extension)
        target_path.write_bytes(audio_bytes)

        return {
            "ok": True,
            "message": "Audio zapisane.",
            "audio_path": str(target_path),
            "size_bytes": len(audio_bytes),
        }

    def verify_voice_in_background(self, call_id: str) -> dict:
        self._ensure_session(call_id)

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT a.patient_pesel, p.enrolled_voice_sample
                FROM auth_sessions a
                LEFT JOIN patients p ON p.pesel = a.patient_pesel
                WHERE a.call_id = ?
                """,
                (call_id,),
            ).fetchone()

            if row is None or row["patient_pesel"] is None:
                return {"ok": False, "message": "Brak PESEL w sesji autoryzacji."}

            connection.execute(
                """
                UPDATE auth_sessions
                SET voice_verification_status = 'pending', updated_at = ?
                WHERE call_id = ?
                """,
                (utc_now_iso(), call_id),
            )
            connection.commit()

        call_audio = self._session_audio_path(call_id)
        enrolled_path = Path(row["enrolled_voice_sample"]) if row["enrolled_voice_sample"] else None
        status, similarity = self.voice_verifier.verify(
            patient_pesel=row["patient_pesel"],
            call_audio_path=call_audio,
            enrolled_audio_path=enrolled_path,
        )

        with get_connection() as connection:
            connection.execute(
                """
                UPDATE auth_sessions
                SET voice_verification_status = ?, voice_similarity_score = ?, updated_at = ?
                WHERE call_id = ?
                """,
                (status, similarity, utc_now_iso(), call_id),
            )
            connection.commit()

        return {
            "ok": True,
            "message": "Weryfikacja głosu zakończona.",
            "voice_verification_status": status,
            "voice_similarity_score": similarity,
            "threshold": settings.voice_similarity_threshold,
        }

    def get_status(self, call_id: str) -> dict:
        self._ensure_session(call_id)

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    a.call_id,
                    a.patient_pesel,
                    a.sms_sent_at,
                    a.sms_verified,
                    a.voice_verification_status,
                    a.voice_similarity_score,
                    p.full_name
                FROM auth_sessions a
                LEFT JOIN patients p ON p.pesel = a.patient_pesel
                WHERE a.call_id = ?
                """,
                (call_id,),
            ).fetchone()

        if row is None:
            return {"ok": False, "message": "Sesja nie istnieje."}

        return {
            "ok": True,
            "call_id": row["call_id"],
            "patient_pesel": row["patient_pesel"],
            "patient_name": row["full_name"],
            "sms_sent_at": row["sms_sent_at"],
            "sms_verified": bool(row["sms_verified"]),
            "voice_verification_status": row["voice_verification_status"],
            "voice_similarity_score": row["voice_similarity_score"],
            "fully_authenticated": bool(row["sms_verified"]) and row["voice_verification_status"] == "passed",
        }
