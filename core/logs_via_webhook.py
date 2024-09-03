from __future__ import annotations

import asyncio
import datetime
import logging
import platform
import textwrap
from typing import TYPE_CHECKING, Any, override

import discord
from discord.ext import tasks

from bot import IrenesCog
from config import LOGGER_WEBHOOK
from utils import const

if TYPE_CHECKING:
    from collections.abc import Mapping

    from bot import IrenesBot

log = logging.getLogger(__name__)


class LoggingHandler(logging.Handler):
    """Extra Logging Handler to output info/warning/errors to a discord webhook."""

    def __init__(self, cog: LogsViaWebhook) -> None:
        self.cog: LogsViaWebhook = cog
        super().__init__(logging.INFO)

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter out some somewhat pointless messages so we don't spam the channel as much."""
        messages_to_ignore = (
            "Webhook ID 1116501979133399113 is rate limited.",  #todo: wrong id
        )
        if any(msg in record.message for msg in messages_to_ignore):  # noqa: SIM103
            return False

        return True

    @override
    def emit(self, record: logging.LogRecord) -> None:
        self.cog.add_record(record)


class LogsViaWebhook(IrenesCog):
    """Mirroring logs to discord webhook messages.

    This cog is responsible for rate-limiting, formatting, fine-tuning and sending the log messages.
    """

    # TODO: ADD MORE STUFF
    AVATAR_MAPPING: Mapping[str, str] = {
        "bot.bot": "https://i.imgur.com/6XZ8Roa.png",  # lady Noir
        "exc_manager": "https://em-content.zobj.net/source/microsoft/378/sos-button_1f198.png",
        "twitchio.ext.eventsub.ws": const.Logo.Twitch,
        "twitchio.websocket": const.Logo.Twitch,
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._logging_queue = asyncio.Queue()

        # cooldown attrs
        self._lock: asyncio.Lock = asyncio.Lock()
        self.cooldown: datetime.timedelta = datetime.timedelta(seconds=5)
        self._most_recent: datetime.datetime | None = None

        self.logging_worker.start()

    @override
    def cog_unload(self) -> None:
        self.logging_worker.stop()

    @discord.utils.cached_property
    def logger_webhook(self) -> discord.Webhook:
        """A webhook in hideout's #logger channel."""
        return self.bot.webhook_from_url(LOGGER_WEBHOOK)

    def add_record(self, record: logging.LogRecord) -> None:
        """Add a record to a logging queue."""
        self._logging_queue.put_nowait(record)

    async def send_log_record(self, record: logging.LogRecord) -> None:
        """Send Log record to discord webhook."""
        attributes = {
            "INFO": "\N{INFORMATION SOURCE}\ufe0f",
            "WARNING": "\N{WARNING SIGN}\ufe0f",
            "ERROR": "\N{CROSS MARK}",
        }

        emoji = attributes.get(record.levelname, "\N{WHITE QUESTION MARK ORNAMENT}")
        dt = datetime.datetime.fromtimestamp(record.created, datetime.UTC)
        msg = textwrap.shorten(f"{emoji} {discord.utils.format_dt(dt, style="T")} {record.message}", width=1995)
        avatar_url = self.AVATAR_MAPPING.get(record.name, discord.utils.MISSING)
        username = record.name.replace("discord", "disсοrd")  # cSpell: ignore disсοrd  # noqa: RUF003
        await self.logger_webhook.send(msg, username=username, avatar_url=avatar_url)

    @tasks.loop(seconds=0.0)
    async def logging_worker(self) -> None:
        """Task responsible for mirroring logging messages to a discord webhook."""
        record = await self._logging_queue.get()

        async with self._lock:
            if self._most_recent and (delta := datetime.datetime.now(datetime.UTC) - self._most_recent) < self.cooldown:
                # We have to wait
                total_seconds = delta.total_seconds()
                log.debug("Waiting %s seconds to send the error.", total_seconds)
                await asyncio.sleep(total_seconds)

            self._most_recent = datetime.datetime.now(datetime.UTC)
            await self.send_log_record(record)


async def setup(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    if platform.system() == "Windows":
        return

    cog = LogsViaWebhook(bot)
    bot.add_cog(cog)
    bot.logs_via_webhook_handler = handler = LoggingHandler(cog)
    logging.getLogger().addHandler(handler)
