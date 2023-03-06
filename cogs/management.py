from __future__ import annotations

import os
from typing import TYPE_CHECKING

from twitchio.ext import commands

from utils.checks import is_aluerie

if TYPE_CHECKING:
    from utils.bot import AlueBot


class Management(commands.Cog):
    def __init__(self, bot: AlueBot):
        self.bot: AlueBot = bot

    @is_aluerie()
    @commands.command()
    async def maintenance(self, ctx: commands.Context):
        await ctx.send("Shutting down the bot")
        try:
            os.system("sudo systemctl stop aluebot")
        except Exception as error:
            print(error)
            # it might not go off
            await ctx.send("Something went wrong.")


def prepare(bot: AlueBot):
    bot.add_cog(Management(bot))
