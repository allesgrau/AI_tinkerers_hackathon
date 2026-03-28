from __future__ import annotations

import asyncio
import audioop
import base64
import json
import os
import sys
from contextlib import suppress
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from app.live_call_registry import LiveCallRegistry
from voiceguard.server.events import EventBus, call_update, reasoning, tool_call, tool_result, transcript


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

from agent.gemini_live_config import build_live_connect_config
from agent.tool_registry import SchedulingAgentTools


TWILIO_SAMPLE_RATE = 8000
MODEL_INPUT_SAMPLE_RATE = 16000
MODEL_OUTPUT_SAMPLE_RATE = 24000
PCM_SAMPLE_WIDTH = 2
CHANNELS = 1
DEFAULT_MODEL = os.environ.get(
    "GEMINI_LIVE_MODEL",
    "models/gemini-3.1-flash-live-preview",
)
DEFAULT_VOICE = os.environ.get("GEMINI_LIVE_VOICE", "Zephyr")


class GeminiLiveTwilioBridge:
    def __init__(
        self,
        *,
        websocket: Any,
        session_id: str,
        stream_sid: str,
        from_number: str | None,
        to_number: str | None,
        event_bus: EventBus,
        registry: LiveCallRegistry,
        model: str | None = None,
        voice_name: str | None = None,
    ) -> None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set. Add it to .env before running the Twilio bridge.")

        self.websocket = websocket
        self.session_id = session_id
        self.stream_sid = stream_sid
        self.from_number = from_number
        self.to_number = to_number
        self.event_bus = event_bus
        self.registry = registry
        self.model = model or DEFAULT_MODEL
        self.voice_name = voice_name or DEFAULT_VOICE
        self.client = genai.Client(
            api_key=api_key,
            http_options={"api_version": "v1beta"},
        )
        self.tools = SchedulingAgentTools()
        self._audio_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=256)
        self._closed = asyncio.Event()
        self._twilio_to_model_state: Any = None
        self._model_to_twilio_state: Any = None
        self._mark_index = 0
        self._last_caller_transcript = ""
        self._last_agent_transcript = ""

    async def enqueue_twilio_payload(self, payload: str) -> None:
        try:
            chunk = base64.b64decode(payload)
        except Exception:
            return

        try:
            self._audio_queue.put_nowait(chunk)
        except asyncio.QueueFull:
            with suppress(asyncio.QueueEmpty):
                self._audio_queue.get_nowait()
            self._audio_queue.put_nowait(chunk)

    async def close(self) -> None:
        self._closed.set()

    async def run(self) -> None:
        config = build_live_connect_config(
            response_modalities=["AUDIO"],
            voice_name=self.voice_name,
            input_audio_transcription=True,
            output_audio_transcription=True,
        )
        self.registry.upsert(
            self.session_id,
            call_sid=self.session_id,
            from_number=self.from_number,
            to_number=self.to_number,
            stream_sid=self.stream_sid,
            model=self.model,
            status="agent_connecting",
        )
        self.event_bus.emit_sync(
            self.session_id,
            call_update(
                "agent_connecting",
                stream_sid=self.stream_sid,
                from_number=self.from_number,
                to_number=self.to_number,
                model=self.model,
            ),
        )

        try:
            async with (
                self.client.aio.live.connect(model=self.model, config=config) as session,
                asyncio.TaskGroup() as task_group,
            ):
                self.registry.upsert(self.session_id, status="live")
                self.event_bus.emit_sync(
                    self.session_id,
                    call_update("live", stream_sid=self.stream_sid, model=self.model),
                )
                await session.send_client_content(
                    turns={
                        "role": "user",
                        "parts": [
                            {
                                "text": (
                                    "A caller has connected on a phone line. "
                                    "Greet them briefly and ask how you can help with scheduling today."
                                )
                            }
                        ],
                    },
                    turn_complete=True,
                )

                task_group.create_task(self._forward_audio_to_model(session))
                task_group.create_task(self._receive_from_model(session))
                await self._closed.wait()
                raise asyncio.CancelledError("Call ended")
        except asyncio.CancelledError:
            pass
        except errors.APIError as exc:
            self.registry.record_error(self.session_id, str(exc))
            self.event_bus.emit_sync(
                self.session_id,
                reasoning(f"Gemini Live API error: {exc}", level="error"),
            )
            self.event_bus.emit_sync(
                self.session_id,
                call_update("error", error=str(exc)),
            )
        except Exception as exc:
            self.registry.record_error(self.session_id, str(exc))
            self.event_bus.emit_sync(
                self.session_id,
                reasoning(f"Bridge failure: {exc}", level="error"),
            )
            self.event_bus.emit_sync(
                self.session_id,
                call_update("error", error=str(exc)),
            )
        finally:
            self.registry.end(self.session_id, "completed")
            self.event_bus.emit_sync(self.session_id, call_update("completed"))

    async def _forward_audio_to_model(self, session: Any) -> None:
        while not self._closed.is_set():
            chunk = await self._audio_queue.get()
            pcm_8k = audioop.ulaw2lin(chunk, PCM_SAMPLE_WIDTH)
            pcm_16k, self._twilio_to_model_state = audioop.ratecv(
                pcm_8k,
                PCM_SAMPLE_WIDTH,
                CHANNELS,
                TWILIO_SAMPLE_RATE,
                MODEL_INPUT_SAMPLE_RATE,
                self._twilio_to_model_state,
            )
            await session.send_realtime_input(
                audio={
                    "data": pcm_16k,
                    "mime_type": f"audio/pcm;rate={MODEL_INPUT_SAMPLE_RATE}",
                }
            )

    async def _receive_from_model(self, session: Any) -> None:
        async for message in session.receive():
            server_content = getattr(message, "server_content", None)
            if server_content is not None:
                await self._handle_server_content(server_content)
            if message.tool_call:
                await self._handle_tool_calls(session, message.tool_call.function_calls)

    async def _handle_server_content(self, server_content: types.LiveServerContent) -> None:
        if server_content.input_transcription and server_content.input_transcription.finished:
            text = (server_content.input_transcription.text or "").strip()
            if text and text != self._last_caller_transcript:
                self._last_caller_transcript = text
                self.registry.record_transcript(self.session_id)
                self.event_bus.emit_sync(self.session_id, transcript("caller", text))

        if server_content.output_transcription and server_content.output_transcription.finished:
            text = (server_content.output_transcription.text or "").strip()
            if text and text != self._last_agent_transcript:
                self._last_agent_transcript = text
                self.registry.record_transcript(self.session_id)
                self.event_bus.emit_sync(self.session_id, transcript("agent", text))

        if server_content.model_turn:
            for part in server_content.model_turn.parts:
                inline_data = getattr(part, "inline_data", None)
                if inline_data and inline_data.data:
                    await self._send_audio_to_twilio(inline_data.data)
                elif getattr(part, "text", None) and part.text != self._last_agent_transcript:
                    text = part.text.strip()
                    if text:
                        self._last_agent_transcript = text
                        self.registry.record_transcript(self.session_id)
                        self.event_bus.emit_sync(self.session_id, transcript("agent", text))

    async def _handle_tool_calls(
        self,
        session: Any,
        function_calls: list[types.FunctionCall],
    ) -> None:
        responses = []

        for function_call in function_calls:
            arguments = self._normalize_arguments(function_call.args)
            self.registry.record_tool(self.session_id, function_call.name)
            self.event_bus.emit_sync(
                self.session_id,
                tool_call(function_call.name, arguments),
            )

            result = self.tools.call_tool(function_call.name, arguments)
            success = bool(
                result.get("success")
                if "success" in result
                else result.get("ok", False)
            )
            self.event_bus.emit_sync(
                self.session_id,
                tool_result(function_call.name, result=result, success=success),
            )
            responses.append(
                types.FunctionResponse(
                    id=function_call.id,
                    name=function_call.name,
                    response=result,
                )
            )

        await session.send_tool_response(function_responses=responses)

    async def _send_audio_to_twilio(self, pcm_24k: bytes) -> None:
        pcm_8k, self._model_to_twilio_state = audioop.ratecv(
            pcm_24k,
            PCM_SAMPLE_WIDTH,
            CHANNELS,
            MODEL_OUTPUT_SAMPLE_RATE,
            TWILIO_SAMPLE_RATE,
            self._model_to_twilio_state,
        )
        mulaw_bytes = audioop.lin2ulaw(pcm_8k, PCM_SAMPLE_WIDTH)
        payload = base64.b64encode(mulaw_bytes).decode("ascii")
        await self.websocket.send_json(
            {
                "event": "media",
                "streamSid": self.stream_sid,
                "media": {"payload": payload},
            }
        )
        self._mark_index += 1
        await self.websocket.send_json(
            {
                "event": "mark",
                "streamSid": self.stream_sid,
                "mark": {"name": f"agent-{self._mark_index}"},
            }
        )

    @staticmethod
    def _normalize_arguments(arguments: Any) -> dict[str, Any]:
        if arguments is None:
            return {}
        if isinstance(arguments, str):
            try:
                parsed = json.loads(arguments)
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                return {}
        if isinstance(arguments, dict):
            return dict(arguments)
        try:
            return dict(arguments)
        except (TypeError, ValueError):
            return {}
