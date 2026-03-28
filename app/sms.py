from __future__ import annotations

import logging

from app.config import settings


logger = logging.getLogger(__name__)


class SmsService:
    def __init__(self) -> None:
        self._client = None
        if settings.sms_provider == "twilio":
            self._init_twilio()

    def _init_twilio(self) -> None:
        missing = [
            name
            for name, value in {
                "TWILIO_ACCOUNT_SID": settings.twilio_account_sid,
                "TWILIO_AUTH_TOKEN": settings.twilio_auth_token,
                "TWILIO_FROM_NUMBER": settings.twilio_from_number,
            }.items()
            if not value
        ]
        if missing:
            logger.warning(
                "Missing Twilio config (%s). Falling back to mock SMS provider.",
                ", ".join(missing),
            )
            return

        from twilio.rest import Client

        self._client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

    def send_code(self, phone_number: str, code: str) -> str:
        message = f"Kod weryfikacyjny: {code}. Podaj go agentowi podczas rozmowy."

        if settings.sms_provider == "twilio" and self._client is not None:
            result = self._client.messages.create(
                body=message,
                from_=settings.twilio_from_number,
                to=phone_number,
            )
            return f"Twilio SID: {result.sid}"

        logger.info("MOCK SMS to %s: %s", phone_number, message)
        return "mock-sms-sent"
