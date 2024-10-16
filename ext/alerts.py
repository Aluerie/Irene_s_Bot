from __future__ import annotations

import asyncio
import logging
import random
from typing import TYPE_CHECKING

from twitchio.ext import commands, eventsub

import config
from bot import IrenesCog
from utils import const, formats

if TYPE_CHECKING:
    import twitchio

    from bot import IrenesBot

log = logging.getLogger("alerts")


class Alerts(IrenesCog):
    """Twitch Chat Alerts.

    Mostly, EventSub events that are nice to have a notification in twitch chat for.
    """

    # TODO: 3.0 will fix ES events so the typehint gonna be correct like this:
    # (self,  payload: eventsub.CustomRewardRedemptionAddUpdateData)
    # and we wont need this ugly first line
    # "payload: eventsub.CustomRewardRedemptionAddUpdateData = event.data  # type: ignore"
    # fix it everywhere

    def __init__(self, bot: IrenesBot) -> None:
        super().__init__(bot)
        self.ban_list: set[str] = set()

    # SECTION 1.
    # Channel Points beta test event (because it's the easiest event to test out)

    @commands.Cog.event(event="event_eventsub_notification_channel_reward_redeem")  # type: ignore # lib issue
    async def channel_points_redeem(self, event: eventsub.NotificationEvent) -> None:
        """Somebody redeemed a custom channel points reward."""
        payload: eventsub.CustomRewardRedemptionAddUpdateData = event.data  # type: ignore
        # just testing
        print(f"{payload.user.name} redeemed {payload.reward.title} for {payload.reward.cost} channel points")

    # SECTION 2
    # Actual events

    @commands.Cog.event(event="event_eventsub_notification_followV2")  # type: ignore # lib issue
    async def follows(self, event: eventsub.NotificationEvent) -> None:
        """Somebody cheered."""
        payload: eventsub.ChannelFollowData = event.data  # type: ignore
        channel = self.get_channel(payload.broadcaster)

        display_name = await self.get_display_name(payload.user, channel)
        random_phrase = random.choice(
            [
                "welcome in",
                "I appreciate it",
                "enjoy your stay",
                "nice to see you",
                "enjoy the show",
            ]
        )
        emotes: list[str] = [
            const.STV.donkHappy,
            const.BTTV.PogU,
            const.STV.dankHey,
            const.STV.donkHey,
            const.BTTV.peepoHey,
            const.STV.Hey,
        ]
        random_emote = random.choice(emotes)
        await channel.send(f"@{display_name} just followed! Thanks, {random_phrase} {random_emote}")

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
                f'They were playing {raider_channel_info.game_name} with title "{raider_channel_info.title}". '
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
        # word = "automatic" if payload.is_automatic else "manual"
        human_delta = formats.timedelta_to_words(seconds=payload.duration, fmt=formats.TimeDeltaFormat.Short)
        await channel.send(f"{human_delta} ad starting {const.STV.peepoAd}")

        # this is pointless probably
        # await asyncio.sleep(payload.duration)
        # await channel.send("TAd break is over")

    @commands.Cog.event(event="event_eventsub_notification_ban")  # type: ignore # lib issue
    async def bans_timeouts(self, event: eventsub.NotificationEvent) -> None:
        """Bans."""
        payload: eventsub.ChannelBanData = event.data  # type: ignore
        assert payload.user.name
        self.ban_list.add(payload.user.name.lower())

    @commands.Cog.event(event="event_message")  # type: ignore # lib issue
    async def first_message(self, message: twitchio.Message) -> None:
        """Greet first time chatters with FirstTimeChadder treatment.

        This functions filters out spam-bots that should be perma-banned right away by other features or other bots.
        """
        if not message.first or not message.content:
            return

        if not isinstance(message.author.name, str):
            # some twitchio type bs uncertainty
            return

        await asyncio.sleep(3.3)
        if message.author.name.lower() not in self.ban_list:
            await message.channel.send(const.STV.FirstTimeChadder)


def prepare(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    bot.add_cog(Alerts(bot))
