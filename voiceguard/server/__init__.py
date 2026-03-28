"""VoiceGuard server — FastAPI + WebSocket for real-time verification UI."""

from voiceguard.server.app import app
from voiceguard.server.events import event_bus

__all__ = ["app", "event_bus"]
