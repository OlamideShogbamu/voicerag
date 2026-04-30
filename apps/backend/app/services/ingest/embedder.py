"""
Embed text chunks with text-embedding-3-small (512 dims) and store in pgvector.
Also provides cosine similarity search for the agent's RAG tool.
"""

from __future__ import annotations

from typing import Any

import asyncpg
import openai

from app.core.config import settings

_EMBED_MODEL = "text-embedding-3-small"
_DIMS = 512
_TOP_K = 5


async def embed_text(text: str) -> list[float]:
    """Return a 512-dim embedding vector for the given text."""
    client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
    resp = await client.embeddings.create(
        model=_EMBED_MODEL,
        input=text,
        dimensions=_DIMS,
    )
    return resp.data[0].embedding


async def store_embedding(
    pool: asyncpg.Pool,
    user_id: str,
    content: str,
    source_type: str,
    source_ref: str | None = None,
    metadata: dict | None = None,
) -> str:
    """Embed `content` and persist to public.embeddings. Returns the row UUID."""
    vector = await embed_text(content)
    vector_str = "[" + ",".join(str(v) for v in vector) + "]"

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
            vector_str,
            __import__("json").dumps(metadata or {}),
        )
    return str(row_id)


async def search_embeddings(
    pool: asyncpg.Pool,
    user_id: str,
    query: str,
    top_k: int = _TOP_K,
) -> list[dict[str, Any]]:
    """Return the top-k most semantically similar chunks for this user."""
    vector = await embed_text(query)
    vector_str = "[" + ",".join(str(v) for v in vector) + "]"

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT content, source_type, source_ref, metadata,
                   1 - (embedding <=> $2::vector) AS similarity
            FROM public.embeddings
            WHERE user_id = $1
            ORDER BY embedding <=> $2::vector
            LIMIT $3
            """,
            user_id,
            vector_str,
            top_k,
        )
    return [dict(r) for r in rows]
