from __future__ import annotations

import platform
from typing import TYPE_CHECKING

import twitchio  # noqa: TCH002

# import pkg_resources
from twitchio.ext import commands

from bot import IrenesCog
from utils import checks, const

if TYPE_CHECKING:
    from bot import IrenesBot


class Meta(IrenesCog):
    """Meta features."""

    @commands.Cog.event()  # type: ignore # one day they will fix it
    async def event_ready(self) -> None:
        """Announce that bot is successfully reloaded/restarted."""
        # await self.bot.join_channels(["Irene_Adler__"]) # not needed
        if platform.system() != "Windows":
            await self.irene_channel().send(f"{const.STV.hi} the bot is reloaded.")

    @checks.is_irene()
    @commands.command()
    async def channel_add(self, ctx: commands.Context, channel: twitchio.Channel) -> None:
        """Make the bot join @channel.

        Its commands and functionality should become available there.
        """
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
        """Remove the bot from @channel.

        The bot should leave their chat and stop responding to commands.
        """
        query = """
            DELETE FROM joined_streamers
            WHERE user_id=$1
        """
        await self.bot.pool.execute(query, (await channel.user()).id)
        await self.bot.part_channels([channel.name])
        await ctx.send(f"Deleted the channel {channel.name}")


def prepare(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    bot.add_cog(Meta(bot))
