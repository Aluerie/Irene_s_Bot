from __future__ import annotations

from typing import TYPE_CHECKING

import config
from bot import IrenesCog
from utils import const

if TYPE_CHECKING:
    from bot import IrenesBot


class EventSubSubscriptions(IrenesCog):
    def __init__(self, bot: IrenesBot) -> None:
        super().__init__(bot)
        self.bot.loop.create_task(self.subscribe_to_events())

    async def subscribe_to_events(self) -> None:
        broadcaster = const.ID.Irene
        token = config.TTG_IRENE_ACCESS_TOKEN
        # moderator = const.BOT_TWITCH_ID

        # https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types
        # todo: currently I just have power-hungry token for irene that has all tokens
        # and token with chat: read/edit for the bot
        # we can narrow it down to only what we need.

        # the order here is alphabetic or more like same as
        # https://twitchio.dev/en/latest/exts/eventsub.html#twitchio.ext.eventsub.EventSubClient
        # Other Important convient links:
        # https://twitchio.dev/en/latest/exts/eventsub.html#event-reference
        # https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/

        # Ad break begin                        channel:read:ads
        # await self.bot.eventsub.subscribe_channel_ad_break_begin(broadcaster, token)
        # Follows                               moderator:read:followers
        await self.bot.eventsub.subscribe_channel_follows_v2(broadcaster, broadcaster, token)
        # Goal End                              channel:read:goals
        await self.bot.eventsub.subscribe_channel_goal_end(broadcaster, token)
        # Channel Points Redeem                 channel:read:redemptions or channel:manage:redemptions
        await self.bot.eventsub.subscribe_channel_points_redeemed(broadcaster, token)
        # Raids to the channel                  No authorization required
        await self.bot.eventsub.subscribe_channel_raid(token, to_broadcaster=broadcaster)
        # Stream went offline                   No authorization required
        await self.bot.eventsub.subscribe_channel_stream_end(broadcaster, token)
        # Stream went live                      No authorization required
        await self.bot.eventsub.subscribe_channel_stream_start(broadcaster, token)
        # Channel Update (title/game)           No authorization required
        await self.bot.eventsub.subscribe_channel_update(broadcaster, token)


def prepare(bot: IrenesBot) -> None:
    bot.add_cog(EventSubSubscriptions(bot))
