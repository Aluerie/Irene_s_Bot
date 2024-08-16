import logging

import twitchio
from twitchio.ext import commands

from utils import const

from ..bot import IrenesBot

__all__ = ("IrenesCog",)

log = logging.getLogger("alerts")
log.setLevel(logging.INFO)  # DEBUG


class IrenesCog(commands.Cog):
    def __init__(self, bot: IrenesBot) -> None:
        self.bot: IrenesBot = bot

    # @property
    def irene_channel(self) -> twitchio.Channel:
        """Get Irene's channel from the cache"""
        channel_name = const.Name.Irene
        channel = self.bot.get_channel(channel_name)
        if channel:
            return channel
        else:
            msg = f"Channel name={channel_name} not in cache"
            raise RuntimeError(msg)

    # Helper functions

    def get_channel(self, partial_user: twitchio.PartialUser) -> twitchio.Channel:
        assert partial_user.name
        channel = self.bot.get_channel(partial_user.name)
        assert channel
        return channel

    async def get_display_name(self, partial_user: twitchio.PartialUser | None, channel: twitchio.Channel) -> str:
        """Get partial user display name

        For some reason it's not that easy!
        """
        if partial_user is None:
            return "Anonymous"

        # log.debug(partial_user)
        if partial_user.name is not None:  # todo: v3 type check | can payload.user.name be None?
            chatter = channel.get_chatter(partial_user.name)
            # log.debug(chatter)
            display_name: str | None = getattr(chatter, "display_name", None)
            # log.debug("%s, and is it truly None? %s", display_name, "yes" if display_name is None else "no")
            if display_name is not None:
                return display_name

        user = await partial_user.fetch()
        # log.debug(user)
        return user.display_name
