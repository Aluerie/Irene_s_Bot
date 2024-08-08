from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING

from twitchio.ext import commands

from bot import IrenesCog
from utils import checks

if TYPE_CHECKING:
    from bot import IrenesBot


class Management(IrenesCog):
    @checks.is_irene()
    @commands.command(aliases=["kill"])
    async def maintenance(self, ctx: commands.Context) -> None:
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
    bot.add_cog(Management(bot))
