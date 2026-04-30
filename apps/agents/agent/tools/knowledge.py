"""RAG knowledge tools — search and save against the pgvector embeddings table."""

from __future__ import annotations

import json
import os
from typing import Any

import openai

from agent.db.database import get_pool

_EMBED_MODEL = "text-embedding-3-small"
_DIMS = 512


async def _embed(text: str) -> list[float]:
    client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = await client.embeddings.create(model=_EMBED_MODEL, input=text, dimensions=_DIMS)
    return resp.data[0].embedding


def _vec(vector: list[float]) -> str:
    return "[" + ",".join(str(v) for v in vector) + "]"


async def search_knowledge(user_id: str, query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Return the top-k most semantically similar chunks for this user."""
    vector = await _embed(query)
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT content, source_type, source_ref,
                   1 - (embedding <=> $2::vector) AS similarity
            FROM public.embeddings
            WHERE user_id = $1
            ORDER BY embedding <=> $2::vector
            LIMIT $3
            """,
            user_id,
            _vec(vector),
            top_k,
        )
    return [dict(r) for r in rows]


async def save_knowledge(
    user_id: str,
    content: str,
    source_type: str = "voice_note",
    source_ref: str | None = None,
    metadata: dict | None = None,
) -> str:
    """Embed `content` and persist it for later retrieval. Returns the row id."""
    vector = await _embed(content)
    pool = get_pool()
    async with pool.acquire() as conn:
        row_id = await conn.fetchval(
            """
            INSERT INTO public.embeddings
              (user_id, source_type, source_ref, content, embedding, metadata)
            VALUES ($1, $2, $3, $4, $5::vector, $6::jsonb)
            RETURNING id
            """,
            user_id,
            source_type,
            source_ref,
            content,
            _vec(vector),
            json.dumps(metadata or {}),
        )
    return str(row_id)
