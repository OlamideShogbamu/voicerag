"""LiveKit-agents TTS plugin wrapping Microsoft Edge TTS (edge-tts)."""

from __future__ import annotations

import edge_tts
from livekit.agents import APIConnectionError, APIConnectOptions, tts
from livekit.agents.types import DEFAULT_API_CONNECT_OPTIONS

SAMPLE_RATE = 24000
NUM_CHANNELS = 1
DEFAULT_VOICE = "en-US-AriaNeural"


def speed_to_rate(speed: float) -> str:
    """Convert a float speed multiplier (0.5–2.0) to an edge-tts rate string."""
    pct = round((speed - 1.0) * 100)
    return f"+{pct}%" if pct >= 0 else f"{pct}%"


class TTS(tts.TTS):
    def __init__(self, *, voice: str = DEFAULT_VOICE, rate: str = "+0%") -> None:
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=False),
            sample_rate=SAMPLE_RATE,
            num_channels=NUM_CHANNELS,
        )
        self._voice = voice
        self._rate = rate

    @property
    def model(self) -> str:
        return "edge-tts"

    @property
    def provider(self) -> str:
        return "microsoft"

    def synthesize(
        self, text: str, *, conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS
    ) -> "_ChunkedStream":
        return _ChunkedStream(tts=self, input_text=text, conn_options=conn_options)


class _ChunkedStream(tts.ChunkedStream):
    def __init__(self, *, tts: TTS, input_text: str, conn_options: APIConnectOptions) -> None:
        super().__init__(tts=tts, input_text=input_text, conn_options=conn_options)
        self._tts: TTS = tts

    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        try:
            communicate = edge_tts.Communicate(
                self.input_text, self._tts._voice, rate=self._tts._rate
            )

            output_emitter.initialize(
                request_id="edge-tts",
                sample_rate=SAMPLE_RATE,
                num_channels=NUM_CHANNELS,
                mime_type="audio/mpeg",
            )

            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    output_emitter.push(chunk["data"])

            output_emitter.flush()

        except Exception as e:
            raise APIConnectionError() from e
