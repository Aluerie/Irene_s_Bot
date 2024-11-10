from __future__ import annotations

import platform
from typing import Any

from twitchio.ext import commands

from . import const, errors


def is_vps() -> Any:
    """Allow the command to be completed only on VPS machine.

    A bit niche, mainly used for developer commands to interact with VPS machine such as
    kill the bot process or reboot it.
    """

    async def predicate(_: commands.Context) -> bool:
        if platform.system() == "Windows":
            # wrong PC
            msg = f"Only production bot allows usage of this command {const.FFZ.peepoPolice}"
            raise errors.CheckError(msg)
        else:
            return True

    return commands.guard(predicate)
