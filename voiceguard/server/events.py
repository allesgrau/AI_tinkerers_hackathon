from __future__ import annotations

from collections import defaultdict
from typing import Callable


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[dict], None]]] = defaultdict(list)

    def subscribe(self, channel: str, callback: Callable[[dict], None]) -> None:
        self._subscribers[channel].append(callback)

    def publish(self, channel: str, event: dict) -> None:
        for callback in self._subscribers[channel]:
            callback(event)
