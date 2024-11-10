from __future__ import annotations

import asyncio
import logging
import os
from typing import TYPE_CHECKING

from twitchio.ext import commands

from bot import IrenesComponent
from utils import checks

if TYPE_CHECKING:
    from bot import IrenesBot

log = logging.getLogger(__name__)


class Development(IrenesComponent):
    """Dev Only Commands."""

    if TYPE_CHECKING:
        ext_alias_mapping: dict[str, str]

    @checks.is_vps()
    @commands.is_owner()
    @commands.command(aliases=["kill"])
    async def maintenance(self, ctx: commands.Context) -> None:
        """Kill the bot process on VPS.

        Usable for bot testing so I don't have double responses.

        Note that this will turn off the whole bot functionality so things like main bot alerts will also stop.
        """
        await ctx.send("Shutting down the bot in 3 2 1")
        await asyncio.sleep(3)
        try:
            # non systemctl users - sorry
            os.system("sudo systemctl stop irenesbot")
        except Exception as error:
            log.error(error, stack_info=True)
            # it might not go off
            await ctx.send("Something went wrong.")

    @checks.is_vps()
    @commands.is_owner()
    @commands.command(aliases=["restart"])
    async def reboot(self, ctx: commands.Context) -> None:
        """Restart the bot process on VPS.

        Usable to restart the bot without logging to VPS machine or committing something.
        """
        await ctx.send("Rebooting in 3 2 1")
        await asyncio.sleep(3)
        try:
            # non systemctl users - sorry
            os.system("sudo systemctl restart irenesbot")
        except Exception as error:
            log.error(error, stack_info=True)
            # it might not go off
            await ctx.send("Something went wrong.")

    @checks.is_vps()
    @commands.is_owner()
    @commands.command()
    async def unload(self, ctx: commands.Context, *, extension: str) -> None:
        ext = self.ext_alias_mapping[extension.lower()]
        await self.bot.unload_module(ext)
        await ctx.send(f"Successfully unloaded `{ext}`.")

    @checks.is_vps()
    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx: commands.Context, *, extension: str) -> None:
        ext = self.ext_alias_mapping[extension.lower()]
        await self.bot.reload_module(ext)
        await ctx.send(f"Successfully reloaded `{ext}`.")

    @checks.is_vps()
    @commands.is_owner()
    @commands.command()
    async def load(self, ctx: commands.Context, *, extension: str) -> None:
        ext = self.ext_alias_mapping[extension.lower()]
        await self.bot.load_module(ext)
        await ctx.send(f"Successfully loaded `{ext}`.")


async def setup(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    await bot.add_component(Development(bot))
