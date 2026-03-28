from __future__ import annotations

from typing import Any

from app.db import get_connection


DEMO_CONVERSATIONS = [
    {
        "id": "call-001",
        "patientPesel": "90010112345",
        "patientName": "Jan Kowalski",
        "date": "2026-03-28",
        "time": "09:14",
        "duration": "4:32",
        "overallStatus": "failed",
        "actionLog": [
            {"ts": "09:14:01", "type": "lookup", "text": "PESEL 90010112345 -> DB lookup -> match: Jan Kowalski"},
            {"ts": "09:14:03", "type": "sms", "text": "SMS challenge generated and sent to the registered phone number"},
            {"ts": "09:14:12", "type": "otp_ok", "text": "OTP accepted -> secure identity checkpoint passed"},
            {"ts": "09:14:14", "type": "audio", "text": "Voice sample buffered: 4.2s, SNR 18dB, continuing speaker verification"},
            {"ts": "09:14:15", "type": "fail", "text": "Cosine similarity 0.431 < threshold 0.72"},
            {"ts": "09:14:15", "type": "fail", "text": "Anti-spoof score suggests possible synthetic or substituted speech"},
            {"ts": "09:14:16", "type": "verdict_fail", "text": "Voice mismatch detected -> escalation flag created"},
        ],
        "segments": [
            {"id": 1, "speaker": "agent", "text": "Dzien dobry, slucham. Przychodnia Medica, w czym moge pomoc?"},
            {"id": 2, "speaker": "caller", "similarity": 0.91, "status": "passed", "parts": [{"text": "Dzien dobry, chcialem umowic sie na wizyte do kardiologa.", "flagged": False}]},
            {"id": 3, "speaker": "agent", "text": "Oczywiscie. Prosze podac PESEL."},
            {"id": 4, "speaker": "caller", "similarity": 0.88, "status": "passed", "parts": [{"text": "Dziewiecdziesiat zero jeden zero jeden jeden dwa trzy cztery piec.", "flagged": False}]},
            {"id": 5, "speaker": "agent", "text": "Dziekuje. Mamy wolny termin w czwartek o 10:30 lub w piatek o 14:00. Co Pan woli?"},
            {"id": 6, "speaker": "caller", "similarity": 0.43, "status": "failed", "parts": [{"text": "Poczekaj chwile.", "flagged": True}]},
            {"id": 7, "speaker": "caller", "similarity": 0.39, "status": "failed", "parts": [{"text": "Tak, ", "flagged": False}, {"text": "czwartek bedzie dobry", "flagged": True}, {"text": ", dziekuje.", "flagged": False}]},
            {"id": 8, "speaker": "agent", "text": "Swietnie, zapisuje na czwartek 2 kwietnia, godzina 10:30. Czy potrzebuje Pan jeszcze czegos?"},
            {"id": 9, "speaker": "caller", "similarity": 0.42, "status": "failed", "parts": [{"text": "Nie, ", "flagged": False}, {"text": "to wszystko", "flagged": True}, {"text": ". Do widzenia.", "flagged": False}]},
            {"id": 10, "speaker": "agent", "text": "Do widzenia, milego dnia."},
        ],
    },
    {
        "id": "call-002",
        "patientPesel": "85060598765",
        "patientName": "Anna Wisniewska",
        "date": "2026-03-28",
        "time": "10:05",
        "duration": "2:18",
        "overallStatus": "passed",
        "actionLog": [
            {"ts": "10:05:02", "type": "lookup", "text": "PESEL 85060598765 -> DB lookup -> match: Anna Wisniewska"},
            {"ts": "10:05:04", "type": "sms", "text": "SMS challenge sent and delivery confirmed"},
            {"ts": "10:05:11", "type": "otp_ok", "text": "OTP accepted -> caller identity chain remains valid"},
            {"ts": "10:05:13", "type": "audio", "text": "Voice sample buffered: 5.1s, high-quality signal received"},
            {"ts": "10:05:14", "type": "sim_ok", "text": "Cosine similarity 0.931 >= threshold 0.72"},
            {"ts": "10:05:14", "type": "verdict_ok", "text": "Speaker verified successfully -> safe session granted"},
        ],
        "segments": [
            {"id": 1, "speaker": "agent", "text": "Przychodnia Medica, dzien dobry."},
            {"id": 2, "speaker": "caller", "similarity": 0.93, "status": "passed", "parts": [{"text": "Dzien dobry, chcialam zapytac o wyniki badan krwi.", "flagged": False}]},
            {"id": 3, "speaker": "agent", "text": "Prosze podac PESEL."},
            {"id": 4, "speaker": "caller", "similarity": 0.91, "status": "passed", "parts": [{"text": "Osiemdziesiat piec zero szesc zero piec dziewiecdziesiat osiem siedem szesc piec.", "flagged": False}]},
            {"id": 5, "speaker": "agent", "text": "Wyniki sa gotowe i dostepne w systemie pacjenta. Moze je Pani pobrac przez aplikacje."},
            {"id": 6, "speaker": "caller", "similarity": 0.89, "status": "passed", "parts": [{"text": "Dobrze, dziekuje bardzo. Do widzenia.", "flagged": False}]},
            {"id": 7, "speaker": "agent", "text": "Do widzenia."},
        ],
    },
]


def _status_from_row(row: Any) -> str:
    status = row["voice_verification_status"]
    if status in {"passed", "failed", "skipped"}:
        return status
    return "skipped"


def list_conversations() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                a.call_id,
                a.patient_pesel,
                p.full_name,
                a.created_at,
                a.voice_verification_status,
                a.voice_similarity_score
            FROM auth_sessions a
            LEFT JOIN patients p ON p.pesel = a.patient_pesel
            ORDER BY a.created_at DESC
            LIMIT 20
            """
        ).fetchall()

        if not rows:
            return DEMO_CONVERSATIONS

        conversations: list[dict[str, Any]] = []
        for row in rows:
            event_rows = connection.execute(
                """
                SELECT event_type, details, created_at, status
                FROM auth_events
                WHERE call_id = ?
                ORDER BY created_at ASC, event_id ASC
                """,
                (row["call_id"],),
            ).fetchall()

            action_log = []
            for event in event_rows:
                event_type = event["event_type"]
                mapped_type = {
                    "pesel_verified": "lookup",
                    "sms_sent": "sms",
                    "sms_verified": "otp_ok",
                    "voice_verified": "verdict_ok",
                    "voice_failed": "verdict_fail",
                    "auth_failed": "fail",
                }.get(event_type, "lookup")
                action_log.append(
                    {
                        "ts": (event["created_at"] or "")[11:19],
                        "type": mapped_type,
                        "text": event["details"] or event_type,
                    }
                )

            similarity = row["voice_similarity_score"]
            voice_status = _status_from_row(row)
            placeholder_text = {
                "passed": "Caller speech matches the enrolled voiceprint.",
                "failed": "This fragment is marked as inconsistent with the enrolled speaker profile.",
                "skipped": "No enrolled voiceprint was available for comparison.",
            }[voice_status]

            conversations.append(
                {
                    "id": row["call_id"],
                    "patientPesel": row["patient_pesel"],
                    "patientName": row["full_name"] or "Unknown caller",
                    "date": (row["created_at"] or "")[:10],
                    "time": (row["created_at"] or "")[11:16],
                    "duration": "live",
                    "overallStatus": voice_status,
                    "actionLog": action_log or [{"ts": "--:--:--", "type": "lookup", "text": "Session created. Waiting for more auth events."}],
                    "segments": [
                        {
                            "id": 1,
                            "speaker": "agent",
                            "text": "Live transcript integration is pending. This placeholder reflects backend auth state."
                        },
                        {
                            "id": 2,
                            "speaker": "caller",
                            "similarity": similarity,
                            "status": voice_status,
                            "parts": [
                                {
                                    "text": placeholder_text,
                                    "flagged": voice_status == "failed",
                                }
                            ],
                        },
                    ],
                }
            )

        return conversations


def get_conversation(call_id: str) -> dict[str, Any] | None:
    conversations = list_conversations()
    for conversation in conversations:
        if conversation["id"] == call_id:
            return conversation
    return None
