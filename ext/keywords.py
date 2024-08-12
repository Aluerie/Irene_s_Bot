from __future__ import annotations

import datetime
import random
import re
from typing import TYPE_CHECKING, TypedDict

from twitchio.ext import commands

from bot import IrenesCog

if TYPE_CHECKING:
    import twitchio

    from bot import IrenesBot

    class KeywordDict(TypedDict):
        aliases: list[str]
        response: str
        dt: datetime.datetime


class Keywords(IrenesCog):
    def __init__(self, bot: IrenesBot) -> None:
        super().__init__(bot)
        self.keywords: list[KeywordDict] = [
            {
                "aliases": aliases,
                "response": response,
                "dt": datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=1),
            }
            for aliases, response in [
                (["Pog", "PogU"], "Pog"),
                (["gg"], "gg"),
                (["GG"], "GG"),
                (
                    ["Pepoga"],
                    "Pepoga 📣 AAAIIIIIIIIIREEEEEEEEEEEEEEEENEE !",
                ),  # # cSpell: ignore AAAIIIIIIIIIREEEEEEEEEEEEEEEENEE
            ]
        ]

    @commands.Cog.event(event="event_message")  # type: ignore # lib issue
    async def keywords_response(self, message: twitchio.Message) -> None:
        if message.echo or not message.content or random.randint(1, 100) > 5:
            return

        now = datetime.datetime.now(datetime.UTC)
        for keyword in self.keywords:
            for word in keyword["aliases"]:
                if re.search(r"\b" + re.escape(word) + r"\b", message.content) and (now - keyword["dt"]).seconds > 600:
                    await message.channel.send(keyword["response"])
                    keyword["dt"] = now


def prepare(bot: IrenesBot) -> None:
    bot.add_cog(Keywords(bot))
