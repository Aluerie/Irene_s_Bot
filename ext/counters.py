from __future__ import annotations

import asyncio
import datetime
import random
import re
from typing import TYPE_CHECKING, TypedDict

from twitchio.ext import commands, eventsub

from bot import IrenesCog
from utils import const, formats

if TYPE_CHECKING:
    import twitchio

    from bot import IrenesBot

    class FirstRedeemsRow(TypedDict):
        user_name: str
        first_times: int


class Counters(IrenesCog):
    def __init__(self, bot: IrenesBot) -> None:
        super().__init__(bot)
        self.last_erm_notification: datetime.datetime = datetime.datetime.now(datetime.UTC)

    # ERM COUNTERS

    @commands.Cog.event(event="event_message")  # type: ignore # one day they will fix it
    async def erm_counter(self, message: twitchio.Message) -> None:
        """Erm Counter"""
        if message.echo or not message.content or message.author.name in const.Bots:
            return
        if message.channel.name != const.Name.Irene:
            return
        if not re.search(r"\bErm\b", message.content):
            return

        query = """--sql
            UPDATE counters
            SET value = value + 1
            where name = $1
            RETURNING value;
        """
        value: int = await self.bot.pool.fetchval(query, "erm")

        # milestone
        if value % 1000 == 0:
            await message.channel.send(f"{const.STV.wow} we reached a milestone of {value} {const.STV.Erm} in chat")
            return

        # random notification/reminder
        now = datetime.datetime.now(datetime.UTC)
        if random.randint(0, 150) < 2 and (now - self.last_erm_notification).seconds > 180:
            await asyncio.sleep(3)
            query = "SELECT value FROM counters WHERE name = $1"
            value: int = await self.bot.pool.fetchval(query, "erm")
            await message.channel.send(f"{value} {const.STV.Erm} in chat.")
            return

    @commands.command(aliases=["erm"])
    async def erms(self, ctx: commands.Context) -> None:
        """Get an erm_counter value"""
        query = "SELECT value FROM counters WHERE name = $1"
        value: int = await self.bot.pool.fetchval(query, "erm")
        await ctx.send(f"{value} {const.STV.Erm} in chat.")

    # FIRST COUNTER

    @commands.Cog.event(event="event_eventsub_notification_channel_reward_redeem")  # type: ignore # lib issue
    async def first_counter(self, event: eventsub.NotificationEvent) -> None:
        """Count all redeems for the reward 'First'"""
        payload: eventsub.CustomRewardRedemptionAddUpdateData = event.data  # type: ignore

        if payload.reward.title != "First!" or payload.broadcaster.id != const.ID.Irene:
            # Secure Irene channel and that it is exactly "First!" redeem
            # a bit scary since I can rename it one day and then we lose the feature but not sure if there is a better way
            # todo: create a routine checking if we have a channel point reward named First as a future fool-proof thing
            return

        query = """--sql
            INSERT INTO first_redeems (user_id, user_name)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO
                UPDATE SET first_times = first_redeems.first_times + 1, user_name = $2
            RETURNING first_times;
        """
        count: int = await self.bot.pool.fetchval(query, payload.user.id, str(payload.user.name))
        print(count)
        channel = self.get_channel(payload.broadcaster)
        user_display_name = await self.get_display_name(payload.user, channel)

        if count == 1:
            msg = f'@{user_display_name}, gratz on your very first "First!" {const.STV.gg}'
        else:
            msg = f"@{user_display_name}, Gratz! you've been first {count} times {const.STV.gg} {const.Global.EZ}"
        await channel.send(msg)

    @commands.command(aliases=["first"])
    async def firsts(self, ctx: commands.Context) -> None:
        """Get top10 first redeemers"""
        query = """--sql
            SELECT user_name, first_times
            FROM first_redeems
            ORDER BY first_times DESC
            LIMIT 3;
        """
        rows: list[FirstRedeemsRow] = await self.bot.pool.fetch(query)
        content = f'Top3 "First!" redeemers {const.STV.DankG} '

        rank_medals = [
            "\N{FIRST PLACE MEDAL}",
            "\N{SECOND PLACE MEDAL}",
            "\N{THIRD PLACE MEDAL}",
        ]  # + const.DIGITS[4:10]
        content += " ".join(
            [
                f"{rank_medals[i]} {row['user_name']}: {formats.plural(row['first_times']):time};"
                for i, row in enumerate(rows)
            ]
        )
        await ctx.send(content)

    @commands.command()
    async def test_digits(self, ctx: commands.Context) -> None:
        # todo: check with this command if these emotes are fixed in web twitch chat (ffz and 7tv addons)
        content = " ".join(const.DIGITS)
        await ctx.send(content)


def prepare(bot: IrenesBot) -> None:
    bot.add_cog(Counters(bot))
