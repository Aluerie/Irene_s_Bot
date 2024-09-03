from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Self, override

import discord
from twitchio.ext import commands, eventsub

from core import CORE_EXTENSIONS
from ext import EXTENSIONS
from utils.dota import Dota2Client

from .exc_manager import ExceptionManager

if TYPE_CHECKING:
    import asyncpg
    from aiohttp import ClientSession

    from utils.database import PoolTypedWithAny

__all__ = ("IrenesBot",)

log = logging.getLogger(__name__)


class IrenesBot(commands.Bot):

    if TYPE_CHECKING:
        logs_via_webhook_handler: logging.Handler

    def __init__(
        self,
        access_token: str,
        initial_channels: list[str],
        *,
        session: ClientSession,
        pool: asyncpg.Pool[asyncpg.Record],
    ) -> None:
        """Initiate IrenesBot.

        Parameters
        ----------
        initial_channels
            List of channel names (names, not ids!).

        """
        self.prefixes = ["!", "?", "$"]
        super().__init__(token=access_token, prefix=self.prefixes, initial_channels=initial_channels)
        self.database: asyncpg.Pool[asyncpg.Record] = pool
        self.pool: PoolTypedWithAny = pool  # type: ignore # asyncpg typehinting crutch, read `utils.database` for more
        self.session: ClientSession = session

        self.eventsub: eventsub.EventSubWSClient = eventsub.EventSubWSClient(self)

        self.exc_manager = ExceptionManager(self)

        self.repo = "https://github.com/Aluerie/Irene_s_Bot"

        self.dota = Dota2Client(self)

    async def __aenter__(self) -> Self:
        return self

    # todo: remove 3.0
    async def __aexit__(self, *_: Any) -> None:
        return

    @override
    async def event_ready(self) -> None:
        log.info("Irene_s_Bot is ready as %s (user_id = %s)", self.nick, self.user_id)
        await self.dota.wait_until_ready()

    @override
    async def event_command_error(self, ctx: commands.Context, error: Exception) -> None:
        match error:
            case commands.BadArgument():
                log.warning(error.message)
                await ctx.send(f"Couldn't find any {error.name} like that")
            case commands.ArgumentParsingFailed() | commands.CheckFailure():
                await ctx.send(str(error))
            case commands.CommandOnCooldown():
                await ctx.send(
                    f"Command {ctx.prefix}{error.command.name} is on cooldown! Try again in {error.retry_after:.0f} sec."
                )
            case commands.CommandNotFound():
                #  otherwise we just spam console with commands from other bots and from my event thing
                pass
            case commands.MissingRequiredArgument():
                await ctx.send(f"Missing required argument(-s): {error.name}")
            case _:
                command_name = getattr(ctx.command, "name", "unknown")

                embed = discord.Embed(description=f"Exception {error} in !{command_name} command: {command_name}:")
                await self.exc_manager.register_error(error, embed=embed)

    @override
    async def event_error(self, error: Exception, data: str | None = None) -> None:
        embed = discord.Embed(description=f"Exception {error.__class__.__name__} in event: {data}")
        await self.exc_manager.register_error(error, embed=embed)

    @override
    async def start(self) -> None:
        for ext in CORE_EXTENSIONS:
            self.load_module(ext)
        for ext in EXTENSIONS:
            self.load_module(ext)

        await super().start()
        # await asyncio.gather(
        #     super().start(),
        #     self.dota.login(),
        # )

    @override
    async def close(self) -> None:
        await self.dota.close()
        await super().close()

    def webhook_from_url(self, url: str) -> discord.Webhook:
        """A shortcut function with filled in discord.Webhook.from_url args."""
        return discord.Webhook.from_url(url=url, session=self.session)
