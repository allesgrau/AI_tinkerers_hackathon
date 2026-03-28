# AI_tinkerers_hackathon

SQLite database setup for a Gemini Live scheduling agent.

## What is included

- `patients` table with PESEL stored as `TEXT` to preserve leading zeroes
- `doctors` table for specialty lookup
- `appointments` table with pre-generated slots and booking state
- SQLite constraints for PESEL format, status validation, and slot uniqueness
- Seed data for a few patients, doctors, and appointment slots

## Project structure

- `database/schema.sql` defines the SQLite schema
- `database/client.py` contains the shared SQLite connection helper
- `database/seed_data.py` contains starter data
- `agent/scheduling_service.py` contains database-backed booking logic
- `agent/tool_registry.py` exposes agent-callable tools
- `agent/gemini_live_blueprint.py` outputs a Gemini Live session config blueprint
- `agent/gemini_live_config.py` builds SDK-native Gemini Live config objects
- `scripts/setup_database.py` creates and seeds `hospital_agent.db`
- `scripts/demo_scheduling_agent.py` runs a local end-to-end tool flow
- `scripts/run_voice_scheduler.py` runs a voice-only Gemini Live scheduler with the database tools

## Usage

Run:

```bash
python3 scripts/setup_database.py
```

This creates `hospital_agent.db` in the repository root.

## Agent flow

The intended live-agent flow is:

1. Verify the patient using PESEL and the registered ZIP code.
2. Query available slots by doctor name or specialty.
3. Ask the patient to confirm one exact slot.
4. Call the booking tool to update the database.

The tool layer supports this directly:

- `verify_patient_identity`
- `find_doctor_availability`
- `book_appointment`

To inspect the Gemini session blueprint:

```bash
python3 agent/gemini_live_blueprint.py
```

To build the SDK-native config in your own code:

```python
from google import genai

from agent.gemini_live_config import build_live_connect_config

client = genai.Client(api_key="YOUR_GEMINI_API_KEY")
config = build_live_connect_config()
```

For a voice-only terminal client with mic input, speaker output, and database tools:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/run_voice_scheduler.py
```

The script loads `.env` automatically. At minimum, set:

```env
GEMINI_API_KEY=your_key_here
GEMINI_LIVE_MODEL=models/gemini-3.1-flash-live-preview
```

Type `q` in the terminal to stop the session.

To run a local booking demo:

```bash
python3 scripts/demo_scheduling_agent.py
```

## Notes about dependencies

The database layer uses Python's built-in `sqlite3` module.
If you want to connect this to Gemini Live, install the SDK listed in `requirements.txt`.
