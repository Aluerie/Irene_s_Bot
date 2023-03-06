from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

import asyncpg
import twitchio
from twitchio.ext import commands, routines

from utils.checks import is_mod

if TYPE_CHECKING:
    from utils.bot import AlueBot
    from utils.database import DRecord

    class TwitchCommands(DRecord):
        user_id: int
        cmd_name: str
        cmd_text: str


class CustomCommands(commands.Cog):
    def __init__(self, bot: AlueBot):
        self.bot: AlueBot = bot
        self.cmd_cache: Dict[int, Dict[str, str]] = dict()
        self.populate_cache.start()

    @routines.routine(iterations=1)
    async def populate_cache(self):
        query = """ SELECT user_id, cmd_name, cmd_text
                    FROM twitch_commands
                """

        rows: List[TwitchCommands] = await self.bot.pool.fetch(query)
        for row in rows:
            self.cmd_cache.setdefault(row.user_id, {})[row.cmd_name] = row.cmd_text

    @commands.Cog.event()
    async def event_message(self, message: twitchio.Message):
        # An event inside a cog!
        if message.echo:
            return

        user = await message.channel.user()
        for k, p in zip(self.cmd_cache.get(user.id, []), self.bot.prefixes):
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
                """
        user = await ctx.message.channel.user()
        try: 
            await self.bot.pool.execute(query, user.id, cmd_name, text)
        except asyncpg.UniqueViolationError:
            raise commands.BadArgument('There already exists a command with such name.')
        self.cmd_cache.setdefault(user.id, {})[cmd_name] = text
        await ctx.send(f"Added the command {cmd_name}.")

    @is_mod()
    @cmd.command(name="del")
    async def delete(self, ctx: commands.Context, cmd_name: str):
        query = """ DELETE FROM twitch_commands 
                    WHERE user_id=$1 AND cmd_name=$2
                    RETURNING cmd_name
                """
        user = await ctx.message.channel.user()
        val = await self.bot.pool.fetchval(query, user.id, cmd_name)
        if val is None:
            raise commands.BadArgument('There is no command with such name.')
        self.cmd_cache[user.id].pop(cmd_name)
        await ctx.send(f"Deleted the command {cmd_name}")

    @is_mod()
    @cmd.command()
    async def edit(self, ctx: commands.Context, cmd_name: str, *, text: str):
        query = """ UPDATE twitch_commands 
                    SET cmd_text=$3
                    WHERE user_id=$1 AND cmd_name=$2
                    RETURNING cmd_name
                """
        user = await ctx.message.channel.user()
        val = await self.bot.pool.fetchval(query, user.id, cmd_name, text)
        if val is None:
            raise commands.BadArgument('There is no command with such name.')
        
        self.cmd_cache[user.id][cmd_name] = text
        await ctx.send(f"Edited the command {cmd_name}.")

    @cmd.command(name="list")
    async def cmd_list(self, ctx: commands.Context):
        cache_list = [f"!{name}" for _k, v in self.cmd_cache.items() for name in v]
        bot_cmds = [
            f"!{v.full_name}"
            for _k, v in self.bot.commands.items()
            if not v._checks and not isinstance(v, commands.Group)
        ]
        await ctx.send(", ".join(cache_list + bot_cmds))


def prepare(bot: AlueBot):
    bot.add_cog(CustomCommands(bot))
