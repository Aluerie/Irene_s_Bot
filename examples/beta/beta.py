#  ruff: noqa: D101, D102, D103

from __future__ import annotations

from examples.beta.base import *


class BetaTest(BetaCog):
    @irenes_loop(count=1)
    async def beta_test(self) -> None:
        pass

    @commands.command()
    async def beta(self, ctx: commands.Context) -> None:
        pass


def prepare(bot: IrenesBot) -> None:
    if platform.system() == "Windows":
        bot.add_cog(BetaTest(bot))
