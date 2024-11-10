from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from twitchio.ext import commands

from utils import const

if TYPE_CHECKING:
    import twitchio

    from ..bot import IrenesBot


__all__ = ("IrenesComponent",)

log = logging.getLogger("alerts")
log.setLevel(logging.INFO)  # DEBUG


class IrenesComponent(commands.Component):
    """Base component to use with IrenesBot."""

    def __init__(self, bot: IrenesBot) -> None:
        self.bot: IrenesBot = bot

    @property
    def irene(self) -> twitchio.PartialUser:
        """Get Irene's channel from the cache."""
        return self.bot.create_partialuser(const.UserID.Irene)

    async def deliver(self, content: str) -> None:
        await self.irene.send_message(
            sender=self.bot.bot_id,
            message=content,
        )

    # # Helper functions
    # TODO: they might be obsolete with 3.0

    # def get_channel(self, partial_user: twitchio.PartialUser) -> twitchio.Channel:
    #     """Helper function to get a channel from cache by partial_user."""
    #     assert partial_user.name
    #     channel = self.bot.get_channel(partial_user.name)
    #     assert channel
    #     return channel

    # async def get_display_name(self, partial_user: twitchio.PartialUser | None, channel: twitchio.Channel) -> str:
    #     """Helper function to get display name for partial user.

    #     For some reason it's not that easy!

    #     Parameters
    #     ----------
    #     partial_user
    #         Partial user for the person (chatter) to get `display_name` of
    #     channel
    #         The channel we are in.

    #     """
    #     if partial_user is None:
    #         return "Anonymous"

    #     if partial_user.name is not None:  # todo: v3 type check | can payload.user.name be None?
    #         chatter = channel.get_chatter(partial_user.name)
    #         display_name: str | None = getattr(chatter, "display_name", None)
    #         if display_name is not None:
    #             return display_name

    #     user = await partial_user.fetch()
    #     # log.debug(user)
    #     return user.display_name
