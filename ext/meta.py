from __future__ import annotations

from typing import TYPE_CHECKING

import twitchio  # noqa: TCH002

# import pkg_resources
from twitchio.ext import commands

from utils import IrenesCog, checks

if TYPE_CHECKING:
    from bot import IrenesBot


class Meta(IrenesCog):
    @commands.Cog.event()  # type: ignore # one day they will fix it
    async def event_ready(self) -> None:
        await self.irene_channel().send("hi the bot is reloaded.")

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.send("\N{TABLE TENNIS PADDLE AND BALL} Pong!")

    @commands.command(aliases=["hi", "yo"])
    async def hello(self, ctx: commands.Context) -> None:
        await ctx.send(f"Hello @{ctx.author.name} yo")

    @commands.command()
    async def source(self, ctx: commands.Context) -> None:
        await ctx.send(f"{self.bot.repo} DankReading")

    @checks.is_irene()
    @commands.command()
    async def channel_add(self, ctx: commands.Context, channel: twitchio.Channel) -> None:
        query = """
            INSERT INTO joined_streamers
            (user_id, user_name)
            VALUES ($1, $2)
        """
        await self.bot.pool.execute(query, (await channel.user()).id, channel.name)
        await self.bot.join_channels([channel.name])
        await ctx.send(f"Added the channel {channel.name}.")

    @checks.is_irene()
    @commands.command()
    async def channel_del(self, ctx: commands.Context, channel: twitchio.Channel) -> None:
        query = """
            DELETE FROM joined_streamers
            WHERE user_id=$1
        """
        await self.bot.pool.execute(query, (await channel.user()).id)
        await self.bot.part_channels([channel.name])
        await ctx.send(f"Deleted the channel {channel.name}")


def prepare(bot: IrenesBot) -> None:
    bot.add_cog(Meta(bot))
