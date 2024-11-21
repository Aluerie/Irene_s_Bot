from __future__ import annotations

from typing import TYPE_CHECKING

from .commands import DotaCommands

if TYPE_CHECKING:
    from bot import IrenesBot


async def setup(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    await bot.add_component(DotaCommands(bot))
