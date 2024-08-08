from __future__ import annotations

from typing import TYPE_CHECKING

from twitchio.ext import commands

from bot import IrenesCog

if TYPE_CHECKING:
    from bot import IrenesBot


class NewCog(IrenesCog):
    @commands.command()
    async def new_command(self, ctx: commands.Context) -> None:
        await ctx.send("Not implemented yet!")


def prepare(bot: IrenesBot) -> None:
    bot.add_cog(NewCog(bot))
