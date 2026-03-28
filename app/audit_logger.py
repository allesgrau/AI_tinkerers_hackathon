"""
Audit Logger for Person 4 - Auth Events
Logs all authentication events to database (no mocks)
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from app.db import get_connection, utc_now_iso


logger = logging.getLogger(__name__)


class AuditLogger:
    """Log authentication events for compliance & debugging"""

    EVENT_TYPES = {
        "pesel_lookup": "PESEL verification attempt",
        "pesel_verified": "PESEL verified successfully",
        "pesel_failed": "PESEL verification failed",
        "sms_sent": "SMS OTP sent",
        "sms_verified": "SMS OTP verified",
        "sms_failed": "SMS OTP verification failed",
        "voice_enrolled": "Voice biometrics enrolled",
        "voice_verified": "Voice biometrics verified",
        "voice_failed": "Voice biometrics verification failed",
        "session_created": "User authenticated session created",
        "session_revoked": "User session revoked",
        "auth_failed": "Authentication failure",
    }

    @staticmethod
    def log(
        event_type: str,
        call_id: str,
        patient_pesel: Optional[str] = None,
        status: str = "success",
        details: str = "",
        ip_address: str = "127.0.0.1",
    ) -> None:
        """
        Log authentication event to database
        
        Args:
            event_type: Type of event (from EVENT_TYPES keys)
            call_id: Voice call ID for tracking
            patient_pesel: Patient PESEL if known
            status: 'success', 'failure', or 'warning'
            details: Additional details
            ip_address: Caller IP (for security)
        """
        if event_type not in AuditLogger.EVENT_TYPES:
            logger.warning(f"Unknown event type: {event_type}")
            return

        try:
            with get_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO auth_events (
                        patient_pesel, event_type, status, details, 
                        call_id, ip_address, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        patient_pesel,
                        event_type,
                        status,
                        details,
                        call_id,
                        ip_address,
                        utc_now_iso(),
                    ),
                )
                connection.commit()

            log_msg = (
                f"[{event_type}] {AuditLogger.EVENT_TYPES[event_type]} "
                f"(call_id={call_id}, pesel={patient_pesel or 'unknown'}, status={status})"
            )
            if status == "failure":
                logger.warning(log_msg)
            else:
                logger.info(log_msg)

        except Exception as e:
            logger.error(f"Failed to log auth event {event_type}: {e}")

    @staticmethod
    def log_pesel_lookup(call_id: str, pesel: str, found: bool) -> None:
        AuditLogger.log(
            event_type="pesel_verified" if found else "pesel_failed",
            call_id=call_id,
            patient_pesel=pesel if found else None,
            status="success" if found else "failure",
            details=f"PESEL lookup for {pesel}",
        )

    @staticmethod
    def log_sms_sent(call_id: str, patient_pesel: str, phone_number: str) -> None:
        AuditLogger.log(
            event_type="sms_sent",
            call_id=call_id,
            patient_pesel=patient_pesel,
            status="success",
            details=f"SMS sent to {phone_number}",
        )

    @staticmethod
    def log_sms_verification(
        call_id: str, patient_pesel: str, success: bool, reason: str = ""
    ) -> None:
        AuditLogger.log(
            event_type="sms_verified" if success else "sms_failed",
            call_id=call_id,
            patient_pesel=patient_pesel,
            status="success" if success else "failure",
            details=reason,
        )

    @staticmethod
    def log_voice_verification(
        call_id: str,
        patient_pesel: str,
        success: bool,
        similarity_score: Optional[float] = None,
        reason: str = "",
    ) -> None:
        AuditLogger.log(
            event_type="voice_verified" if success else "voice_failed",
            call_id=call_id,
            patient_pesel=patient_pesel,
            status="success" if success else "failure",
            details=f"Similarity: {similarity_score or 'N/A'} - {reason}",
        )

    @staticmethod
    def log_session_created(call_id: str, patient_pesel: str) -> None:
        AuditLogger.log(
            event_type="session_created",
            call_id=call_id,
            patient_pesel=patient_pesel,
            status="success",
            details="Authenticated session created",
        )

    @staticmethod
    def log_auth_failure(
        call_id: str, patient_pesel: Optional[str], reason: str
    ) -> None:
        AuditLogger.log(
            event_type="auth_failed",
            call_id=call_id,
            patient_pesel=patient_pesel,
            status="failure",
            details=reason,
        )
