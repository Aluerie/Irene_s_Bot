from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, TypedDict

import twitchio
from twitchio.ext import commands, routines

from utils.const import ALUERIE_TWITCH_ID
from utils.database import DRecord

if TYPE_CHECKING:
    from utils.bot import AlueBot

    class TwitchCommands(DRecord):
        user_id: int
        cmd_name: str
        cmd_text: str


def is_mod():
    async def pred(ctx: commands.Context) -> bool:
        if ctx.message.author.is_mod:
            return True
        else:
            raise commands.CheckFailure("Only moderators can use this command")

    def decorator(func: commands.Command):
        func._checks.append(pred)
        return func

    return decorator


class CustomCommands(commands.Cog):
    def __init__(self, bot: AlueBot):
        self.bot: AlueBot = bot
        self.cmd_cache: Dict[int, Dict[str, str]] = dict()
        self.populate_cache.start()

    @routines.routine(iterations=1)
    async def populate_cache(self):
        query = """ SELECT user_id, cmd_name, cmd_text
                    FROM twitch_commands
                    WHERE user_id=$1
                """

        rows: List[TwitchCommands] = await self.bot.pool.fetch(query, ALUERIE_TWITCH_ID)
        for row in rows:
            self.cmd_cache[row.user_id][row.cmd_name] = row.cmd_text

    @commands.Cog.event()
    async def event_message(self, message: twitchio.Message):
        # An event inside a cog!
        if message.echo:
            return

        user = await message.channel.user()
        for k, p in zip(self.cmd_cache[user.id], self.bot.prefixes):
            if message.content.startswith(f"{p}{k}"):  # type: ignore
                await message.channel.send(self.cmd_cache[user.id][k])

    async def cmd_group(self, ctx: commands.Context):
        await ctx.send(f"Sorry, you should use it with subcommands add, del, edit")

    # todo: do it with @commands.group when they bring it back
    cmd = commands.Group(name="cmd", func=cmd_group)

    @is_mod()
    @cmd.command()
    async def add(self, ctx: commands.Context, cmd_name: str, *, text: str):
        query = """ INSERT INTO twitch_commands 
                        (user_id, cmd_name, cmd_text)
                        VALUES ($1, $2, $3)
                        ??????????????????????????????
                        ON CONFLICT DO 
                            INSERT INTO twitch_streamers
                            (user_id, user_name)
                            VALUES ($1, $4)
                """
        user = await ctx.message.channel.user()
        await self.bot.pool.execute(query, user.id, cmd_name, text, user.name)
        self.cmd_cache[user.id][cmd_name] = text
        await ctx.send(f"Added the command {cmd_name}.")

    @is_mod()
    @cmd.command(name="del")
    async def delete(self, ctx: commands.Context, cmd_name: str):
        query = """ DELETE FROM twitch_commands 
                    WHERE user_id=$1 AND cmd_name=$2
                """
        user = await ctx.message.channel.user()
        await self.bot.pool.execute(query, user.id, cmd_name)
        self.cmd_cache[user.id].pop(cmd_name)
        await ctx.send(f"Deleted the command {cmd_name}")

    @is_mod()
    @cmd.command()
    async def edit(self, ctx: commands.Context, cmd_name: str, *, text: str):
        query = """ UPDATE twitch_commands 
                    SET cmd_text=$3
                    WHERE user_id=$1 AND cmd_name=$2
                """
        user = await ctx.message.channel.user()
        await self.bot.pool.execute(query, user.id, cmd_name, text)
        self.cmd_cache[user.id][cmd_name] = text
        await ctx.send(f"Edited the command {cmd_name}.")

    @cmd.command(name="list")
    async def cmd_list(self, ctx: commands.Context):
        cache_list = [f"!{k}" for k in self.cmd_cache]
        bot_cmds = [
            f"!{v.full_name}"
            for k, v in self.bot.commands.items()
            if not v._checks and not isinstance(v, commands.Group)
        ]
        await ctx.send(", ".join(cache_list + bot_cmds))


def prepare(bot: AlueBot):
    bot.add_cog(CustomCommands(bot))
