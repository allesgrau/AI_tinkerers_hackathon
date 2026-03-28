from __future__ import annotations

from fastapi import FastAPI

from voiceguard.server.ws import router as ws_router

app = FastAPI(title="VoiceGuard Server", version="0.1.0")
app.include_router(ws_router)


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "voiceguard"}
