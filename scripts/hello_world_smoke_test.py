from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from scripts.setup_database import main as setup_database


ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "hospital_agent.db"


def _get_sms_code(call_id: str) -> str:
    with sqlite3.connect(DB_PATH) as connection:
        row = connection.execute(
            "SELECT sms_code FROM auth_sessions WHERE call_id = ?",
            (call_id,),
        ).fetchone()
    if row is None or row[0] is None:
        raise RuntimeError("SMS code was not created")
    return str(row[0])


def run_smoke_test() -> None:
    setup_database()

    call_id = "hello-world-call"
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json().get("ok") is True

        collect = client.post(
            "/vapi/tools/collect-pesel",
            json={"call_id": call_id, "pesel": "02211312345"},
        )
        assert collect.status_code == 200
        assert collect.json().get("ok") is True

        send_sms = client.post(
            "/vapi/tools/send-sms",
            json={"call_id": call_id},
        )
        assert send_sms.status_code == 200
        assert send_sms.json().get("ok") is True

        sms_code = _get_sms_code(call_id)
        verify = client.post(
            "/vapi/tools/verify-sms",
            json={"call_id": call_id, "code": sms_code},
        )
        assert verify.status_code == 200
        assert verify.json().get("ok") is True

        status = client.post(
            "/vapi/tools/auth-status",
            json={"call_id": call_id},
        )
        assert status.status_code == 200
        status_json = status.json()
        assert status_json.get("ok") is True
        assert status_json.get("sms_verified") is True

    print("HELLO WORLD SMOKE TEST PASSED")


if __name__ == "__main__":
    run_smoke_test()
