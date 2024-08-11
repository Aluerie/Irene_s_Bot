from __future__ import annotations

import asyncio
import datetime
import random
import re
from typing import TYPE_CHECKING

from twitchio.ext import commands

from bot import IrenesCog
from utils import const

if TYPE_CHECKING:
    import twitchio

    from bot import IrenesBot


class Counters(IrenesCog):
    def __init__(self, bot: IrenesBot) -> None:
        super().__init__(bot)
        self.last_erm_notification: datetime.datetime = datetime.datetime.now(datetime.UTC)

    @commands.Cog.event(event="event_message")  # type: ignore # one day they will fix it
    async def erm_counter(self, message: twitchio.Message) -> None:
        """Erm Counter"""
        if message.echo or not message.content or message.author.name in const.Bots:
            return

        if re.search(r"\b" + re.escape("Erm") + r"\b", message.content):
            query = "UPDATE counters SET value = value + 1 where name = $1"
            value: int = await self.bot.pool.fetchval(query, "erm")

            now = datetime.datetime.now(datetime.UTC)
            if random.randint(0, 100) < 2 and (now - self.last_erm_notification).seconds > 180:
                await asyncio.sleep(3)
                query = "SELECT value FROM counters WHERE name = $1"
                value: int = await self.bot.pool.fetchval(query, "erm")
                await self.irene_channel().send(f"{value} Erm in chat.")


def prepare(bot: IrenesBot) -> None:
    bot.add_cog(Counters(bot))
