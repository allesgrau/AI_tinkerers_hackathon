from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from voiceguard.db import sqlite_connection


@dataclass(frozen=True)
class TokenClaims:
    session_id: str
    pesel: str
    pesel_verified: bool
    otp_verified: bool
    voice_verified: bool
    voice_score: float
    jti: str
    iat: int
    exp: int


def _utc_timestamp() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def _ensure_nonce_schema(db_path: str) -> None:
    with sqlite_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS jwt_nonces (
                jti TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                issued_at INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                consumed_at INTEGER
            )
            """
        )
        connection.commit()


def _store_nonce(
    *,
    jti: str,
    session_id: str,
    issued_at: int,
    expires_at: int,
    db_path: str,
) -> None:
    _ensure_nonce_schema(db_path)
    with sqlite_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO jwt_nonces (jti, session_id, issued_at, expires_at)
            VALUES (?, ?, ?, ?)
            """,
            (jti, session_id, issued_at, expires_at),
        )
        connection.commit()


def _consume_nonce(jti: str, db_path: str) -> bool:
    _ensure_nonce_schema(db_path)
    now_ts = _utc_timestamp()
    with sqlite_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT consumed_at, expires_at
            FROM jwt_nonces
            WHERE jti = ?
            """,
            (jti,),
        ).fetchone()

        if row is None:
            return False
        if row["consumed_at"] is not None:
            return False
        if now_ts > int(row["expires_at"]):
            return False

        connection.execute(
            "UPDATE jwt_nonces SET consumed_at = ? WHERE jti = ?",
            (now_ts, jti),
        )
        connection.commit()
    return True


def revoke_nonce(jti: str, db_path: str = "hospital_agent.db") -> bool:
    """Manual token revocation helper (e.g. on forced session revoke)."""
    _ensure_nonce_schema(db_path)
    now_ts = _utc_timestamp()
    with sqlite_connection(db_path) as connection:
        cursor = connection.execute(
            """
            UPDATE jwt_nonces
            SET consumed_at = ?
            WHERE jti = ? AND consumed_at IS NULL
            """,
            (now_ts, jti),
        )
        connection.commit()
        return int(cursor.rowcount or 0) > 0


def issue_token(
    *,
    secret: str,
    session_id: str,
    pesel: str,
    pesel_verified: bool,
    otp_verified: bool,
    voice_verified: bool,
    voice_score: float,
    expiry_seconds: int = 900,
    db_path: str = "hospital_agent.db",
    additional_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    iat = int(now.timestamp())
    exp = int((now + timedelta(seconds=expiry_seconds)).timestamp())
    jti = str(uuid.uuid4())

    payload = {
        "session_id": session_id,
        "pesel": pesel,
        "pesel_verified": bool(pesel_verified),
        "otp_verified": bool(otp_verified),
        "voice_verified": bool(voice_verified),
        "voice_score": float(voice_score),
        "jti": jti,
        "iat": iat,
        "exp": exp,
    }
    if additional_claims:
        payload.update(additional_claims)

    token = jwt.encode(payload, secret, algorithm="HS256")
    _store_nonce(jti=jti, session_id=session_id, issued_at=iat, expires_at=exp, db_path=db_path)
    return token


def issue_session_token(
    *,
    secret: str,
    session_id: str,
    pesel: str,
    pesel_verified: bool,
    otp_verified: bool,
    voice_verified: bool,
    voice_score: float,
    expiry_seconds: int = 900,
    db_path: str = "hospital_agent.db",
    session_status: str = "completed",
    risk_level: str | None = None,
) -> str:
    """Stage 2 convenience wrapper matching session.complete semantics."""
    extra: dict[str, Any] = {"session_status": session_status}
    if risk_level is not None:
        extra["risk_level"] = risk_level

    return issue_token(
        secret=secret,
        session_id=session_id,
        pesel=pesel,
        pesel_verified=pesel_verified,
        otp_verified=otp_verified,
        voice_verified=voice_verified,
        voice_score=voice_score,
        expiry_seconds=expiry_seconds,
        db_path=db_path,
        additional_claims=extra,
    )


def decode_token(token: str, secret: str) -> dict[str, Any]:
    return jwt.decode(token, secret, algorithms=["HS256"])


def verify_token(
    token: str,
    secret: str,
    *,
    db_path: str = "hospital_agent.db",
    consume_nonce: bool = True,
) -> TokenClaims:
    decoded = decode_token(token, secret)

    required = [
        "session_id",
        "pesel",
        "pesel_verified",
        "otp_verified",
        "voice_verified",
        "voice_score",
        "jti",
        "iat",
        "exp",
    ]
    missing = [name for name in required if name not in decoded]
    if missing:
        raise jwt.InvalidTokenError(f"Missing claims: {', '.join(missing)}")

    if consume_nonce:
        ok = _consume_nonce(str(decoded["jti"]), db_path=db_path)
        if not ok:
            raise jwt.InvalidTokenError("Token replay detected or nonce is invalid")

    return TokenClaims(
        session_id=str(decoded["session_id"]),
        pesel=str(decoded["pesel"]),
        pesel_verified=bool(decoded["pesel_verified"]),
        otp_verified=bool(decoded["otp_verified"]),
        voice_verified=bool(decoded["voice_verified"]),
        voice_score=float(decoded["voice_score"]),
        jti=str(decoded["jti"]),
        iat=int(decoded["iat"]),
        exp=int(decoded["exp"]),
    )


def verify_session_complete_token(
    token: str,
    secret: str,
    *,
    db_path: str = "hospital_agent.db",
    consume_nonce: bool = True,
) -> TokenClaims:
    claims = verify_token(
        token,
        secret,
        db_path=db_path,
        consume_nonce=consume_nonce,
    )
    if not (claims.pesel_verified and claims.otp_verified and claims.voice_verified):
        raise jwt.InvalidTokenError("Session token does not represent full verification")
    return claims
