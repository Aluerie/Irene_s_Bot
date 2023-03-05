from __future__ import annotations
from typing import TYPE_CHECKING


import asyncpg

from config import POSTGRES_URL


if TYPE_CHECKING:
    pass


class DRecord(asyncpg.Record):
    """DRecord - Dot Record

    Same as `asyncpg.Record`, but allows dot-notations
    such as `record.id` instead of `record['id']`.
    """

    def __getattr__(self, name: str):
        return self[name]


async def create_pool() -> asyncpg.Pool:
    return await asyncpg.create_pool(
        POSTGRES_URL,
        command_timeout=60,
        min_size=10,
        max_size=10,
        record_class=DRecord,
        statement_cache_size=0,
    ) # type: ignore
