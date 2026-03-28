from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt


def issue_token(claims: dict[str, Any], secret: str, expiry_seconds: int = 900) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        **claims,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expiry_seconds)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_token(token: str, secret: str) -> dict[str, Any]:
    return jwt.decode(token, secret, algorithms=["HS256"])
