from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, TypedDict

import asyncpg
import twitchio  # noqa: TCH002
from twitchio.ext import commands, routines

from utils.checks import is_mod

if TYPE_CHECKING:
    from bot import IrenesBot

    class TwitchCommands(TypedDict):
        streamer_id: int
        command_name: str
        content: str


class CustomCommands(commands.Cog):
    def __init__(self, bot: IrenesBot) -> None:
        self.bot: IrenesBot = bot
        self.command_cache: dict[int, dict[str, str]] = {}
        self.populate_cache.start()

    @routines.routine(iterations=1)
    async def populate_cache(self) -> None:
        query = """
            SELECT streamer_id, command_name, content
            FROM chat_commands
        """

        rows: list[TwitchCommands] = await self.bot.pool.fetch(query)
        for row in rows:
            self.command_cache.setdefault(row["streamer_id"], {})[row["command_name"]] = row["content"]

    @commands.Cog.event()  # type: ignore # one day they will fix it
    async def event_message(self, message: twitchio.Message) -> None:
        # An event inside a cog!
        if message.echo:
            return

        user = await message.channel.user()
        for k, p in itertools.product(self.command_cache.get(user.id, []), self.bot.prefixes):
            if message.content.startswith(f"{p}{k}"):  # type: ignore
                await message.channel.send(self.command_cache[user.id][k])

    async def cmd_group(self, ctx: commands.Context) -> None:
        await ctx.send("Sorry, you should use it with subcommands add, del, edit")

    # todo: do it with @commands.group when they bring it back
    cmd = commands.Group(name="cmd", func=cmd_group)

    @is_mod()
    @cmd.command()
    async def add(self, ctx: commands.Context, cmd_name: str, *, text: str) -> None:
        query = """
            INSERT INTO chat_commands
            (streamer_id, command_name, content)
            VALUES ($1, $2, $3)
        """
        user = await ctx.message.channel.user()
        try:
            await self.bot.pool.execute(query, user.id, cmd_name, text)
        except asyncpg.UniqueViolationError:
            msg = "There already exists a command with such name."
            raise commands.BadArgument(msg)
        self.command_cache.setdefault(user.id, {})[cmd_name] = text
        await ctx.send(f"Added the command {cmd_name}.")

    @is_mod()
    @cmd.command(name="del")
    async def delete(self, ctx: commands.Context, command_name: str) -> None:
        query = """
            DELETE FROM chat_commands
            WHERE streamer_id=$1 AND command_name=$2
            RETURNING command_name
        """
        user = await ctx.message.channel.user()
        val = await self.bot.pool.fetchval(query, user.id, command_name)
        if val is None:
            msg = "There is no command with such name."
            raise commands.BadArgument(msg)
        self.command_cache[user.id].pop(command_name)
        await ctx.send(f"Deleted the command {command_name}")

    @is_mod()
    @cmd.command()
    async def edit(self, ctx: commands.Context, command_name: str, *, text: str) -> None:
        query = """
            UPDATE chat_commands
            SET content=$3
            WHERE streamer_id=$1 AND command_name=$2
            RETURNING command_name
        """
        user = await ctx.message.channel.user()
        val = await self.bot.pool.fetchval(query, user.id, command_name, text)
        if val is None:
            msg = "There is no command with such name."
            raise commands.BadArgument(msg)

        self.command_cache[user.id][command_name] = text
        await ctx.send(f"Edited the command {command_name}.")

    @cmd.command(name="list")
    async def cmd_list(self, ctx: commands.Context) -> None:
        cache_list = [f"!{name}" for v in self.command_cache.values() for name in v]
        bot_cmds = [
            f"!{v.full_name}" for v in self.bot.commands.values() if not v._checks and not isinstance(v, commands.Group)
        ]
        await ctx.send(", ".join(cache_list + bot_cmds))


def prepare(bot: IrenesBot) -> None:
    bot.add_cog(CustomCommands(bot))
