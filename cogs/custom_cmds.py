from __future__ import annotations

from typing import TYPE_CHECKING, List

import twitchio
from twitchio.ext import commands, routines

from utils.database import DRecord

if TYPE_CHECKING:
    from utils.bot import AlueBot


class TwitchCommands(DRecord):
    command_name: str
    command_text: str


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
        self.cmd_cache: dict = dict()
        self.populate_cache.start()

    @routines.routine(iterations=1)
    async def populate_cache(self):
        query = """ SELECT command_name, command_text
                    FROM twitch_commands
                    WHERE streamer_id=$1
                """
        # one day if we introduce the bot to public we will need some refactoring around it
        # cmd_cache will need to be different type
        ALUERIE_TWITCH_ID = 180499648
        rows: List[TwitchCommands] = await self.bot.pool.fetch(query, ALUERIE_TWITCH_ID)
        for row in rows:
            self.cmd_cache[row.command_name] = row.command_text

    @commands.Cog.event()
    async def event_message(self, message: twitchio.Message):
        # An event inside a cog!
        if message.echo:
            return

        for k, p in zip(self.cmd_cache, self.bot.prefixes):
            if message.content.startswith(f"{p}{k}"):
                await message.channel.send(self.cmd_cache[k])

    async def cmd_group(self, ctx: commands.Context):
        await ctx.send(f"Sorry, you should use it with subcommands add, del, edit")

    # todo: do it with @commands.group when they bring it back
    cmd = commands.Group(name="cmd", func=cmd_group)

    @is_mod()
    @cmd.command()
    async def add(self, ctx: commands.Context, cmd_name: str, *, text: str):
        query = """ INSERT INTO twitch_commands (streamer_id, command_name, command_text)
                    VALUES ($1, $2, $3)
                """
        stream_user = await ctx.message.channel.user()
        await self.bot.pool.execute(query, stream_user.id, cmd_name, text)
        self.cmd_cache[cmd_name] = text
        await ctx.send(f"Added the command {cmd_name}.")

    @is_mod()
    @cmd.command(name="del")
    async def delete(self, ctx: commands.Context, cmd_name: str):
        query = """ DELETE FROM twitch_commands 
                    WHERE streamer_id=$1 AND command_name=$2
                """
        stream_user = await ctx.message.channel.user()
        await self.bot.pool.execute(query, stream_user.id, cmd_name)
        self.cmd_cache.pop(cmd_name)
        await ctx.send(f"Deleted the command {cmd_name}")

    @is_mod()
    @cmd.command()
    async def edit(self, ctx: commands.Context, cmd_name: str, *, text: str):
        query = """ UPDATE twitch_commands 
                    SET command_text=$3
                    WHERE streamer_id=$1 AND command_name=$2
                """
        stream_user = await ctx.message.channel.user()
        await self.bot.pool.execute(query, stream_user.id, cmd_name, text)
        self.cmd_cache[cmd_name] = text
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
