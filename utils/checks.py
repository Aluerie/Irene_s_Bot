import twitchio
from twitchio.ext import commands

from utils.const import ALUERIE_TWITCH_ID


def is_mod():
    async def pred(ctx: commands.Context) -> bool:
        author = ctx.message.author
        # if isinstance(author, twitchio.PartialChatter):
        #     author = ???
        if author.is_mod:
            return True
        else:
            raise commands.CheckFailure("Only moderators can use this command")

    def decorator(func: commands.Command):
        func._checks.append(pred)
        return func

    return decorator


def is_aluerie():
    async def pred(ctx: commands.Context) -> bool:
        if (await ctx.message.author.user()).id == ALUERIE_TWITCH_ID:
            return True
        else:
            raise commands.CheckFailure("Only Aluerie can use this command")

    def decorator(func: commands.Command):
        func._checks.append(pred)
        return func

    return decorator
