from __future__ import annotations

import sqlite3
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "hospital_agent.db"


def create_connection(db_path: Path | None = None) -> sqlite3.Connection:
    database_path = db_path or DB_PATH
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection
