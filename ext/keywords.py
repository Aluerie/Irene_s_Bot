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
        """Schema for `self.keywords` elements."""

        aliases: list[str]
        response: str
        dt: datetime.datetime


class Keywords(IrenesCog):
    """React to specific key word / key phrases with bot's own messages.

    Mostly used to make a small feeling of a crowd - something like many users are Pog-ing.
    """

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
        """Sends a flavour message if a keyword/key phrase was spotted in the chat."""
        if message.echo or not message.content or random.randint(1, 100) > 5:
            return

        now = datetime.datetime.now(datetime.UTC)
        for keyword in self.keywords:
            for word in keyword["aliases"]:
                if re.search(r"\b" + re.escape(word) + r"\b", message.content) and (now - keyword["dt"]).seconds > 600:
                    await message.channel.send(keyword["response"])
                    keyword["dt"] = now


def prepare(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    bot.add_cog(Keywords(bot))
