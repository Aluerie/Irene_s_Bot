from __future__ import annotations

from typing import TYPE_CHECKING

from twitchio.ext import commands, eventsub

import config
from bot import IrenesCog
from utils import const

if TYPE_CHECKING:
    import twitchio

    from bot import IrenesBot


class Alerts(IrenesCog):
    # TODO: 3.0 will fix ES events so the typehint gonna be correct like this:
    # (self,  payload: eventsub.CustomRewardRedemptionAddUpdateData)
    # and we wont need this ugly first line
    # "payload: eventsub.CustomRewardRedemptionAddUpdateData = event.data  # type: ignore"
    # fix it everywhere

    # SECTION 1.
    # Channel Points beta test event (because it's the easiest event to test out)

    @commands.Cog.event(event="event_eventsub_notification_channel_reward_redeem")  # type: ignore # lib issue
    async def channel_points_redeem(self, event: eventsub.NotificationEvent) -> None:
        """Somebody redeemed a custom channel points reward."""
        payload: eventsub.CustomRewardRedemptionAddUpdateData = event.data  # type: ignore
        print(f"{payload.user.name} redeemed {payload.reward.title} for {payload.reward.cost} channel points")

    # SECTION 2
    # Helper functions

    def get_channel(self, partial_user: twitchio.PartialUser) -> twitchio.Channel:
        assert partial_user.name
        channel = self.bot.get_channel(partial_user.name)
        assert channel
        return channel

    async def get_display_name(self, partial_user: twitchio.PartialUser | None, channel: twitchio.Channel) -> str:
        if partial_user and partial_user.name:  # todo: v3 type check | can payload.user.name be None?
            chatter = channel.get_chatter(partial_user.name)
            display_name: str | None = getattr(chatter, "mention", None)
            if not display_name:
                display_name = (await partial_user.fetch()).display_name
        else:
            display_name = "Anonymous"
        return display_name

    # SECTION 3
    # Actual events

    @commands.Cog.event(event="event_eventsub_notification_followV2")  # type: ignore # lib issue
    async def follows(self, event: eventsub.NotificationEvent) -> None:
        """Somebody cheered."""
        payload: eventsub.ChannelFollowData = event.data  # type: ignore
        channel = self.get_channel(payload.broadcaster)
        display_name = await self.get_display_name(payload.user, channel)
        await channel.send(f"@{display_name} just followed")

    @commands.Cog.event(event="event_eventsub_notification_channel_goal_end")  # type: ignore # lib issue
    async def goal_end(self, event: eventsub.NotificationEvent) -> None:
        """The channel goal was achieved/failed."""
        payload: eventsub.ChannelGoalEndData = event.data  # type: ignore
        channel = self.get_channel(payload.user)

        word = "finished!" if payload.is_achieved else "just failed?"
        await channel.send(
            f"The goal for {payload.type}s just {word} {payload.description} "
            f"{payload.current_amount}/{payload.target_amount}."
        )

    @commands.Cog.event(event="event_eventsub_notification_raid")  # type: ignore # lib issue
    async def raids(self, event: eventsub.NotificationEvent) -> None:
        """Somebody raided the channel."""
        payload: eventsub.ChannelRaidData = event.data  # type: ignore
        channel = self.get_channel(payload.reciever)
        streamer = await channel.user()

        raider_display_name = await self.get_display_name(payload.raider, channel)
        raider_channel_info = await self.bot.fetch_channel(raider_display_name)

        await streamer.shoutout(config.TTG_IRENE_ACCESS_TOKEN, payload.raider.id, const.ID.Irene)
        await streamer.chat_announcement(
            config.TTG_ACCESS_TOKEN,
            const.ID.Bot,
            (
                f"@{raider_display_name} just raided us with {payload.viewer_count} viewers. "
                f'They were playing {raider_channel_info.game_name} with title "{raider_channel_info.title}".'
                f"Hey chat be nice to raiders {const.STV.donkHappy}"
            ),
        )

    @commands.Cog.event(event="event_eventsub_notification_stream_end")  # type: ignore # lib issue
    async def stream_end(self, event: eventsub.NotificationEvent) -> None:
        """Stream ended (went offline)."""
        payload: eventsub.StreamOfflineData = event.data  # type: ignore
        channel = self.get_channel(payload.broadcaster)
        await channel.send(f"Stream is now offline {const.STV.Offline}")

    @commands.Cog.event(event="event_eventsub_notification_stream_start")  # type: ignore # lib issue
    async def stream_start(self, event: eventsub.NotificationEvent) -> None:
        """Stream started (went live)."""
        payload: eventsub.StreamOnlineData = event.data  # type: ignore
        channel = self.get_channel(payload.broadcaster)
        channel_info = await self.bot.fetch_channel(channel.name)
        await channel.send(
            f"Stream just started {const.STV.FeelsBingMan} "
            f"Game: {channel_info.game_name} | Title: {channel_info.title}"
        )

    @commands.Cog.event(event="event_eventsub_notification_channel_ad_break_begin")  # type: ignore # lib issue
    async def ad_break(self, event: eventsub.NotificationEvent) -> None:
        """Ad break."""
        payload: eventsub.ChannelAdBreakBeginData = event.data  # type: ignore
        channel = self.get_channel(payload.broadcaster)
        word = "automatic" if payload.is_automatic else "manual"
        await channel.send(f"{payload.duration} secs {word} ad break is starting.")


# f"{payload.duration} sec ad break is starting.
def prepare(bot: IrenesBot) -> None:
    bot.add_cog(Alerts(bot))