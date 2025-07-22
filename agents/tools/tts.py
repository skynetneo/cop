"""tts_stream_tool.py – LangChain‑style tool for ElevenLabs TTS streaming

Usage inside agent prompt:
    result_b64 = tts_stream_tool(text="Hello there…")
    # returns Base64‑encoded MP3 suitable for <audio src="data:audio/mpeg;base64,..."> tags

Design notes
------------
• Follows LangChain tool API via @tool decorator (sync wrapper calls async core).
• Aggregates streamed bytes into memory, then Base64‑encodes so the agent can
  embed it in chat or store it elsewhere.
• Users that need low‑latency playback can bypass the wrapper and call
  `text_to_audio_stream` directly, piping chunks to a websocket.
"""

from __future__ import annotations

import os, logging, base64, asyncio, httpx
from typing import AsyncGenerator, Callable, Any, Coroutine
from pydantic import BaseModel, Field
from langchain_core.tools import tool

# ----------------------------------------------------------------------------
# Environment & logging
# ----------------------------------------------------------------------------
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

if not all([ELEVENLABS_API_KEY, VOICE_ID]):
    raise EnvironmentError("Missing ELEVENLABS_API_KEY or VOICE_ID in env vars")

logger = logging.getLogger("tts_stream_tool")
logger.addHandler(logging.NullHandler())

# ----------------------------------------------------------------------------
# Core streaming helper (unchanged except minor refactor)
# ----------------------------------------------------------------------------
async def _text_to_audio_stream(
    text_chunk_stream: AsyncGenerator[str, None],
    output_callback: Callable[[bytes], Coroutine[Any, Any, None]],
) -> None:
    """Stream ElevenLabs TTS; forward audio bytes to *output_callback*."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        async for chunk in text_chunk_stream:
            if not chunk:
                continue
            payload = {
                "text": chunk,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
            }
            try:
                async with client.stream("POST", url, headers=headers, json=payload) as resp:
                    resp.raise_for_status()
                    async for audio_bytes in resp.aiter_bytes():
                        await output_callback(audio_bytes)
            except httpx.ReadTimeout:
                logger.warning("ElevenLabs timed out for a chunk")
            except Exception as e:
                logger.error("ElevenLabs error: %s", e)
                break

# ----------------------------------------------------------------------------
# LangChain tool wrapper
# ----------------------------------------------------------------------------
class _TTSInput(BaseModel):
    text: str = Field(..., description="Plain text to synthesise via ElevenLabs")

@tool("tts_stream_tool", args_schema=_TTSInput, return_direct=True)
def tts_stream_tool(text: str) -> str:
    """Convert *text* to speech using ElevenLabs and return Base64‑encoded MP3.

    This sync wrapper spawns an asyncio loop, streams audio, aggregates it into
    memory, and returns a base64 string the calling agent can embed.
    """

    async def _runner(user_text: str) -> str:
        # Create a one‑shot generator (single chunk) – keeps interface simple
        async def gen():
            yield user_text
        buf: bytearray = bytearray()
        async def sink(b: bytes):
            buf.extend(b)
        await _text_to_audio_stream(gen(), sink)
        return base64.b64encode(buf).decode()

    return asyncio.run(_runner(text))


# ----------------------------------------------------------------------------
# __all__ for clean imports
# ----------------------------------------------------------------------------
__all__ = ["tts_stream_tool"]
