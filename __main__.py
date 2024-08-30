from __future__ import annotations

import asyncio
import logging
import sys

import aiohttp
import click

import config
from bot import IrenesBot, setup_logging
from utils.database import create_pool

try:
    import uvloop  # type: ignore
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def start_the_bot() -> None:
    log = logging.getLogger()
    try:
        pool = await create_pool()
    except Exception:
        click.echo("Could not set up PostgreSQL. Exiting.", file=sys.stderr)
        log.exception("Could not set up PostgreSQL. Exiting.")
        return

    access_token = config.TTG_ACCESS_TOKEN
    # if not await tokens.verify_token(access_token):
    #     access_token = await tokens.refresh_access_token(
    #         refresh_token=config.TWITCH_REFRESH_TOKEN,
    #         client_id=config.TWITCH_CLIENT_ID,
    #         secret=config.TWITCH_CLIENT_SECRET,
    #     )

    query = "SELECT user_name FROM joined_streamers"
    initial_channels: list[str] = [str(user_name) for (user_name,) in await pool.fetch(query)]

    async with (
        aiohttp.ClientSession() as session,
        pool as pool,
        IrenesBot(access_token, initial_channels, session=session, pool=pool) as irenesbot,
    ):
        await irenesbot.start()


@click.group(invoke_without_command=True, options_metavar="[options]")
@click.pass_context
def main(click_ctx: click.Context) -> None:
    """Launches the bot."""
    if click_ctx.invoked_subcommand is None:
        with setup_logging():
            asyncio.run(start_the_bot())


if __name__ == "__main__":
    main()
