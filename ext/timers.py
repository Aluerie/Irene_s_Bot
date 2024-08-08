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
    def __init__(self, bot: IrenesBot) -> None:
        super().__init__(bot)
        self.stream_online: bool = False

        self.messages: list[str] = [
            f"FIX YOUR POSTURE {const.FFZ.Weirdge}",
            (
                f"{const.STV.heyinoticedyouhaveaprimegamingbadgenexttoyourname} Use your Twitch Prime to sub for "
                f"my channel {const.STV.DonkPrime} it's completely free {const.BTTV.PogU}"
            ),
            f"{const.STV.Adge} {const.STV.DankApprove}",
            f"Don't forget to stretch and scoot {const.STV.GroupScoots}",
            # "Discord discord.gg/K8FuDeP",
            # "if you have nothing to do Sadge you can try !randompasta. Maybe you'll like it Okayge",
        ]
        self.lines_count: int = 0
        self.check_stream_online.start()

    @irenes_routine(iterations=1)
    async def check_stream_online(self) -> None:
        stream = next(iter(await self.bot.fetch_streams(user_ids=[const.ID.Irene])), None)  # None if offline
        if stream:
            self.stream_online = True
            self.timer_task.start()

    @commands.Cog.event()  # type: ignore # lib issue
    async def event_eventsub_notification_stream_start(self, _: eventsub.StreamOnlineData) -> None:
        """Stream started (went live)."""
        self.stream_online = True
        self.timer_task.start()

    @commands.Cog.event()  # type: ignore # lib issue
    async def event_eventsub_notification_stream_end(self, _: eventsub.StreamOfflineData) -> None:
        """Stream ended (went offline)."""
        self.stream_online = False
        self.timer_task.cancel()

    @commands.Cog.event()  # type: ignore # lib issue
    async def event_message(self, message: twitchio.Message) -> None:
        if message.echo or not self.stream_online:
            return

        self.lines_count += 1

    @irenes_routine(minutes=103, wait_first=True)
    async def timer_task(self) -> None:
        messages = self.messages.copy()
        random.shuffle(messages)

        irene_channel = self.irene_channel()
        for text in itertools.cycle(messages):
            while self.lines_count < 50:
                await asyncio.sleep(60)

            self.lines_count = 0
            await irene_channel.send(text)
            time_to_sleep = 60 * (60 + random.randint(1, 20))
            await asyncio.sleep(time_to_sleep)


def prepare(bot: IrenesBot) -> None:
    bot.add_cog(Timers(bot))
