from __future__ import annotations

from typing import TYPE_CHECKING

from twitchio.ext import commands


if TYPE_CHECKING:
    from utils.bot import AlueBot


class Meta(commands.Cog):
    def __init__(self, bot: AlueBot):
        self.bot: AlueBot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send("\N{TABLE TENNIS PADDLE AND BALL} Pong!")

    @commands.command()
    async def hello(self, ctx: commands.Context):
        await ctx.send(f'Hello @{ctx.author.name} yo')


def prepare(bot: AlueBot):
    bot.add_cog(Meta(bot))
