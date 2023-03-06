from __future__ import annotations

from typing import TYPE_CHECKING

import twitchio
from twitchio.ext import commands

from utils.const import ALUERIE_TWITCH_NAME
from utils.checks import is_aluerie

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

    @is_aluerie()
    @commands.command()
    async def channel_add(self, ctx: commands.Context, channel: twitchio.Channel):
        query = """ INSERT INTO twitch_users
                    (user_id, user_name)
                    VALUES ($1, $2)
                """
        await self.bot.pool.execute(query, (await channel.user()).id, channel.name)
        await ctx.send(f"Added the channel {channel.name}.")

    @is_aluerie()
    @commands.command()
    async def channel_del(self, ctx: commands.Context, channel: twitchio.Channel):
        query = """ DELETE FROM twitch_users 
                    WHERE user_id=$1
                """
        await self.bot.pool.execute(query, (await channel.user()).id)
        await ctx.send(f"Deleted the channel {channel.name}")


def prepare(bot: AlueBot):
    bot.add_cog(Meta(bot))
