from __future__ import annotations

import hashlib
import json


def compute_event_hash(prev_hash: str, event: dict) -> str:
    blob = f"{prev_hash}{json.dumps(event, sort_keys=True, separators=(',', ':'))}"
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
