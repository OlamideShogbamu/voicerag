"""Shared asyncpg connection pool — initialised once per worker process."""

import os
import asyncpg

_pool: asyncpg.Pool | None = None


async def init_db() -> None:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            os.environ["DATABASE_URL"],
            min_size=2,
            max_size=10,
            timeout=10,        # fail fast if DB is unreachable
            command_timeout=30,
        )


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("DB pool not initialised — call init_db() first")
    return _pool
