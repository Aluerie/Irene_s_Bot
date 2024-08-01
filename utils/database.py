from __future__ import annotations

import asyncpg

from config import POSTGRES_URL


async def create_pool() -> asyncpg.Pool:
    return await asyncpg.create_pool(
        POSTGRES_URL,
        command_timeout=60,
        min_size=10,
        max_size=10,
        statement_cache_size=0,
    )  # type: ignore
