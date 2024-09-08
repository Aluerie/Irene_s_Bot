from __future__ import annotations

import asyncio
import os
import platform
from typing import TYPE_CHECKING

from twitchio.ext import commands

from bot import IrenesCog
from utils import checks

if TYPE_CHECKING:
    from bot import IrenesBot


class Management(IrenesCog):
    """Dev Only Commands."""

    @checks.is_irene()
    @commands.command(aliases=["kill"])
    async def maintenance(self, ctx: commands.Context) -> None:
        """Kill the bot process on VPS.

        This won't work on main PC.
        Usable for bot testing so I don't have double responses.

        Note that this will turn off the whole bot functionality so things like main bot alerts will also stop.
        """
        if platform.system() == "Windows":
            # wrong PC
            await ctx.send("This bot is not a VPS version.")
            return

        else:
            await ctx.send("Shutting down the bot in 3 2 1")
        await asyncio.sleep(3)
        try:
            # non systemctl users - sorry
            os.system("sudo systemctl stop luebyt")
        except Exception as error:
            print(error)
            # it might not go off
            await ctx.send("Something went wrong.")


def prepare(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    bot.add_cog(Management(bot))
