from __future__ import annotations

from typing import TYPE_CHECKING

from twitchio.ext import commands, eventsub

import config
from bot import IrenesCog
from utils import const

if TYPE_CHECKING:
    from bot import IrenesBot


class UnusedAlerts(IrenesCog):
    """Unused alerts.

    Most are indeed pointless since they are already handled by native twitch.tv "system"-messages.
    """

    def __init__(self, bot: IrenesBot) -> None:
        super().__init__(bot)
        self.bot.loop.create_task(self.subscribe_to_events())

    async def subscribe_to_events(self) -> None:
        """Create eventsub subscriptions."""
        broadcaster = const.ID.Irene
        token = config.TTG_IRENE_ACCESS_TOKEN

        # Charity                               channel:read:charity
        await self.bot.eventsub.subscribe_channel_charity_donate(broadcaster, token)
        # Cheers                                bits:read
        await self.bot.eventsub.subscribe_channel_cheers(broadcaster, token)
        # Sub gifts                             channel:read:subscriptions
        await self.bot.eventsub.subscribe_channel_subscription_gifts(broadcaster, token)
        # Sub messages (when re-sub)             channel:read:subscriptions
        await self.bot.eventsub.subscribe_channel_subscription_messages(broadcaster, token)
        # Subs                                  channel:read:subscriptions
        await self.bot.eventsub.subscribe_channel_subscriptions(broadcaster, token)

    @commands.Cog.event(event="event_eventsub_notification_channel_charity_donate")  # type: ignore # lib issue
    async def charity_donate(self, event: eventsub.NotificationEvent) -> None:
        """Somebody donated to on-going charity event."""
        payload: eventsub.ChannelCharityDonationData = event.data  # type: ignore
        channel = self.get_channel(payload.broadcaster)
        display_name = await self.get_display_name(payload.user, channel)
        await channel.send(
            f"@{display_name} just donated {payload.donation_value} {payload.donation_currency} "
            f'to charity "{payload.charity_name}"'
        )

    @commands.Cog.event(event="event_eventsub_notification_cheer")  # type: ignore # lib issue
    async def cheer(self, event: eventsub.NotificationEvent) -> None:
        """Somebody cheered."""
        payload: eventsub.ChannelCheerData = event.data  # type: ignore
        channel = self.get_channel(payload.broadcaster)
        display_name = await self.get_display_name(payload.user, channel)
        await channel.send(f'@{display_name} just cheered {payload.bits} bits: "{payload.message}"')

    @commands.Cog.event(event="event_eventsub_notification_subscription_gift")  # type: ignore # lib issue
    async def sub_gift(self, event: eventsub.NotificationEvent) -> None:
        """Somebody gifted subscriptions to the channel."""
        payload: eventsub.ChannelSubscriptionGiftData = event.data  # type: ignore
        channel = self.get_channel(payload.broadcaster)  # type: ignore
        display_name = await self.get_display_name(payload.user, channel)
        await channel.send(f"@{display_name} gifted {payload.total} subs")

    @commands.Cog.event(event="event_eventsub_notification_subscription_message")  # type: ignore # lib issue
    async def re_sub_message(self, event: eventsub.NotificationEvent) -> None:
        """Somebody re-subscribed to the channel with a message."""
        payload: eventsub.ChannelSubscriptionMessageData = event.data  # type: ignore
        channel = self.get_channel(payload.broadcaster)
        display_name = await self.get_display_name(payload.user, channel)
        await channel.send(
            f'@{display_name} subscribed for {payload.streak} months with Tier {payload.tier}: "{payload.message}"'
        )

    @commands.Cog.event(event="event_eventsub_notification_subscription")  # type: ignore # lib issue
    async def subs(self, event: eventsub.NotificationEvent) -> None:
        """Somebody subscribed to the channel."""
        # prime tier will be "prime" btw. Actual tier 1/2/3 are 1000/2000/3000
        payload: eventsub.ChannelSubscribeData = event.data  # type: ignore
        channel = self.get_channel(payload.broadcaster)
        display_name = await self.get_display_name(payload.user, channel)
        if payload.is_gift:
            await channel.send(f"@{display_name} was gifted Tier {payload.tier} sub")
        else:
            await channel.send(f"@{display_name} subscribed with Tier {payload.tier}")


def prepare(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    bot.add_cog(UnusedAlerts(bot))
