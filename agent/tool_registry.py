from __future__ import annotations

import json
from typing import Any

from agent.scheduling_service import SchedulingService


class SchedulingAgentTools:
    """Thin tool wrapper designed for a realtime model session."""

    def __init__(self, service: SchedulingService | None = None) -> None:
        self.service = service or SchedulingService()

    @staticmethod
    def tool_definitions() -> list[dict[str, Any]]:
        return [
            {
                "name": "verify_patient_identity",
                "description": "Verify a patient before revealing or booking appointments. Always provide pesel and verification_zip.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pesel": {"type": "string"},
                        "verification_zip": {"type": "string"},
                        "full_name": {"type": "string"},
                    },
                    "required": ["pesel", "verification_zip"],
                },
            },
            {
                "name": "find_doctor_availability",
                "description": "List available appointment slots by exact doctor_name or by specialty.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "specialty": {"type": "string"},
                        "doctor_name": {"type": "string"},
                        "limit": {"type": "integer", "default": 5},
                    },
                },
            },
            {
                "name": "book_appointment",
                "description": "Confirm a specific available slot for a verified patient using patient_pesel, doctor_name, and appointment_datetime.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "patient_pesel": {"type": "string"},
                        "doctor_name": {"type": "string"},
                        "appointment_datetime": {"type": "string"},
                    },
                    "required": ["patient_pesel", "doctor_name", "appointment_datetime"],
                },
            },
        ]

    @staticmethod
    def _normalize_arguments(arguments: Any) -> dict[str, Any]:
        if arguments is None:
            return {}

        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                return {}

        if not isinstance(arguments, dict):
            try:
                arguments = dict(arguments)
            except (TypeError, ValueError):
                return {}

        normalized = dict(arguments)
        aliases = {
            "verificationZip": "verification_zip",
            "zip_code": "verification_zip",
            "zipCode": "verification_zip",
            "fullName": "full_name",
            "doctorName": "doctor_name",
            "patientPesel": "patient_pesel",
            "appointmentDatetime": "appointment_datetime",
        }
        for source_key, target_key in aliases.items():
            if source_key in normalized and target_key not in normalized:
                normalized[target_key] = normalized[source_key]

        return normalized

    @staticmethod
    def _missing_argument_response(tool_name: str, field_name: str) -> dict[str, Any]:
        return {
            "success": False,
            "reason": f"Missing required argument '{field_name}' for tool '{tool_name}'.",
        }

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        normalized = self._normalize_arguments(arguments)

        if tool_name == "verify_patient_identity":
            if "pesel" not in normalized:
                return self._missing_argument_response(tool_name, "pesel")
            if "verification_zip" not in normalized:
                return self._missing_argument_response(tool_name, "verification_zip")
            return self.service.verify_patient(
                pesel=normalized["pesel"],
                verification_zip=normalized["verification_zip"],
                full_name=normalized.get("full_name"),
            )

        if tool_name == "find_doctor_availability":
            return self.service.find_availability(
                specialty=normalized.get("specialty"),
                doctor_name=normalized.get("doctor_name"),
                limit=normalized.get("limit", 5),
            )

        if tool_name == "book_appointment":
            if "patient_pesel" not in normalized:
                return self._missing_argument_response(tool_name, "patient_pesel")
            if "doctor_name" not in normalized:
                return self._missing_argument_response(tool_name, "doctor_name")
            if "appointment_datetime" not in normalized:
                return self._missing_argument_response(tool_name, "appointment_datetime")
            return self.service.book_appointment(
                patient_pesel=normalized["patient_pesel"],
                doctor_name=normalized["doctor_name"],
                appointment_datetime=normalized["appointment_datetime"],
            )

        return {"success": False, "reason": f"Unknown tool: {tool_name}"}
