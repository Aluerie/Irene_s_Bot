import logging

import twitchio
from twitchio.ext import commands

from utils import const

from ..bot import IrenesBot

__all__ = ("IrenesCog",)

log = logging.getLogger("alerts")
log.setLevel(logging.INFO)  # DEBUG


class IrenesCog(commands.Cog):
    """Base cog to use with IrenesBot."""

    def __init__(self, bot: IrenesBot) -> None:
        self.bot: IrenesBot = bot

    # @property
    def irene_channel(self) -> twitchio.Channel:
        """Get Irene's channel from the cache."""
        channel_name = const.Name.Irene
        channel = self.bot.get_channel(channel_name)
        if channel:
            return channel
        else:
            msg = f"Channel name={channel_name} not in cache"
            raise RuntimeError(msg)

    # Helper functions

    def get_channel(self, partial_user: twitchio.PartialUser) -> twitchio.Channel:
        """Helper function to get a channel from cache by partial_user."""
        assert partial_user.name
        channel = self.bot.get_channel(partial_user.name)
        assert channel
        return channel

    async def get_display_name(self, partial_user: twitchio.PartialUser | None, channel: twitchio.Channel) -> str:
        """Helper function to get display name for partial user.

        For some reason it's not that easy!

        Parameters
        ----------
        partial_user
            Partial user for the person (chatter) to get `display_name` of
        channel
            The channel we are in.

        """
        if partial_user is None:
            return "Anonymous"

        if partial_user.name is not None:  # todo: v3 type check | can payload.user.name be None?
            chatter = channel.get_chatter(partial_user.name)
            display_name: str | None = getattr(chatter, "display_name", None)
            if display_name is not None:
                return display_name

        user = await partial_user.fetch()
        # log.debug(user)
        return user.display_name
