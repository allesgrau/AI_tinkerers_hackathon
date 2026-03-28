import asyncio
import json
import os

from google import genai
from google.genai import types

from agent.gemini_live_config import build_live_connect_config
from agent.tool_registry import SchedulingAgentTools

MODEL = "models/gemini-3.1-flash-live-preview"

async def main():
    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"],
        http_options={"api_version": "v1alpha"},
    )

    tools = SchedulingAgentTools()
    config = build_live_connect_config()

    async with client.aio.live.connect(model=MODEL, config=config) as session:
        await session.send_client_content(
            turns={"role": "user", "parts": [{"text": "I need a cardiologist appointment."}]}
        )

        async for message in session.receive():
            server_content = getattr(message, "server_content", None)
            if server_content and getattr(server_content, "model_turn", None):
                print(server_content.model_turn)

            tool_call = getattr(message, "tool_call", None)
            if tool_call:
                responses = []
                for fc in tool_call.function_calls:
                    result = tools.call_tool(fc.name, dict(fc.args or {}))
                    responses.append(
                        types.FunctionResponse(
                            id=fc.id,
                            name=fc.name,
                            response=result,
                        )
                    )
                await session.send_tool_response(function_responses=responses)

asyncio.run(main())
