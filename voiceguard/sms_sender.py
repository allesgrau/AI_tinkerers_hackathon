"""Twilio SMS OTP sender implementing the OtpSender protocol."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


class TwilioSmsSender:
    """Sends OTP codes via Twilio SMS."""

    def __init__(self) -> None:
        self._client = None
        self._from_number = os.environ.get("TWILIO_FROM_NUMBER", "")
        sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
        token = os.environ.get("TWILIO_AUTH_TOKEN", "")
        if sid and token and self._from_number:
            try:
                from twilio.rest import Client
                self._client = Client(sid, token)
                logger.info("Twilio SMS sender initialized (from: %s)", self._from_number)
            except ImportError:
                logger.warning("twilio package not installed — SMS will be logged only")
        else:
            logger.warning("Twilio credentials missing — SMS will be logged only")

    def send_code(self, phone_number: str, code: str) -> None:
        message = f"Kod weryfikacyjny: {code}"
        if self._client is not None:
            result = self._client.messages.create(
                body=message,
                from_=self._from_number,
                to=phone_number,
            )
            logger.info("SMS sent to %s (SID: %s)", phone_number, result.sid)
        else:
            logger.info("MOCK SMS to %s: %s", phone_number, message)
