from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, Dict, List

import asyncpg
import twitchio
from twitchio.ext import commands, routines

from utils.checks import is_mod

if TYPE_CHECKING:
    from utils.bot import LueByt
    from utils.database import DRecord

    class TwitchCommands(DRecord):
        streamer_id: int
        command_name: str
        content: str


class CustomCommands(commands.Cog):
    def __init__(self, bot: LueByt):
        self.bot: LueByt = bot
        self.command_cache: Dict[int, Dict[str, str]] = dict()
        self.populate_cache.start()

    @routines.routine(iterations=1)
    async def populate_cache(self):
        query = """ SELECT streamer_id, command_name, content
                    FROM chat_commands
                """

        rows: List[TwitchCommands] = await self.bot.pool.fetch(query)
        for row in rows:
            self.command_cache.setdefault(row.streamer_id, {})[row.command_name] = row.content

    @commands.Cog.event()  # type: ignore # one day they will fix it
    async def event_message(self, message: twitchio.Message):
        # An event inside a cog!
        if message.echo:
            return

        user = await message.channel.user()
        for k, p in itertools.product(self.command_cache.get(user.id, []), self.bot.prefixes):
            if message.content.startswith(f"{p}{k}"):  # type: ignore
                await message.channel.send(self.command_cache[user.id][k])

    async def cmd_group(self, ctx: commands.Context):
        await ctx.send(f"Sorry, you should use it with subcommands add, del, edit")

    # todo: do it with @commands.group when they bring it back
    cmd = commands.Group(name="cmd", func=cmd_group)

    @is_mod()
    @cmd.command()
    async def add(self, ctx: commands.Context, cmd_name: str, *, text: str):
        query = """ INSERT INTO chat_commands
                        (streamer_id, command_name, content)
                        VALUES ($1, $2, $3)
                """
        user = await ctx.message.channel.user()
        try:
            await self.bot.pool.execute(query, user.id, cmd_name, text)
        except asyncpg.UniqueViolationError:
            raise commands.BadArgument("There already exists a command with such name.")
        self.command_cache.setdefault(user.id, {})[cmd_name] = text
        await ctx.send(f"Added the command {cmd_name}.")

    @is_mod()
    @cmd.command(name="del")
    async def delete(self, ctx: commands.Context, command_name: str):
        query = """ DELETE FROM chat_commands
                    WHERE streamer_id=$1 AND command_name=$2
                    RETURNING command_name
                """
        user = await ctx.message.channel.user()
        val = await self.bot.pool.fetchval(query, user.id, command_name)
        if val is None:
            raise commands.BadArgument("There is no command with such name.")
        self.command_cache[user.id].pop(command_name)
        await ctx.send(f"Deleted the command {command_name}")

    @is_mod()
    @cmd.command()
    async def edit(self, ctx: commands.Context, command_name: str, *, text: str):
        query = """ UPDATE chat_commands
                    SET content=$3
                    WHERE streamer_id=$1 AND command_name=$2
                    RETURNING command_name
                """
        user = await ctx.message.channel.user()
        val = await self.bot.pool.fetchval(query, user.id, command_name, text)
        if val is None:
            raise commands.BadArgument("There is no command with such name.")

        self.command_cache[user.id][command_name] = text
        await ctx.send(f"Edited the command {command_name}.")

    @cmd.command(name="list")
    async def cmd_list(self, ctx: commands.Context):
        cache_list = [f"!{name}" for v in self.command_cache.values() for name in v]
        bot_cmds = [
            f"!{v.full_name}" for v in self.bot.commands.values() if not v._checks and not isinstance(v, commands.Group)
        ]
        await ctx.send(", ".join(cache_list + bot_cmds))


def prepare(bot: LueByt):
    bot.add_cog(CustomCommands(bot))
