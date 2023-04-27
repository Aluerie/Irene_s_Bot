from __future__ import annotations

import asyncio
import logging
import sys
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING, List

import click

from utils.bot import LueByt
from utils.database import create_pool

if TYPE_CHECKING:
    pass

try:
    import uvloop  # type: ignore
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


@contextmanager
def setup_logging():
    log = logging.getLogger()
    log.setLevel(logging.INFO)

    try:
        # Stream Handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "{asctime} | {levelname:<7} | {name:<23} | {lineno:<4} | {funcName:<30} | {message}",
            "%H:%M:%S %d/%m",
            style="{",
        )
        handler.setFormatter(formatter)
        log.addHandler(handler)

        # ensure logs folder
        Path(".logs/").mkdir(parents=True, exist_ok=True)
        # File Handler
        file_handler = RotatingFileHandler(
            filename=f".logs/luebyt.log",
            encoding="utf-8",
            mode="w",
            maxBytes=16 * 1024 * 1024,  # 16 MiB
            backupCount=5,  # Rotate through 5 files
        )
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)


async def bot_start():
    log = logging.getLogger()
    try:
        pool = await create_pool()
    except Exception:
        click.echo("Could not set up PostgreSQL. Exiting.", file=sys.stderr)
        log.exception("Could not set up PostgreSQL. Exiting.")
        return

    query = "SELECT user_name FROM twitch_users"
    initial_channels: List[str] = [row for row, in await pool.fetch(query)]
    # async with LueByt() as bot:
    bot = LueByt(initial_channels)
    bot.pool = pool
    await bot.start()


@click.group(invoke_without_command=True, options_metavar="[options]")
@click.pass_context
def main(click_ctx: click.Context):
    """Launches the bot."""

    if click_ctx.invoked_subcommand is None:
        with setup_logging():
            asyncio.run(bot_start())


if __name__ == "__main__":
    main()
