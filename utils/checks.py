from __future__ import annotations

import platform
from typing import TYPE_CHECKING

from . import const, errors

if TYPE_CHECKING:
    from collections.abc import Callable

    from twitchio.ext import commands

    CheckCallable = Callable[[commands.Command], commands.Command]


def is_mod() -> CheckCallable:
    """Only allow moderators to use the command."""

    async def pred(ctx: commands.Context) -> bool:
        author = ctx.message.author
        # if isinstance(author, twitchio.PartialChatter):
        #     author = ???
        if author.is_mod:  # type: ignore # the dev said it's fine
            return True
        else:
            msg = "Only moderators can use this command"
            raise errors.CheckError(msg)

    def decorator(func: commands.Command) -> commands.Command:
        func._checks.append(pred)
        return func

    return decorator


def is_irene() -> CheckCallable:
    """Only allow Irene to use the command."""

    async def pred(ctx: commands.Context) -> bool:
        if (await ctx.message.author.user()).id == const.ID.Irene:  # TODO: do we really need an await function here
            return True
        else:
            msg = "Only Irene can use this command"
            raise errors.CheckError(msg)

    def decorator(func: commands.Command) -> commands.Command:
        func._checks.append(pred)
        return func

    return decorator


def is_vps() -> CheckCallable:
    """Allow the command to be completed only on VPS machine.

    A bit niche, mainly used for developer commands to interact with VPS machine such as
    kill the bot process or reboot it.
    """

    async def pred(_: commands.Context) -> bool:
        if platform.system() == "Windows":
            # wrong PC
            msg = f"Only production bot allows usage of this command {const.FFZ.peepoPolice}"
            raise errors.CheckError(msg)
        else:
            return True

    def decorator(func: commands.Command) -> commands.Command:
        func._checks.append(pred)
        return func

    return decorator
