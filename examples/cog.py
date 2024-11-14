from __future__ import annotations

from typing import TYPE_CHECKING

from twitchio.ext import commands

from bot import IrenesComponent

if TYPE_CHECKING:
    from bot import IrenesBot


class NewCog(IrenesComponent):
    """."""

    @commands.command()
    async def new_command(self, ctx: commands.Context) -> None:
        """."""
        await ctx.send("Not implemented yet!")


async def setup(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    await bot.add_component(NewCog(bot))
