from __future__ import annotations

import logging
import sys
import traceback
from typing import TYPE_CHECKING, List, Optional, Type

import asyncpg
from twitchio.ext import commands

from cogs import EXTENSIONS

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self


log = logging.getLogger(__name__)


class LueByt(commands.Bot):
    pool: asyncpg.Pool

    def __init__(self, access_token: str, initial_channels: List[str]):
        self.prefixes = ["!", "?", "$"]
        super().__init__(token=access_token, prefix=self.prefixes, initial_channels=initial_channels)

        self.repo = "https://github.com/Aluerie/LueByt"

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.close()

    async def event_ready(self):
        log.info(f"LueByt Ready as {self.nick} | user_id = {self.user_id}")

    async def event_command_error(self, ctx: commands.Context, error: Exception) -> None:
        # print('---------------------')
        # print(error, type(error))
        # getattr(ctx.command, 'name', 'Unknown') only bcs typing
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"{error}")
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f"{error}")
            # print(f"{type(error)} in {getattr(ctx.command, 'name', 'Unknown')}: {error}:", file=sys.stderr)
        elif isinstance(error, commands.CommandNotFound):
            #  idk otherwise we just spam console with commands from other bots and from my event thing
            pass
        elif isinstance(error, commands.MissingRequiredArgument):
            missing_arg = ", ".join([f"{x.name}" for x in error.args])
            await ctx.send(f"Missing required argument(-s): {missing_arg}")
        else:
            command_name = getattr(ctx.command, "name", "unknown")
            log.error(f"Ignoring exception in !{command_name} command: {error}:", exc_info=error)

    async def start(self):
        for ext in EXTENSIONS:
            self.load_module(ext)
        await super().start()
