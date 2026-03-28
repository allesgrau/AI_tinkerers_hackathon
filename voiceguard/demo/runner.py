"""Demo runner: plays pre-scripted scenarios through the EventBus with realistic timing."""

from __future__ import annotations

import asyncio
import importlib
import logging
from typing import Any

from voiceguard.server.events import Event, event_bus

logger = logging.getLogger(__name__)

SCENARIOS = {
    "happy_path": "voiceguard.demo.scenarios.happy_path",
    "wrong_voice": "voiceguard.demo.scenarios.wrong_voice",
    "brute_force": "voiceguard.demo.scenarios.brute_force",
    "replay_attack": "voiceguard.demo.scenarios.replay_attack",
}

# Default demo session IDs (so the UI can subscribe)
DEMO_SESSION_PREFIX = "demo"


def load_scenario(name: str) -> list[dict[str, Any]]:
    """Import and return the scenario event list."""
    module_path = SCENARIOS.get(name)
    if module_path is None:
        raise ValueError(f"Unknown scenario: {name}. Available: {list(SCENARIOS.keys())}")
    mod = importlib.import_module(module_path)
    return mod.scenario


async def play_scenario(name: str, session_id: str | None = None) -> None:
    """Play a scenario, emitting events with realistic delays."""
    events = load_scenario(name)
    sid = session_id or f"{DEMO_SESSION_PREFIX}-{name}"

    logger.info("Playing demo scenario '%s' (session: %s, %d events)", name, sid, len(events))

    # Emit a start marker
    await event_bus.emit(sid, Event("demo.start", {"scenario": name, "session_id": sid}))

    for entry in events:
        delay = entry.get("delay", 0.5)
        await asyncio.sleep(delay)

        # Build event from scenario entry (strip 'delay' key)
        event_type = entry["type"]
        data = {k: v for k, v in entry.items() if k not in ("type", "delay")}
        await event_bus.emit(sid, Event(event_type, data))

    # Emit an end marker
    await event_bus.emit(sid, Event("demo.end", {"scenario": name}))
    logger.info("Demo scenario '%s' complete", name)


async def play_all_scenarios(delay_between: float = 3.0) -> None:
    """Play all scenarios sequentially with a pause between each."""
    for name in ["happy_path", "wrong_voice", "brute_force"]:
        await play_scenario(name)
        await asyncio.sleep(delay_between)


def run_demo(scenario_name: str = "happy_path") -> list[dict]:
    """Synchronous entry point for running a demo scenario."""
    events = load_scenario(scenario_name)
    return events
