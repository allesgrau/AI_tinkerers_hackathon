from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agent.tool_registry import SchedulingAgentTools


SYSTEM_INSTRUCTION = """
You are a medical scheduling voice agent.
Your job is to help patients find and confirm appointments with doctors.

Rules:
- Verify the patient's identity before sharing or booking patient-specific details.
- Use find_doctor_availability to look up open slots by specialty or doctor name.
- Only use book_appointment after the patient clearly confirms the exact slot.
- Never claim a booking is confirmed until the tool returns success=true.
- If no slots are available, offer the closest alternatives returned by the tool.
- Use the exact argument names defined by each tool schema.
- Keep doctor and patient names in English when speaking with the caller.
""".strip()


def build_session_config() -> dict[str, object]:
    return {
        "system_instruction": SYSTEM_INSTRUCTION,
        "tools": SchedulingAgentTools.tool_definitions(),
    }


if __name__ == "__main__":
    print(json.dumps(build_session_config(), indent=2))
