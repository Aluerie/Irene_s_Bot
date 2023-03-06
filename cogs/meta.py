from __future__ import annotations

from typing import TYPE_CHECKING

import twitchio
from twitchio.ext import commands

from utils.const import ALUERIE_TWITCH_NAME

if TYPE_CHECKING:
    from utils.bot import AlueBot


class Meta(commands.Cog):
    def __init__(self, bot: AlueBot):
        self.bot: AlueBot = bot

    @commands.Cog.event()
    async def event_ready(self):
        channel: twitchio.Channel = self.bot.get_channel(ALUERIE_TWITCH_NAME) #type: ignore
        await channel.send('hi the bot is reloaded')

    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send("\N{TABLE TENNIS PADDLE AND BALL} Pong!")

    @commands.command()
    async def hello(self, ctx: commands.Context):
        await ctx.send(f"Hello @{ctx.author.name} yo")

    @commands.command()
    async def source(self, ctx: commands.Context):
        await ctx.send(f"{self.bot.repo} DankReading")


def prepare(bot: AlueBot):
    bot.add_cog(Meta(bot))
