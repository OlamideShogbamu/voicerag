"""VoiceRAG agent — single-agent design with knowledge search + save."""

from __future__ import annotations

from typing import Annotated

from livekit import rtc
from livekit.agents import Agent, RunContext, function_tool

from agent.prompts.voicerag import VOICERAG_INSTRUCTIONS
from agent.tools.knowledge import save_knowledge, search_knowledge

_SIMILARITY_THRESHOLD = 0.55


class VoiceRAGAgent(Agent):
    def __init__(self, room: rtc.Room, user_id: str) -> None:
        self._room = room
        self._user_id = user_id
        super().__init__(instructions=VOICERAG_INSTRUCTIONS)

    async def on_enter(self) -> None:
        self.session.options.preemptive_generation = True
        await self.session.say("VoiceRAG ready. What would you like to talk about?")

    @function_tool
    async def search_knowledge(
        self,
        context: RunContext,
        query: Annotated[str, "What to look up — a fact, note, or topic the user shared earlier"],
    ) -> str:
        """Search the user's stored knowledge for relevant context.

        Use this whenever the user references something they previously told
        you, or asks about notes / documents they've shared.
        """
        results = await search_knowledge(self._user_id, query, top_k=5)
        relevant = [r for r in results if float(r.get("similarity", 0)) >= _SIMILARITY_THRESHOLD]
        if not relevant:
            return "Nothing relevant in saved notes."
        return "\n\n".join(
            f"[{r['source_type']}] {r['content']}" for r in relevant
        )

    @function_tool
    async def save_knowledge(
        self,
        context: RunContext,
        content: Annotated[str, "The fact, preference, or note to remember verbatim"],
    ) -> str:
        """Store a fact for later retrieval.

        Call when the user says things like "remember that…", "save this…",
        "for next time…", or otherwise asks you to remember something.
        """
        await save_knowledge(self._user_id, content, source_type="voice_note")
        return f'Got it — I\'ve saved: "{content}"'
