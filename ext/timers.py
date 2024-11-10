from __future__ import annotations

import asyncio
import itertools
import random
from typing import TYPE_CHECKING

from twitchio.ext import commands

from bot import IrenesComponent, irenes_loop
from utils import const

if TYPE_CHECKING:
    import twitchio

    from bot import IrenesBot


class Timers(IrenesComponent):
    """Periodic messages/announcements in Irene's channel."""

    def __init__(self, bot: IrenesBot) -> None:
        super().__init__(bot)

        self.messages: list[str] = [
            f"FIX YOUR POSTURE {const.BTTV.weirdChamp}",
            (
                f"{const.STV.heyinoticedyouhaveaprimegamingbadgenexttoyourname} Use your Twitch Prime to sub for "
                f"my channel {const.STV.DonkPrime} it's completely free {const.BTTV.PogU}"
            ),
            f"{const.STV.Adge} {const.STV.DankApprove}",
            f"Don't forget to stretch and scoot {const.STV.GroupScoots}",
            f"{const.STV.plink}",
            f"{const.STV.uuh}",
            f"chat don't forget to {const.STV.plink}",
            (
                "hi chat many features of this bot are WIP so, please, if you notice bugs or incorrect responses "
                f"- inform me {const.STV.DANKHACKERMANS}"
            ),
            # "Discord discord.gg/K8FuDeP",
            # "if you have nothing to do Sadge you can try !randompasta. Maybe you'll like it Okayge",
        ]
        self.lines_count: int = 0
        self.check_stream_online.start()

    @irenes_loop(count=1)
    async def check_stream_online(self) -> None:
        """Check if the stream is live on bot's reboot."""
        stream = next(iter(await self.bot.fetch_streams(user_ids=[const.UserID.Irene])), None)  # None if offline
        if stream:
            self.timer_task.start()

    @commands.Component.listener(name="stream_online")
    async def event_eventsub_notification_stream_start(self, _: twitchio.StreamOnline) -> None:
        """Stream started (went live)."""
        self.timer_task.start()

    @commands.Component.listener(name="stream_offline")
    async def event_eventsub_notification_stream_end(self, _: twitchio.StreamOffline) -> None:
        """Stream ended (went offline)."""
        self.timer_task.cancel()

    @commands.Component.listener(name="message")
    async def count_messages(self, message: twitchio.ChatMessage) -> None:
        """Count messages between timers so the bot doesn't spam fill up an empty chat."""
        if message.chatter.name in const.Bots:
            # * do not count messages from the bot itself
            # other bots soon^tm will stop talking in my chat at all so this is a fine check;
            # No need for `message.author.name.lower() in const.Bot` condition
            return

        self.lines_count += 1

    @irenes_loop(count=1)
    async def timer_task(self) -> None:
        """Task to send periodic messages into irene's channel on timer."""
        await asyncio.sleep(10 * 60)
        messages = self.messages.copy()
        random.shuffle(messages)

        # refresh lines count so it only counts messages from the current stream.
        self.lines_count = 0
        for text in itertools.cycle(messages):
            while self.lines_count < 99:
                await asyncio.sleep(100)

            self.lines_count = 0
            await self.deliver(text)
            minutes_to_sleep = 69 + random.randint(1, 21)
            await asyncio.sleep(minutes_to_sleep * 60)

    @timer_task.before_loop
    async def timer_task_before_loop(self) -> None:
        await self.bot.wait_for("ready")


async def setup(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    await bot.add_component(Timers(bot))
