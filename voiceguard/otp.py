from __future__ import annotations

import hashlib
import random
import secrets


def generate_otp(length: int = 6) -> str:
    if length <= 0:
        raise ValueError("OTP length must be positive")
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def hash_otp(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def verify_otp(code: str, otp_hash: str) -> bool:
    return hash_otp(code) == otp_hash


class OtpService:
    def __init__(self, length: int = 6) -> None:
        self.length = length

    def issue_code(self) -> str:
        return generate_otp(self.length)

    def store_hash(self, code: str) -> str:
        return hash_otp(code)

    def verify_code(self, code: str, otp_hash: str) -> bool:
        return verify_otp(code, otp_hash)
