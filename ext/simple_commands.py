from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import twitchio  # noqa: TCH002
from twitchio.ext import commands

import config
from bot import IrenesCog
from utils import checks, const, formats

if TYPE_CHECKING:
    from bot import IrenesBot


class DefaultCommands(IrenesCog):
    """Simple commands.

    Simple in a sense that they are just somewhat static;
    Probably a better name would be "uncategorised custom commands"
    because they are defined here in code, instead of
    sitting in the database like commands from `custom_commands.py` do.
    """

    # 1. TEMPORARY COMMANDS

    @commands.command()
    async def erdoc(self, ctx: commands.Context) -> None:
        await ctx.send("docs.google.com/document/d/1o4RFCGdgFsCuNQMc9zXx9iJGY--WLJjaPqdH4_YkOLk/edit?usp=sharing")

    @commands.command()
    async def run(self, ctx: commands.Context) -> None:
        msg = (
            "All Bosses & MiniBosses, Charmless. For details about routing/plan/strategies look for AB&M section "
            "of this !sekirodoc: "
            "docs.google.com/document/d/1rjp7lhvP0vwwlO7bC7TyFAjKcGDovFuo2EYUaX66QiA/edit?usp=sharing "  # cSpell: ignore vwwl
            "It's my first ever hitless run, so there is a lot to learn."
        )
        await ctx.send(msg)

    @commands.command()
    async def sekirodoc(self, ctx: commands.Context) -> None:
        await ctx.send("docs.google.com/document/d/1rjp7lhvP0vwwlO7bC7TyFAjKcGDovFuo2EYUaX66QiA/edit?usp=sharing")

    # 2. MORE OR LESS STABLE COMMANDS
    # (sorted alphabetically)

    @commands.command()
    async def clip(self, ctx: commands.Context) -> None:
        """Create a clip for last 30 seconds of the stream."""
        streamer = await ctx.channel.user()
        clip = await streamer.create_clip(config.TTG_ACCESS_TOKEN)
        await ctx.send(f"https://clips.twitch.tv/{clip["id"]}")
        # now = datetime.datetime.now(datetime.UTC)
        #  new_clips = await streamer.fetch_clips(started_at=now)

    @commands.command()
    async def discord(self, ctx: commands.Context) -> None:
        """Discord"""
        await ctx.send(f"{const.STV.Discord} discord.gg/K8FuDeP")

    @commands.command()
    async def donate(self, ctx: commands.Context) -> None:
        """Donate"""
        await ctx.send("donationalerts.com/r/irene_adler__")

    @commands.command()
    async def followage(self, ctx: commands.Context) -> None:
        """Followage"""
        await ctx.send("Just click your name 4Head")

    @commands.command(aliases=["hi", "yo"])
    async def hello(self, ctx: commands.Context) -> None:
        """Hello"""
        await ctx.send(f"{const.STV.Hello} @{ctx.author.name} {const.STV.yo}")

    @commands.command()
    async def lurk(self, ctx: commands.Context) -> None:
        """Lurk"""
        try:
            mention = ctx.author.mention  # type: ignore
        except:
            mention = f"@{ctx.author.name}"
        await ctx.send(f"{mention} is now lurking {const.STV.DankLurk} Have fun {const.STV.donkHappy}")

    @commands.command()
    async def nomic(self, ctx: commands.Context) -> None:
        """No mic"""
        await ctx.send("Please read info below the stream, specifically, FAQ")

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """Ping"""
        await ctx.send("\N{TABLE TENNIS PADDLE AND BALL} Pong!")

    @commands.command()
    async def playlist(self, ctx: commands.Context) -> None:
        """Get a link to Spotify playlist"""
        await ctx.send("open.spotify.com/playlist/7fVAcuDPLVAUL8555vy8Kz?si=b26cecab2cf24608")  # cSpell: ignore DPLVAUL

    @checks.is_mod()
    @commands.command(aliases=["so"])
    async def shoutout(self, ctx: commands.Context, user: twitchio.User) -> None:
        """Shoutout"""
        streamer = await ctx.channel.user()
        await streamer.shoutout(config.TTG_IRENE_ACCESS_TOKEN, user.id, const.ID.Irene)

    @commands.command()
    async def song(self, ctx: commands.Context) -> None:
        """Get currently played song on Spotify"""
        async with self.bot.session.get(
            f"https://spotify.aidenwallis.co.uk/u/{config.SPOTIFY_AIDENWALLIS_CODE}"
        ) as resp:
            msg = await resp.text()

        if msg == "User is currently not playing any music on Spotify.":
            answer = f"{const.STV.Erm} No music is being played"
        else:
            answer = f"{const.STV.donkJam} {msg}"
        await ctx.send(answer)

    @commands.command()
    async def source(self, ctx: commands.Context) -> None:
        """Get a link to the bot's GitHub repository"""
        await ctx.send(f"{self.bot.repo} {const.STV.DankReading}")

    @commands.command()
    async def uptime(self, ctx: commands.Context) -> None:
        """Get stream uptime"""
        stream = next(iter(await self.bot.fetch_streams(user_ids=[const.ID.Irene])), None)  # None if offline
        if stream is None:
            await ctx.send(f"The stream is offline {const.STV.Offline}")
        else:
            uptime = datetime.datetime.now(datetime.UTC) - stream.started_at
            await ctx.send(f"{formats.seconds_to_words(uptime)} {const.STV.peepoDapper}")

    @commands.command()
    async def vods(self, ctx: commands.Context) -> None:
        """Get a link to youtube vods archive"""
        await ctx.send(f"youtube.com/@Aluerie_VODS/ {const.STV.Cinema}")


def prepare(bot: IrenesBot) -> None:
    bot.add_cog(DefaultCommands(bot))
