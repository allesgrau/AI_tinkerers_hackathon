from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agent.tool_registry import SchedulingAgentTools


def main() -> None:
    tools = SchedulingAgentTools()

    verified_patient = tools.call_tool(
        "verify_patient_identity",
        {
            "pesel": "02211312345",
            "verification_zip": "10001",
            "full_name": "John Smith",
        },
    )
    cardiology_slots = tools.call_tool(
        "find_doctor_availability",
        {"specialty": "Cardiologist", "limit": 3},
    )
    booking_result = tools.call_tool(
        "book_appointment",
        {
            "patient_pesel": "02211312345",
            "doctor_name": "Dr. Emily Carter",
            "appointment_datetime": "2026-03-29 10:00",
        },
    )

    print("verify_patient_identity")
    print(json.dumps(verified_patient, indent=2))
    print("\nfind_doctor_availability")
    print(json.dumps(cardiology_slots, indent=2))
    print("\nbook_appointment")
    print(json.dumps(booking_result, indent=2))


if __name__ == "__main__":
    main()
