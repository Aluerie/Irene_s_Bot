from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

import asyncpg

from config import POSTGRES_URL

if TYPE_CHECKING:

    class PoolTypedWithAny(asyncpg.Pool[asyncpg.Record]):
        """Fake Type Class.

        For typing purposes, our `bot.pool` will be "type-ignore"'d-as `PoolTypedWithAny`
        that allows us to properly type the return values via narrowing like mentioned in instructions above
        without hundreds of "type: ignore" notices for each TypedDict.

        I could use Protocol to type it all, but `async-stubs` provide a good job in typing most of the stuff
        and we also don't lose doc-string this way.

        * Right now, asyncpg is untyped so this is better than the current status quo
        * If we ever need the regular Pool type we have `bot.database` without any shenanigans.
        """

        # all methods below were changed from "asyncpg.Record" to "Any"

        @override
        async def fetch(self, query: str, *args: Any, timeout: float | None = None) -> list[Any]: ...

        @override
        async def fetchrow(self, query: str, *args: Any, timeout: float | None = None) -> Any: ...


async def create_pool() -> asyncpg.Pool[asyncpg.Record]:
    """Create AsyncPG Pool."""
    return await asyncpg.create_pool(
        POSTGRES_URL,
        command_timeout=60,
        min_size=10,
        max_size=10,
        statement_cache_size=0,
    )  # type: ignore
