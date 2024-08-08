from collections.abc import Callable

from twitchio.ext import commands

from utils import const


def is_mod() -> Callable[[commands.Command], commands.Command]:
    async def pred(ctx: commands.Context) -> bool:
        author = ctx.message.author
        # if isinstance(author, twitchio.PartialChatter):
        #     author = ???
        if author.is_mod:  # type: ignore # the dev said it's fine
            return True
        else:
            msg = "Only moderators can use this command"
            raise commands.CheckFailure(msg)

    def decorator(func: commands.Command) -> commands.Command:
        func._checks.append(pred)
        return func

    return decorator


def is_irene() -> Callable[[commands.Command], commands.Command]:
    async def pred(ctx: commands.Context) -> bool:
        if (await ctx.message.author.user()).id == const.ID.Irene:
            return True
        else:
            msg = "Only Irene can use this command"
            raise commands.CheckFailure(msg)

    def decorator(func: commands.Command) -> commands.Command:
        func._checks.append(pred)
        return func

    return decorator
