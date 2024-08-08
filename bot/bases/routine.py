from __future__ import annotations

import asyncio
import datetime
from typing import TYPE_CHECKING, Any

from discord import Embed
from twitchio.ext import routines

from .cog import IrenesCog

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop
    from collections.abc import Callable, Coroutine

    from ..bot import IrenesBot


__all__ = ("irenes_routine",)


class IrenesRoutine(routines.Routine):
    _bot: IrenesBot

    def __init__(
        self,
        *,
        coro: Callable[..., Any],
        loop: AbstractEventLoop | None = None,
        iterations: int | None = None,
        time: datetime.datetime | None = None,
        delta: float | None = None,
        wait_first: bool | None = False,
    ) -> None:
        super().__init__(coro=coro, loop=loop, iterations=iterations, time=time, delta=delta, wait_first=wait_first)
        self._before = self._new_before
        self._error = self._new_error

    async def _new_before(self, *args: Any) -> None:
        cog = args[0]
        if isinstance(cog, IrenesCog):
            self._bot = cog.bot
            await cog.bot.wait_for_ready()

    async def _new_error(self, *args: Any) -> None:
        exception: Exception = args[-1]
        embed = Embed(description="Error in the routine")
        await self._bot.exc_manager.register_error(exception, embed)


def compute_timedelta(dt: datetime.datetime) -> float:
    if dt.tzinfo is None:
        dt = dt.astimezone()

    now = datetime.datetime.now(datetime.UTC)
    return max((dt - now).total_seconds(), 0)


def irenes_routine(
    *,
    seconds: float = 0,
    minutes: float = 0,
    hours: float = 0,
    time: datetime.datetime | None = None,
    iterations: int | None = None,
    wait_first: bool = False,
) -> Callable[..., IrenesRoutine]:
    def decorator(coro: Callable[..., Coroutine[Any, Any, Any]]) -> IrenesRoutine:
        time_ = time

        if any((seconds, minutes, hours)) and time_:
            msg = "Argument <time> can not be used in conjunction with any <seconds>, <minutes> or <hours> argument(s)."
            raise RuntimeError(msg)

        if not time_:
            delta = compute_timedelta(
                datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=seconds, minutes=minutes, hours=hours)
            )
        else:
            delta = None

            now = datetime.datetime.now(time_.tzinfo)
            if time_ < now:
                time_ = datetime.datetime.combine(now.date(), time_.time())
            if time_ < now:
                time_ = time_ + datetime.timedelta(days=1)

        if not asyncio.iscoroutinefunction(coro):
            msg = f"Expected coroutine function not type, {type(coro).__name__!r}."
            raise TypeError(msg)

        return IrenesRoutine(coro=coro, time=time_, delta=delta, iterations=iterations, wait_first=wait_first)

    return decorator
