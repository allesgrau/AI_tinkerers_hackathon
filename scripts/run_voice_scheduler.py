from __future__ import annotations

import argparse
import asyncio
import os
import sys
import traceback
from pathlib import Path

import pyaudio
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from google.genai import types


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

from agent.gemini_live_config import build_live_connect_config
from agent.tool_registry import SchedulingAgentTools


FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024
DEFAULT_MODEL = os.environ.get(
    "GEMINI_LIVE_MODEL",
    "models/gemini-2.5-flash-native-audio-preview-12-2025",
)
DEFAULT_VOICE = "Zephyr"


class VoiceScheduler:
    def __init__(self, model: str, voice_name: str) -> None:
        self.model = model
        self.voice_name = voice_name
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set. Add it to .env or export it in your shell.")
        self.client = genai.Client(
            api_key=api_key,
            http_options={"api_version": "v1beta"},
        )
        self.pya = pyaudio.PyAudio()
        self.tools = SchedulingAgentTools()

        self.session = None
        self.audio_in_queue: asyncio.Queue[bytes] | None = None
        self.audio_out_queue: asyncio.Queue[dict[str, bytes | str]] | None = None
        self.input_stream = None
        self.output_stream = None

    async def send_text(self) -> None:
        while True:
            text = await asyncio.to_thread(input, "message > ")
            if text.lower() == "q":
                raise asyncio.CancelledError("User requested exit")
            if self.session is not None:
                await self.session.send_client_content(
                    turns={
                        "role": "user",
                        "parts": [{"text": text or "."}],
                    },
                    turn_complete=True,
                )

    async def listen_audio(self) -> None:
        mic_info = self.pya.get_default_input_device_info()
        self.input_stream = await asyncio.to_thread(
            self.pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        while True:
            chunk = await asyncio.to_thread(
                self.input_stream.read,
                CHUNK_SIZE,
                exception_on_overflow=False,
            )
            if self.audio_out_queue is not None:
                await self.audio_out_queue.put({"data": chunk, "mime_type": "audio/pcm"})

    async def send_audio(self) -> None:
        while True:
            if self.audio_out_queue is None or self.session is None:
                await asyncio.sleep(0.05)
                continue
            message = await self.audio_out_queue.get()
            await self.session.send_realtime_input(
                audio={
                    "data": message["data"],
                    "mime_type": str(message["mime_type"]),
                }
            )

    async def receive(self) -> None:
        while True:
            if self.session is None:
                await asyncio.sleep(0.05)
                continue

            try:
                async for message in self.session.receive():
                    if message.server_content and message.server_content.model_turn:
                        for part in message.server_content.model_turn.parts:
                            if part.inline_data and self.audio_in_queue is not None:
                                self.audio_in_queue.put_nowait(part.inline_data.data)
                            if part.text:
                                print(part.text, end="", flush=True)

                    if message.tool_call:
                        await self.handle_tool_calls(message.tool_call.function_calls)
            except errors.APIError as exc:
                print(f"\nLive API error: {exc}")
                raise asyncio.CancelledError("Live API session ended with an error") from exc

    async def handle_tool_calls(
        self,
        function_calls: list[types.FunctionCall],
    ) -> None:
        if self.session is None:
            return

        responses = []
        for function_call in function_calls:
            result = self.tools.call_tool(function_call.name, dict(function_call.args or {}))
            responses.append(
                types.FunctionResponse(
                    id=function_call.id,
                    name=function_call.name,
                    response=result,
                )
            )

        await self.session.send_tool_response(function_responses=responses)

    async def play_audio(self) -> None:
        self.output_stream = await asyncio.to_thread(
            self.pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        while True:
            if self.audio_in_queue is None:
                await asyncio.sleep(0.05)
                continue
            data = await self.audio_in_queue.get()
            await asyncio.to_thread(self.output_stream.write, data)

    async def run(self) -> None:
        config = build_live_connect_config(
            response_modalities=["AUDIO"],
            voice_name=self.voice_name,
        )
        try:
            async with (
                self.client.aio.live.connect(model=self.model, config=config) as session,
                asyncio.TaskGroup() as task_group,
            ):
                self.session = session
                self.audio_in_queue = asyncio.Queue()
                self.audio_out_queue = asyncio.Queue(maxsize=20)

                task_group.create_task(self.send_text())
                task_group.create_task(self.listen_audio())
                task_group.create_task(self.send_audio())
                task_group.create_task(self.receive())
                task_group.create_task(self.play_audio())
        except asyncio.CancelledError:
            pass
        except ExceptionGroup as exc:
            traceback.print_exception(exc)
        finally:
            if self.input_stream is not None:
                self.input_stream.close()
            if self.output_stream is not None:
                self.output_stream.close()
            self.pya.terminate()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    args = parser.parse_args()

    scheduler = VoiceScheduler(model=args.model, voice_name=args.voice)
    asyncio.run(scheduler.run())


if __name__ == "__main__":
    main()
