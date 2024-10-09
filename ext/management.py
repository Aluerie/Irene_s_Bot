from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from twitchio.ext import commands, eventsub

import config
from bot import IrenesCog, irenes_loop
from utils import checks, const, errors, formats

if TYPE_CHECKING:
    import twitchio

    from bot import IrenesBot


class ChannelManagement(IrenesCog):
    """Channel Management commands.

    Such as change Game or Title.
    """

    def __init__(self, bot: IrenesBot) -> None:
        super().__init__(bot)
        self.game_tracked: str = "idk"
        self.title_tracked: str = "idk"

        # datetimes indicating when game/title was changed with specifically Irene's Bot commands !game/!title
        self.game_updated_dt: datetime.datetime = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=1)
        self.title_updated_dt: datetime.datetime = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=1)

        self.start_tracking.start()

    @irenes_loop(count=1)
    async def start_tracking(self) -> None:
        """Start tracking my channel info.

        Unfortunately, twitch eventSub payloads for channel update events do not have before/after and
        do not say what exactly changed, they just send new stuff in.

        This is why we need to track the past ourselves.
        """
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
            await ctx.send(f"Only moderators are allowed to change game name {const.FFZ.peepoPolice}")
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

    async def update_title(self, streamer: twitchio.User, title: str) -> None:
        """Helper function to update the streamer's title."""
        self.title_updated_dt = datetime.datetime.now(datetime.UTC)
        try:
            await streamer.modify_stream(token=config.TTG_IRENE_ACCESS_TOKEN, title=title)
        except Exception as error:
            if "Title is too long" in str(error):
                msg = f"Sorry, title is too long: {len(title)}/140"
                raise errors.UsageError(msg)
            else:
                raise errors.SomethingWentWrong(str(error))
        else:
            # success
            return

    async def title_callback(self, ctx: commands.Context, *, title: str | None = None) -> None:
        """Callback for !title group commands.

        Can be used with subcommands. But when used on its - it either shows the title or updates it,
        whether the title argument was provided and user has moderator permissions.

        Examples
        --------
            * !title - shows current title.
            * !title Hello World - title changes to "Hello World" (if mod)
        """
        streamer = await ctx.channel.user()

        if not title:
            # 1. No argument
            # respond with current game name the channel is playing
            channel_info = await ctx.bot.fetch_channel(streamer.name)
            await ctx.send(channel_info.title)
            return

        # 2. Argument "title" is provided
        if not ctx.author.is_mod:  # type: ignore # the dev said it's fine
            # a. non-mod case: give a warning for the chatter
            await ctx.send(f"Only moderators are allowed to change title {const.FFZ.peepoPolice}")
        else:
            # b. mod case: actually update the title
            await self.update_title(streamer, title=title)
            await ctx.send(f'{const.STV.donkHappy} Changed title to "{title}"')

    # todo: do it with @commands.group when they bring it back
    title_group = commands.Group(name="title", func=title_callback)

    @checks.is_mod()
    @title_group.command(name="set")
    async def title_set(self, ctx: commands.Context, *, title: str) -> None:
        """Set the title for the stream."""
        streamer = await ctx.channel.user()
        await self.update_title(streamer, title=title)
        await ctx.send(f'{const.STV.donkHappy} Set title to "{title}"')

    @checks.is_mod()
    @title_group.command(name="restore", aliases=["prev", "previous"])
    async def title_restore(self, ctx: commands.Context, offset: int = 1) -> None:
        """Restore title for the stream from the database.

        Database keeps some recent titles (cleans up up to last 2 days on stream-offline event).
        Useful when we switch the title for some activity, i.e. "watching animes" and then
        go back to Elden Ring so we just !title restore and it sets to my previous relevant Elden Ring title.

        Parameters
        ----------
        offset
            The number representing how old the title should be as in ordinal, i.e. !title restore 5 means
            restore 5th newest title from the database. "Previous" = 1 for this logic (and default).
        """
        query = """
            SELECT title FROM ttv_stream_titles
            ORDER BY edit_time DESC
            LIMIT 1
            OFFSET $1;
        """
        title: str | None = await self.bot.pool.fetchval(query, offset)
        if title is None:
            await ctx.send("No change: the database doesn't keep such an old title.")
        else:
            streamer = await ctx.channel.user()
            await self.update_title(streamer, title=title)
            await ctx.send(f"Set the title to {formats.ordinal(offset)} in history: {title}")

    @checks.is_mod()
    @title_group.command(name="history")
    async def title_history(self, ctx: commands.Context, number: int = 3) -> None:
        """Shows some title history so you can remember/edit what we had before.

        Parameters
        ----------
        number
            amount of entries (newest titles) to pull out from the database.

        """
        query = """
            SELECT title FROM ttv_stream_titles
            ORDER BY edit_time DESC
            LIMIT $1
            OFFSET 1
        """
        history_titles: list[str] = [r for (r,) in await self.bot.pool.fetch(query, number)]
        if len(history_titles):
            for count, saved_title in enumerate(history_titles, start=1):
                await ctx.send(f"{count}. {saved_title}")
        else:
            await ctx.send("Database doesn't have any titles saved.")

    @commands.Cog.event(event="event_eventsub_notification_channel_update")  # type: ignore # lib issue
    async def channel_update(self, event: eventsub.NotificationEvent) -> None:
        """Channel Info (game, title, etc) got updated."""
        payload: eventsub.ChannelUpdateData = event.data  # type: ignore
        channel_name = payload.broadcaster.name
        assert channel_name
        channel = self.bot.get_channel(channel_name)
        assert channel

        now = datetime.datetime.now(datetime.UTC)
        # time check is needed so we don't repeat notif that comes from !game !title commands.

        if self.game_tracked != payload.category_name and (now - self.game_updated_dt).seconds > 15:
            await channel.send(f'{const.STV.donkDetective} Game was changed to "{payload.category_name}"')

        if self.title_tracked != payload.title and (now - self.title_updated_dt).seconds > 15:
            await channel.send(f'{const.STV.DankThink} Title was changed to "{payload.title}"')

        if self.title_tracked != payload.title:
            # we need to record the title into the database
            query = """
                INSERT INTO ttv_stream_titles
                (title, edit_time)
                VALUES ($1, $2)
                ON CONFLICT (title) DO
                    UPDATE SET edit_time = $2;
            """
            await self.bot.pool.execute(query, payload.title, now)

        self.game_tracked = payload.category_name
        self.title_tracked = payload.title

    @commands.Cog.event(event="event_eventsub_notification_stream_end")  # type: ignore # lib issue
    async def clear_the_database(self, _: eventsub.NotificationEvent) -> None:
        """Clear the database from old enough titles.

        I guess stream end is a good event for it - it's rare enough and we don't need old titles after stream is over.
        """
        cutoff_dt = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=2)
        query = "DELETE FROM ttv_stream_titles WHERE edit_time < $1"
        await self.bot.pool.execute(query, cutoff_dt)


def prepare(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    bot.add_cog(ChannelManagement(bot))
