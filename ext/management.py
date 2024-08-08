from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from twitchio.ext import commands, eventsub

import config
from bot import IrenesCog, irenes_routine
from utils import const

if TYPE_CHECKING:
    from bot import IrenesBot


class ChannelManagement(IrenesCog):
    def __init__(self, bot: IrenesBot) -> None:
        super().__init__(bot)
        self.game_tracked: str = "idk"
        self.title_tracked: str = "idk"

        # datetimes indicating when game/title was changed with specifically Irene's Bot commands !game/!title
        self.game_updated_dt: datetime.datetime = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=1)
        self.title_updated_dt: datetime.datetime = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=1)

        self.start_tracking.start()

    @irenes_routine(iterations=1)
    async def start_tracking(self) -> None:
        channel_info = await self.bot.fetch_channel(const.Name.Irene)

        self.game_tracked = channel_info.game_name
        self.title_tracked = channel_info.title

    @commands.command()
    async def game(self, ctx: commands.Context, *, game_name: str | None = None) -> None:
        """Either get current channel game or update it."""

        streamer = await ctx.channel.user()

        if not game_name:
            # 1. No argument
            # respond with current game name the channel is playing
            channel_info = await ctx.bot.fetch_channel(streamer.name)

            game_name = channel_info.game_name if channel_info.game_name else "No game category"
            await ctx.send(f"{game_name} {const.STV.DankDolmes}")
            return

        # 2. Argument "game_name" is provided
        # Set the game to it
        if not ctx.author.is_mod:  # type: ignore # the dev said it's fine
            # a. non-mod case
            await ctx.send(f"Only moderators are allowed to change game name {const.STV.peepoPolice}")
            return

        if game_name.lower() == "clear":
            # b. A keyword to clear the game category, sets it uncategorised
            self.game_updated_dt = datetime.datetime.now(datetime.UTC)
            await streamer.modify_stream(token=config.TTG_IRENE_ACCESS_TOKEN, game_id=0)
            await ctx.send(f'Set game to "No game category" {const.STV.uuh}')
            return

        # c. specified game
        # specific exception so I can type "!game dota" without 2;
        game_name = game_name if game_name != "dota" else "Dota 2"

        game = next(iter(await self.bot.fetch_games(names=[game_name])), None)
        if not game:
            await ctx.send(f"Couldn't find any games with such a name {const.STV.How2Read}")
            return

        self.game_updated_dt = datetime.datetime.now(datetime.UTC)
        await streamer.modify_stream(token=config.TTG_IRENE_ACCESS_TOKEN, game_id=game.id)
        await ctx.send(f'Changed game to "{game.name}" {const.STV.DankMods}')
        return

    @commands.command()
    async def title(self, ctx: commands.Context, *, title: str | None = None) -> None:
        """Either get current channel title or update it."""

        streamer = await ctx.channel.user()

        if not title:
            # 1. No argument
            # respond with current game name the channel is playing
            channel_info = await ctx.bot.fetch_channel(streamer.name)
            await ctx.send(channel_info.title)
            return

        # 2. Argument "title" is provided
        # Set the title to it
        if not ctx.author.is_mod:  # type: ignore # the dev said it's fine
            # a. non-mod case
            await ctx.send(f"Only moderators are allowed to change title {const.STV.peepoPolice}")
            return

        self.title_updated_dt = datetime.datetime.now(datetime.UTC)
        await streamer.modify_stream(token=config.TTG_IRENE_ACCESS_TOKEN, title=title)
        await ctx.send(f'{const.STV.donkHappy} Changed title to "{title}"')
        return

    @commands.Cog.event(event="event_eventsub_notification_channel_update")  # type: ignore # lib issue
    async def channel_update(self, event: eventsub.NotificationEvent) -> None:
        """Channel Info (game, title, etc) got updated."""
        payload: eventsub.ChannelUpdateData = event.data  # type: ignore
        channel_name = payload.broadcaster.name
        assert channel_name
        channel = self.bot.get_channel(channel_name)
        assert channel

        now = datetime.datetime.now(datetime.UTC)
        if self.game_tracked != payload.category_name and (now - self.game_updated_dt).seconds > 15:
            await channel.send(f'{const.STV.donkDetective} Game was changed to "{payload.category_name}"')

        if self.title_tracked != payload.title and (now - self.title_updated_dt).seconds > 15:
            await channel.send(f'{const.STV.DankThink} Title was changed to "{payload.title}"')

        self.game_tracked = payload.category_name
        self.title_tracked = payload.title


def prepare(bot: IrenesBot) -> None:
    bot.add_cog(ChannelManagement(bot))
