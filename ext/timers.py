from __future__ import annotations

import asyncio
import itertools
import random
from typing import TYPE_CHECKING

from twitchio.ext import commands, eventsub

from bot import IrenesCog, irenes_routine
from utils import const

if TYPE_CHECKING:
    import twitchio

    from bot import IrenesBot


class Timers(IrenesCog):
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
            f"{const.STV.Plink}",
            f"{const.STV.uuh}",
            f"chat don't forget to {const.STV.Plink}",
            # "Discord discord.gg/K8FuDeP",
            # "if you have nothing to do Sadge you can try !randompasta. Maybe you'll like it Okayge",
        ]
        self.lines_count: int = 0
        self.check_stream_online.start()

    @irenes_routine(iterations=1)
    async def check_stream_online(self) -> None:
        """Check if the stream is live on bot's reboot."""
        stream = next(iter(await self.bot.fetch_streams(user_ids=[const.ID.Irene])), None)  # None if offline
        if stream:
            self.timer_task.start()

    @commands.Cog.event()  # type: ignore # lib issue
    async def event_eventsub_notification_stream_start(self, _: eventsub.StreamOnlineData) -> None:
        """Stream started (went live)."""
        self.timer_task.start()

    @commands.Cog.event()  # type: ignore # lib issue
    async def event_eventsub_notification_stream_end(self, _: eventsub.StreamOfflineData) -> None:
        """Stream ended (went offline)."""
        self.timer_task.cancel()

    @commands.Cog.event(event="event_message")  # type: ignore # lib issue
    async def count_messages(self, message: twitchio.Message) -> None:
        """Count messages between timers so the bot doesn't spam fill up an empty chat."""
        if message.echo:
            # * do not count messages from the bot itself
            # other bots soon^tm will stop talking in my chat at all so this is a fine check;
            # No need for `message.author.name.lower() in const.Bot` condition
            return

        self.lines_count += 1

    @irenes_routine(iterations=1)
    async def timer_task(self) -> None:
        """Task to send periodic messages into irene's channel on timer."""
        await asyncio.sleep(10 * 60)
        messages = self.messages.copy()
        random.shuffle(messages)

        # refresh lines count so it only counts messages from the current stream.
        self.lines_count = 0
        irene_channel = self.irene_channel()
        for text in itertools.cycle(messages):
            while self.lines_count < 99:
                await asyncio.sleep(100)

            self.lines_count = 0
            await irene_channel.send(text)
            minutes_to_sleep = 69 + random.randint(1, 21)
            await asyncio.sleep(minutes_to_sleep * 60)


def prepare(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    bot.add_cog(Timers(bot))
