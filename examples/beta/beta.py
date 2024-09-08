#  ruff: noqa: D101, D102, D103

from __future__ import annotations

from examples.beta.base import *


class BetaTest(BetaCog):
    @routines.routine(iterations=1)
    async def beta_test(self) -> None:
        pass


def prepare(bot: IrenesBot) -> None:
    if platform.system() == "Windows":
        bot.add_cog(BetaTest(bot))
