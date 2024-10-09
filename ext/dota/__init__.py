from __future__ import annotations

from typing import TYPE_CHECKING

from .commands import DotaCommands

if TYPE_CHECKING:
    from bot import IrenesBot


def prepare(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    bot.add_cog(DotaCommands(bot))
