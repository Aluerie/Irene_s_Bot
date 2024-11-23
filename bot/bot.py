from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, TypedDict, override

import discord
import twitchio
from twitchio import eventsub
from twitchio.ext import commands

import config
from ext import EXTENSIONS
from utils import const, errors
from utils.dota import Dota2Client

from .bases import irenes_loop
from .exc_manager import ExceptionManager

if TYPE_CHECKING:
    import asyncpg
    from aiohttp import ClientSession

    from utils.database import PoolTypedWithAny

    class LoadTokensQueryRow(TypedDict):
        user_id: str
        token: str
        refresh: str


__all__ = ("IrenesBot",)

log = logging.getLogger(__name__)


class IrenesBot(commands.Bot):
    """Main class for Irene's Bot.

    Essentially subclass over TwitchIO's Client.
    Used to interact with the Twitch API, EventSub and more.
    Includes `ext.commands` extension to organize cogs/commands framework.
    """

    if TYPE_CHECKING:
        logs_via_webhook_handler: logging.Handler

    def __init__(
        self,
        *,
        session: ClientSession,
        pool: asyncpg.Pool[asyncpg.Record],
    ) -> None:
        """Initiate IrenesBot.

        Parameters
        ----------
        initial_channels
            List of channel names (names, not ids!).

        """
        self.prefixes: tuple[str, ...] = ("!", "?", "$")
        super().__init__(
            client_id=config.TTV_DEV_CLIENT_ID,
            client_secret=config.TTV_DEV_CLIENT_SECRET,
            bot_id=const.UserID.Bot,
            owner_id=const.UserID.Irene,
            prefix=self.prefixes,
            # TODO: fill in scopes= argument once we figure out what it's used for :x
        )
        self.database: asyncpg.Pool[asyncpg.Record] = pool
        self.pool: PoolTypedWithAny = pool  # type: ignore # asyncpg typehinting crutch, read `utils.database` for more
        self.session: ClientSession = session
        self.extensions: tuple[str, ...] = EXTENSIONS

        self.exc_manager = ExceptionManager(self)
        self.repo = "https://github.com/Aluerie/Irene_s_Bot"
        self.dota = Dota2Client(self)

        self.irene_online: bool = False

    # def show_oauth(self) -> None:
    #     oauth = twitchio.authentication.OAuth(
    #         client_id=config.TTV_DEV_CLIENT_ID,
    #         client_secret=config.TTV_DEV_CLIENT_SECRET,
    #         redirect_uri="http://localhost:4343/oauth/callback",
    #         scopes=twitchio.Scopes(
    #             [
    #                 "channel:bot",
    #                 "channel:read:ads",
    #                 "channel:moderate",
    #                 "moderator:read:followers",
    #                 "channel:read:redemptions",
    #             ]
    #         ),
    #     )
    #     #
    #     #  # Generate the authorization URL
    #     auth_url = oauth.get_authorization_url(force_verify=True)
    #     print(auth_url)  # noa: T201

    def print_bot_oauth(self) -> None:
        scopes = "%20".join(
            [
                "user:read:chat",
                "user:write:chat",
                "user:bot",
                "moderator:read:followers",
                "moderator:manage:shoutouts",
                "moderator:manage:announcements",
                "moderator:manage:banned_users",
                "clips:edit",
            ]
        )
        link = f"http://localhost:4343/oauth?scopes={scopes}&force_verify=true"
        print(f"🤖🤖🤖 BOT OATH LINK: 🤖🤖🤖\n{link}")  # noqa: T201

    def print_broadcaster_oauth(self) -> None:
        scopes = "%20".join(
            [
                "channel:bot",
                "channel:read:ads",
                "channel:moderate",
                "channel:read:redemptions",
                "channel:manage:broadcast",
            ]
        )
        link = f"http://localhost:4343/oauth?scopes={scopes}&force_verify=true"
        print(f"🎬🎬🎬 BROADCASTER OATH LINK: 🎬🎬🎬\n{link}")  # noqa: T201

    @override
    async def setup_hook(self) -> None:
        # Twitchio tokens magic
        # Uncomment the following three lines and run the bot when creating tokens (otherwise they should be commented)
        # This will make the bot update the database with new tokens.
        # self.print_bot_oauth()
        # self.print_broadcaster_oauth()
        # return

        for ext in self.extensions:
            await self.load_module(ext)

        # it's just a personal bot :)
        broadcaster = const.UserID.Irene
        bot = const.UserID.Bot

        # * TwitchDev Docs:
        #   Eventsub:   https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types
        #   Scopes:     https://dev.twitch.tv/docs/authentication/scopes/
        # * TwitchIO  Docs:
        #   Events:     https://twitchio.dev/en/dev-3.0/references/events.html
        #   Models:     https://twitchio.dev/en/dev-3.0/references/eventsub_models.html

        # EventSub Subscriptions Table (order - function name sorted by alphabet).
        # Subscription Name                     Permission
        # ------------------------------------------------------
        # ✅ Ad break begin                        channel:read:ads
        sub = eventsub.AdBreakBeginSubscription(broadcaster_user_id=broadcaster)
        await self.subscribe_websocket(payload=sub, token_for=broadcaster, as_bot=False)
        # Bans                                  channel:moderate
        sub = eventsub.ChannelBanSubscription(broadcaster_user_id=broadcaster)
        await self.subscribe_websocket(payload=sub, token_for=broadcaster, as_bot=False)
        # ✅ Follows                               moderator:read:followers
        sub = eventsub.ChannelFollowSubscription(broadcaster_user_id=broadcaster, moderator_user_id=bot)
        await self.subscribe_websocket(payload=sub)
        # ✅ Channel Points Redeem                 channel:read:redemptions or channel:manage:redemptions
        sub = eventsub.ChannelPointsRedeemAddSubscription(broadcaster_user_id=broadcaster)
        await self.subscribe_websocket(payload=sub, token_for=broadcaster, as_bot=False)
        # ✅ Message                               user:read:chat from the chatting user, channel:bot from broadcaster
        sub = eventsub.ChatMessageSubscription(broadcaster_user_id=broadcaster, user_id=bot)
        await self.subscribe_websocket(payload=sub)
        # Raids to the channel                  No authorization required
        sub = eventsub.ChannelRaidSubscription(to_broadcaster_user_id=broadcaster)
        await self.subscribe_websocket(payload=sub)
        # ✅ Stream went offline                   No authorization required
        sub = eventsub.StreamOfflineSubscription(broadcaster_user_id=broadcaster)
        await self.subscribe_websocket(payload=sub)
        # ✅ Stream went live                      No authorization required
        sub = eventsub.StreamOnlineSubscription(broadcaster_user_id=broadcaster)
        await self.subscribe_websocket(payload=sub)
        # ✅ Channel Update (title/game)           No authorization required
        sub = eventsub.ChannelUpdateSubscription(broadcaster_user_id=broadcaster)
        await self.subscribe_websocket(payload=sub)

        self.check_if_online.start()

    @override
    async def add_token(self, token: str, refresh: str) -> twitchio.authentication.ValidateTokenPayload:
        # Make sure to call super() as it will add the tokens internally and return us some data...
        resp: twitchio.authentication.ValidateTokenPayload = await super().add_token(token, refresh)

        # Store our tokens in a simple SQLite Database when they are authorized...
        query = """
            INSERT INTO ttv_tokens (user_id, token, refresh)
            VALUES ($1, $2, $3)
            ON CONFLICT(user_id)
            DO UPDATE SET
                token = excluded.token,
                refresh = excluded.refresh;
        """
        await self.pool.execute(query, resp.user_id, token, refresh)
        log.debug("Added token to the database for user: %s", resp.user_id)
        return resp

    @override
    async def load_tokens(self, path: str | None = None) -> None:
        # We don't need to call this manually, it is called in .login() from .start() internally...

        rows: list[LoadTokensQueryRow] = await self.pool.fetch("""SELECT * from ttv_tokens""")
        for row in rows:
            await self.add_token(row["token"], row["refresh"])

    # @override
    async def event_ready(self) -> None:
        log.info("Irene_s_Bot is ready as bot_id = %s", self.bot_id)
        if "ext.dota" in self.extensions:
            await self.dota.wait_until_ready()

    @override
    async def event_command_error(self, payload: commands.CommandErrorPayload) -> None:
        """Called when error happens during command invoking."""
        command: commands.Command[Any, ...] | None = payload.context.command
        if command and command.has_error and payload.context.error_dispatched:
            return

        ctx = payload.context
        error = payload.exception

        # we aren't interested in the chain traceback:
        error = error.original if isinstance(error, commands.CommandInvokeError) and error.original else error

        match error:
            case errors.IrenesBotError():
                # errors defined by me - just send the string
                await ctx.send(str(error))
            case commands.CommandNotFound():
                #  otherwise we just spam console with commands from other bots and from my event thing
                log.info("CommandNotFound: %s", payload.exception)
            case commands.GuardFailure():
                guard_mapping = {
                    "is_moderator.<locals>.predicate": (
                        f"Only moderators are allowed to use this command {const.FFZ.peepoPolice}"
                    ),
                    "is_vps.<locals>.predicate": (
                        f"Only production bot allows usage of this command {const.FFZ.peepoPolice}"
                    ),
                    "is_owner.<locals>.predicate": (
                        f"Only Irene is allowed to use this command {const.FFZ.peepoPolice}"
                    ),
                    "is_online.<locals>.predicate": (
                        f"This commands is only allowed when stream is online {const.FFZ.peepoPolice}"
                    ),
                }
                await ctx.send(guard_mapping.get(error.guard.__qualname__, str(error)))
            case twitchio.HTTPException():
                # log.error("%s", error.__class__.__name__, exc_info=error)
                await ctx.send(
                    f"{error.extra.get('error', 'Error')} {error.extra.get('status', 'XXX')}: "
                    f"{error.extra.get('message', 'Unknown')} {const.STV.dankFix}"
                )
            case commands.MissingRequiredArgument():
                await ctx.send(
                    f'You need to provide "{error.param.name}" argument for this command {const.FFZ.peepoPolice}'
                )

            # case commands.CommandOnCooldown(): # TODO: WAIT TILL IMPLEMENTED
            #     await ctx.send(
            #         f"Command {ctx.prefix}{error.command.name} is on cooldown! Try again in {error.retry_after:.0f} sec."
            #     )

            # case commands.BadArgument():
            #     log.warning("%s %s", error.name, error)
            #     await ctx.send(f"Couldn't find any {error.name} like that")
            # case commands.ArgumentError():
            #     await ctx.send(str(error))

            case _:
                await ctx.send(f"{error.__class__.__name__}: {config.replace_secrets(str(error))}")

                command_name = getattr(ctx.command, "name", "unknown")

                embed = (
                    discord.Embed(
                        colour=ctx.chatter.colour.code if ctx.chatter.colour else 0x890620,
                        title=f"Error in `!{command_name}`",
                    )
                    .add_field(
                        name="Command Args",
                        value=(
                            "```py\n" + "\n".join(f"[{name}]: {value!r}" for name, value in ctx.kwargs.items()) + "```"
                            if ctx.kwargs
                            else "```py\nNo arguments```"
                        ),
                        inline=False,
                    )
                    .set_author(
                        name=ctx.chatter.display_name,
                        icon_url=(await ctx.chatter.user()).profile_image,
                    )
                    .set_footer(
                        text=f"event_command_error: {command_name}",
                        icon_url=(await ctx.broadcaster.user()).profile_image,
                    )
                )
                await self.exc_manager.register_error(error, embed=embed)

    @override
    async def event_error(self, payload: twitchio.EventErrorPayload) -> None:
        embed = (
            discord.Embed()
            .add_field(name="Exception", value=f"`{payload.error.__class__.__name__}`")
            .set_footer(text=f"event_error: `{payload.listener.__qualname__}`")
        )
        await self.exc_manager.register_error(payload.error, embed=embed)

    @override
    async def start(self) -> None:
        if "ext.dota" in self.extensions:
            await asyncio.gather(
                super().start(),
                self.dota.login(),
            )
        else:
            await super().start()

    async def instantiate_steam_web_api(self) -> None:
        """Initialize Steam Web API client."""
        if not hasattr(self, "steam_web_api"):
            from utils.dota import SteamWebAPIClient

            self.steam_web_api = SteamWebAPIClient()
            await self.steam_web_api.__aenter__()

    async def instantiate_opendota(self) -> None:
        """Initialize OpenDota client."""
        if not hasattr(self, "opendota"):
            from utils.dota import OpenDotaClient

            self.opendota = OpenDotaClient()
            await self.opendota.__aenter__()

    async def instantiate_cache_dota(self) -> None:
        """Initialize OpenDota client."""
        if not hasattr(self, "cache_dota"):
            from utils.dota import DotaKeyCache

            self.cache_dota = DotaKeyCache(self)

    @override
    async def close(self) -> None:
        await self.dota.close()
        await super().close()

        for client in (
            "steam_web_api",
            "opendota",
        ):
            if hasattr(self, client):
                await getattr(self, client).__aexit__()

    def webhook_from_url(self, url: str) -> discord.Webhook:
        """A shortcut function with filled in discord.Webhook.from_url args."""
        return discord.Webhook.from_url(url=url, session=self.session)

    @discord.utils.cached_property
    def logger_webhook(self) -> discord.Webhook:
        """A webhook in hideout's #logger channel."""
        return self.webhook_from_url(config.LOGGER_WEBHOOK)

    @discord.utils.cached_property
    def error_webhook(self) -> discord.Webhook:
        """A webhook in hideout server to send errors/notifications to the developer(-s)."""
        return self.webhook_from_url(config.ERROR_WEBHOOK)

    @property
    def error_ping(self) -> str:
        """Error Role ping used to notify Irene about some errors."""
        return config.ERROR_PING

    async def irene_stream(self) -> twitchio.Stream | None:
        return next(iter(await self.fetch_streams(user_ids=[const.UserID.Irene])), None)

    @irenes_loop(count=1)
    async def check_if_online(self) -> None:
        if await self.irene_stream():
            self.irene_online = True
            self.dispatch("irene_online")

    async def event_stream_online(self, _: twitchio.StreamOnline) -> None:
        self.irene_online = True
        self.dispatch("irene_online")

    async def event_stream_offline(self, _: twitchio.StreamOffline) -> None:
        self.irene_online = False
        self.dispatch("irene_offline")
