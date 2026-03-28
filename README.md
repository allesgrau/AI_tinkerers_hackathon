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

---

## Podział prac

<img width="930" height="701" alt="image" src="https://github.com/user-attachments/assets/87da427c-ea61-407b-a003-d2c3eaae6dea" />
<img width="925" height="595" alt="image" src="https://github.com/user-attachments/assets/46ea36de-5b63-44de-8ca9-74a57f6faba2" />
<img width="925" height="667" alt="image" src="https://github.com/user-attachments/assets/808f034a-768a-44a8-8256-469c38296be3" />

