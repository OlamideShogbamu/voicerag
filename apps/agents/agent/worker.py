"""VoiceRAG LiveKit worker — STT → LLM → TTS with RAG tools."""

from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()

from livekit import agents
from livekit.agents import AgentSession, JobContext, TurnHandlingOptions, WorkerOptions
from livekit.plugins import deepgram, openai, silero

from agent.db.database import init_db
from agent.tts_edge import TTS as EdgeTTS
from agent.voicerag import VoiceRAGAgent


async def voicerag_session(ctx: JobContext) -> None:
    await init_db()
    await ctx.connect()

    participant = await ctx.wait_for_participant()
    user_id = participant.identity

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=EdgeTTS(voice="en-US-AriaNeural"),
        vad=silero.VAD.load(
            min_silence_duration=0.7,
            activation_threshold=0.5,
            deactivation_threshold=0.3,
        ),
        turn_handling=TurnHandlingOptions(interruption={"mode": "vad"}),
    )

    await session.start(
        room=ctx.room,
        agent=VoiceRAGAgent(room=ctx.room, user_id=user_id),
    )


if __name__ == "__main__":
    agents.cli.run_app(
        WorkerOptions(
            entrypoint_fnc=voicerag_session,
            agent_name="voicerag",
        )
    )
