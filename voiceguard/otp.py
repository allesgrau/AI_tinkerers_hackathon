from __future__ import annotations

import hashlib
import random


def generate_otp(length: int = 6) -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(length))


def hash_otp(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def verify_otp(code: str, otp_hash: str) -> bool:
    return hash_otp(code) == otp_hash
