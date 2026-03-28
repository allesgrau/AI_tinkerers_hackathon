from __future__ import annotations

from typing import Protocol


class OtpSender(Protocol):
    def send_code(self, phone_number: str, code: str) -> None:
        """Send the OTP code through an external provider."""
