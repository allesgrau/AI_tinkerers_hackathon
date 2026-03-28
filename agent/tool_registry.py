from __future__ import annotations

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
                "description": "Verify a patient before revealing or booking appointments.",
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
                "description": "List available appointment slots by doctor name or specialty.",
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
                "description": "Confirm a specific available slot for a verified patient.",
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

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if tool_name == "verify_patient_identity":
            return self.service.verify_patient(
                pesel=arguments["pesel"],
                verification_zip=arguments["verification_zip"],
                full_name=arguments.get("full_name"),
            )

        if tool_name == "find_doctor_availability":
            return self.service.find_availability(
                specialty=arguments.get("specialty"),
                doctor_name=arguments.get("doctor_name"),
                limit=arguments.get("limit", 5),
            )

        if tool_name == "book_appointment":
            return self.service.book_appointment(
                patient_pesel=arguments["patient_pesel"],
                doctor_name=arguments["doctor_name"],
                appointment_datetime=arguments["appointment_datetime"],
            )

        return {"success": False, "reason": f"Unknown tool: {tool_name}"}
