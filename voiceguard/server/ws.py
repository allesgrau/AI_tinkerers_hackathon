from __future__ import annotations

from fastapi import APIRouter, WebSocket

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json({"type": "connection", "status": "ok"})
    while True:
        _ = await websocket.receive_text()
        await websocket.send_json({"type": "echo", "status": "todo"})
