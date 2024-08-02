from __future__ import annotations

import logging
from typing import TYPE_CHECKING, override

import discord
from twitchio.ext import commands

from ext import EXTENSIONS

from .exc_manager import ExceptionManager

if TYPE_CHECKING:
    import asyncpg


log = logging.getLogger(__name__)


class IrenesBot(commands.Bot):
    pool: asyncpg.Pool

    def __init__(self, access_token: str, initial_channels: list[str]) -> None:
        """Init

        Parameters
        ----------
        access_token : str
            _description_
        initial_channels : list[str]
            List of channel names.
            Interestingly enough, at the moment, they don't straight accept channel ids.
        """

        self.prefixes = ["!", "?", "$"]
        super().__init__(token=access_token, prefix=self.prefixes, initial_channels=initial_channels)

        self.repo = "https://github.com/Aluerie/Irene_s_Bot"

        self.exc_manager = ExceptionManager(self)

    @override
    async def event_ready(self) -> None:
        log.info("Irene_s_Bot is ready as %s (user_id = %s)", self.nick, self.user_id)

    @override
    async def event_command_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"{error}")
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f"{error}")
        elif isinstance(error, commands.CommandNotFound):
            #  otherwise we just spam console with commands from other bots and from my event thing
            pass
        elif isinstance(error, commands.MissingRequiredArgument):
            missing_arg = ", ".join([f"{x.name}" for x in error.args])
            await ctx.send(f"Missing required argument(-s): {missing_arg}")
        else:
            command_name = getattr(ctx.command, "name", "unknown")

            embed = discord.Embed(description=f"Exception in !{command_name} command: {command_name}:")
            await self.exc_manager.register_error(error, embed=embed)

    @override
    async def start(self) -> None:
        for ext in EXTENSIONS:
            self.load_module(ext)
        await super().start()
