from __future__ import annotations

import platform
from typing import TYPE_CHECKING

from twitchio.ext import commands

from bot import IrenesComponent
from utils import const

if TYPE_CHECKING:
    from bot import IrenesBot


class Meta(IrenesComponent):
    """Meta features."""

    @commands.Component.listener(name="ready")
    async def announce_reloaded(self) -> None:
        """Announce that bot is successfully reloaded/restarted."""
        # await self.bot.join_channels(["Irene_Adler__"]) # not needed
        if platform.system() != "Windows":
            await self.deliver(f"{const.STV.hi} the bot is reloaded.")


async def setup(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    await bot.add_component(Meta(bot))
