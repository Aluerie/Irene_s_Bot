from __future__ import annotations

import logging
import sys
import traceback
from typing import TYPE_CHECKING, Optional, Type

import asyncpg
from twitchio.ext import commands

from cogs import EXTENSIONS
from config import TWITCH_TOKEN

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self


log = logging.getLogger(__name__)


class AlueBot(commands.Bot):
    pool: asyncpg.Pool

    def __init__(self):
        self.prefixes = ["!", "?", "$"]
        super().__init__(token=TWITCH_TOKEN, prefix=self.prefixes, initial_channels=["Aluerie"])

        self.repo = 'https://github.com/Aluerie/AlueBot'

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
        log.info(f"TwitchBot Ready as {self.nick} | user_id = {self.user_id}")

    async def event_command_error(self, ctx: commands.Context, error: Exception) -> None:
        # print('---------------------')
        # print(error, type(error))
        # getattr(ctx.command, 'name', 'Unknown') only bcs typing
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f"{error}")
            # print(f"{type(error)} in {getattr(ctx.command, 'name', 'Unknown')}: {error}:", file=sys.stderr)
        elif isinstance(error, commands.CommandNotFound):
            #  idk otherwise we just spam console with commands from other bots and from my event thing
            pass
        elif isinstance(error, commands.MissingRequiredArgument):
            missing_arg = ', '.join([f'{x.name}' for x in error.args]) 
            await ctx.send(f'Missing required argument(-s): {missing_arg}')
        else:
            print(f"Ignoring exception in command {getattr(ctx.command, 'name', 'Unknown')}: {error}:", file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    async def start(self):
        for ext in EXTENSIONS:
            self.load_module(ext)
        await super().start()
