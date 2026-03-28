from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

from google.genai import types


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agent.gemini_live_blueprint import SYSTEM_INSTRUCTION
from agent.tool_registry import SchedulingAgentTools


def build_sdk_tools() -> list[types.Tool]:
    declarations = []
    for definition in SchedulingAgentTools.tool_definitions():
        declarations.append(
            types.FunctionDeclaration(
                name=definition["name"],
                description=definition["description"],
                parametersJsonSchema=definition["parameters"],
            )
        )
    return [types.Tool(function_declarations=declarations)]


def build_live_connect_config(
    response_modalities: Sequence[str] | None = None,
    voice_name: str | None = None,
) -> types.LiveConnectConfig:
    modalities = list(response_modalities or ["TEXT"])
    speech_config = None
    if voice_name:
        speech_config = types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
            )
        )

    return types.LiveConnectConfig(
        response_modalities=modalities,
        system_instruction=SYSTEM_INSTRUCTION,
        tools=build_sdk_tools(),
        speech_config=speech_config,
    )
