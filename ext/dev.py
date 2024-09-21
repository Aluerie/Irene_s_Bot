from __future__ import annotations

import asyncio
import logging
import os
from typing import TYPE_CHECKING

from twitchio.ext import commands

from bot import IrenesCog
from utils import checks

if TYPE_CHECKING:
    from bot import IrenesBot

log = logging.getLogger(__name__)


class Management(IrenesCog):
    """Dev Only Commands."""

    @checks.is_vps()
    @checks.is_irene()
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
            os.system("sudo systemctl stop luebyt")
        except Exception as error:
            log.error(error, stack_info=True)
            # it might not go off
            await ctx.send("Something went wrong.")

    @checks.is_vps()
    @checks.is_irene()
    @commands.command(aliases=["restart"])
    async def reboot(self, ctx: commands.Context) -> None:
        """Restart the bot process on VPS.

        Usable to restart the bot without logging to VPS machine or committing something.
        """
        await ctx.send("Rebooting in 3 2 1")
        await asyncio.sleep(3)
        try:
            # non systemctl users - sorry
            os.system("sudo systemctl restart luebyt")
        except Exception as error:
            log.error(error, stack_info=True)
            # it might not go off
            await ctx.send("Something went wrong.")


def prepare(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    bot.add_cog(Management(bot))
