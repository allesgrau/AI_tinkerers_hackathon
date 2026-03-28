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
- `database/seed_data.py` contains starter data
- `scripts/setup_database.py` creates and seeds `hospital_agent.db`

## Usage

Run:

```bash
python3 scripts/setup_database.py
```

This creates `hospital_agent.db` in the repository root.

## Notes about dependencies

This setup uses Python's built-in `sqlite3` module, so there are no external package dependencies to install in this environment.
