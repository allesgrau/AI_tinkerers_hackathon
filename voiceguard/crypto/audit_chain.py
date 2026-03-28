from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from voiceguard.db import sqlite_connection


GENESIS_HASH = "0" * 64


@dataclass(frozen=True)
class AuditEventRecord:
    sequence_no: int
    session_id: str
    event_type: str
    event_hash: str
    prev_hash: str
    created_at: str


@dataclass(frozen=True)
class ChainVerificationReport:
    valid: bool
    checked_events: int
    broken_at_sequence: int | None = None
    expected_prev_hash: str | None = None
    found_prev_hash: str | None = None
    expected_event_hash: str | None = None
    found_event_hash: str | None = None


def _canonical_json(event: dict[str, Any]) -> str:
    return json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _ensure_audit_schema(db_path: str) -> None:
    with sqlite_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_chain_events (
                audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                sequence_no INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                event_json TEXT NOT NULL,
                prev_hash TEXT NOT NULL,
                event_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(session_id, sequence_no)
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_audit_chain_session
            ON audit_chain_events (session_id, sequence_no)
            """
        )
        connection.commit()


def compute_event_hash(prev_hash: str, event: dict[str, Any]) -> str:
    blob = f"{prev_hash}{_canonical_json(event)}"
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def append_event(
    session_id: str,
    event_type: str,
    event_payload: dict[str, Any],
    db_path: str = "hospital_agent.db",
) -> AuditEventRecord:
    _ensure_audit_schema(db_path)
    created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    event = {
        "session_id": session_id,
        "event_type": event_type,
        "payload": event_payload,
        "created_at": created_at,
    }

    with sqlite_connection(db_path) as connection:
        last_row = connection.execute(
            """
            SELECT sequence_no, event_hash
            FROM audit_chain_events
            WHERE session_id = ?
            ORDER BY sequence_no DESC
            LIMIT 1
            """,
            (session_id,),
        ).fetchone()

        if last_row is None:
            sequence_no = 1
            prev_hash = GENESIS_HASH
        else:
            sequence_no = int(last_row["sequence_no"]) + 1
            prev_hash = str(last_row["event_hash"])

        event_hash = compute_event_hash(prev_hash, event)
        connection.execute(
            """
            INSERT INTO audit_chain_events (
                session_id,
                sequence_no,
                event_type,
                event_json,
                prev_hash,
                event_hash,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                sequence_no,
                event_type,
                _canonical_json(event),
                prev_hash,
                event_hash,
                created_at,
            ),
        )
        connection.commit()

    return AuditEventRecord(
        sequence_no=sequence_no,
        session_id=session_id,
        event_type=event_type,
        event_hash=event_hash,
        prev_hash=prev_hash,
        created_at=created_at,
    )


def verify_chain(session_id: str, db_path: str = "hospital_agent.db") -> ChainVerificationReport:
    _ensure_audit_schema(db_path)
    with sqlite_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT sequence_no, event_json, prev_hash, event_hash
            FROM audit_chain_events
            WHERE session_id = ?
            ORDER BY sequence_no ASC
            """,
            (session_id,),
        ).fetchall()

    if not rows:
        return ChainVerificationReport(valid=True, checked_events=0)

    expected_prev_hash = GENESIS_HASH
    for row in rows:
        sequence_no = int(row["sequence_no"])
        found_prev_hash = str(row["prev_hash"])
        found_event_hash = str(row["event_hash"])
        event_json = json.loads(str(row["event_json"]))

        if found_prev_hash != expected_prev_hash:
            return ChainVerificationReport(
                valid=False,
                checked_events=sequence_no - 1,
                broken_at_sequence=sequence_no,
                expected_prev_hash=expected_prev_hash,
                found_prev_hash=found_prev_hash,
            )

        expected_event_hash = compute_event_hash(expected_prev_hash, event_json)
        if found_event_hash != expected_event_hash:
            return ChainVerificationReport(
                valid=False,
                checked_events=sequence_no - 1,
                broken_at_sequence=sequence_no,
                expected_event_hash=expected_event_hash,
                found_event_hash=found_event_hash,
            )

        expected_prev_hash = found_event_hash

    return ChainVerificationReport(valid=True, checked_events=len(rows))
