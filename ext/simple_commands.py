from __future__ import annotations

import asyncio
import datetime
import random
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

    @commands.command(name="commands", aliases=["help"])
    async def command_list(self, ctx: commands.Context) -> None:
        """Commands"""
        await ctx.send('Not implemented yet, for now use "!cmd list"')

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
    async def love(self, ctx: commands.Context, *, arg: str) -> None:
        """Love"""

        def choose_love_emote() -> tuple[int, str]:
            love = random.randint(0, 100)
            if love < 10:
                emote = const.STV.donkSad
            if love < 33:
                emote = const.STV.sadKEK
            elif love < 66:
                emote = const.STV.donkHappy
            elif love < 88:
                emote = const.STV.widepeepoHappyRightHeart
            else:
                emote = const.STV.DankL
            return love, emote

        author_mention = ctx.author.mention  # type: ignore
        chatter = ctx.channel.get_chatter(arg.lstrip("@"))

        if not chatter:
            # NOT USER, just object case
            love, emote = choose_love_emote()
            await ctx.send(f"{love}% love between {author_mention} & {arg} {emote}")
            return

        chatter_display_name = getattr(chatter, "display_name")
        if not chatter_display_name:
            chatter = await chatter.user()
            chatter_display_name = chatter.display_name

        if chatter_display_name.lower() in const.Bots:
            await ctx.send("Silly organic, bots cannot know love BibleThump")
        elif chatter.name == ctx.author.name:
            await ctx.send("pls")
        elif chatter.name == const.Name.Irene:
            await ctx.send(f"The {author_mention}'s love for our beloved Irene transcends all")
        else:
            love, emote = choose_love_emote()
            await ctx.send(f"{love}% love between {author_mention} and @{chatter_display_name} {emote}")

    @commands.command(aliases=["lorem", "ipsum"])
    async def loremipsum(self, ctx: commands.Context) -> None:
        """Lorem ipsum"""
        await ctx.send(  # cSpell:disable
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero. "
            "Sed cursus ante dapibus diam. Sed nisi. Nulla quis sem at nibh elementum imperdiet. "
            "Duis sagittis ipsum. Praesent mauris. Fusce nec tellus sed augue semper porta. Mauris massa. "
            "Vestibulum lacinia arcu eget nulla. Class aptent taciti sociosqu ad litora torquent per conubia nostra, "
            "per inceptos himenaeos. Curabitur sodales ligula in libero. Sed dignissim lacinia nunc. Curabitur tortor. "
            "Pellentesque nibh."
        )  # cSpell:enable

    @commands.command()
    async def lurk(self, ctx: commands.Context) -> None:
        """Lurk"""
        try:
            mention = ctx.author.mention  # type: ignore
        except:
            mention = f"@{ctx.author.name}"
        await ctx.send(f"{mention} is now lurking {const.STV.DankLurk} Have fun {const.STV.donkHappy}")

    @commands.command(name="decide", aliases=["ball", "8ball", "answer", "question", "yesno"])
    async def magic_ball(self, ctx: commands.Context, *, text: str | None = None) -> None:
        """Magic Ball"""
        if not text:
            await ctx.send(f"Wrong command usage! You need to ask the bot yes/no question with it {const.FFZ.peepoWTF}")
            return

        options = [
            "69% for sure",
            "Are you kidding?!",
            "Ask again",
            "Better not tell you now",
            "Definitely... not",
            "Don't bet on it",
            "don't count on it",
            "Doubtful",
            "For sure",
            "Forget about it",
            "Hah!",
            "Hells no.",
            "If the Twitch gods grant it",
            "Impossible!In due time",
            "Indubitably!",
            "It is certain",
            "It is so",
            "Leaning towards no",
            "Look deep in your heart and you will see the answer",
            "Most definitely",
            "Most likely",
            "My sources say yes",
            "Never",
            "No wais",
            "No way!",
            "No.",
            "Of course!",
            "Outlook good",
            "Outlook not so good",
            "Perhaps",
            "Possibly",
            "Please.",
            "That's a tough one",
            "That's like totally a yes. Duh!",
            "The answer might not be not no",
            "The answer to that isn't pretty",
            "The heavens point to yes",
            "Who knows?",
            "Without a doubt",
            "Yesterday it would've been a yes, but today it's a yep",
            "You will have to wait",
        ]
        await ctx.send(random.choice(options))

    @commands.command()
    async def nomic(self, ctx: commands.Context) -> None:
        """No mic"""
        await ctx.send("Please read info below the stream, specifically, FAQ")

    @commands.command()
    async def oversight(self, ctx: commands.Context) -> None:
        """Oversight"""
        await ctx.send(
            "The biggest🙌💯oversight🔭🔍with Dark✊🏾Willow🌳is that she's unbelievably sexy🤤💦🍆. "
            "I can't go on a hour🕐of my day🌞without thinking💭💦about plowing👉👌🚜that tight😳wooden🌳ass💦🍑. "
            "I'd kill🔫😱a man👨 in cold❄️blood😈just to spend💷a minute⏱️with her crotch🍑😫grinding against "
            "my throbbing💦🍆💦manhood💦🍆💦as she whispers🙊😫terribly dirty💩💩things to me in her "
            "geographically🌍🌎ambiguous🌏🗺️accent 🇮🇪"
        )

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """Ping"""
        await ctx.send("\N{TABLE TENNIS PADDLE AND BALL} Pong!")

    @commands.command()
    async def playlist(self, ctx: commands.Context) -> None:
        """Get a link to Spotify playlist"""
        await ctx.send("open.spotify.com/playlist/7fVAcuDPLVAUL8555vy8Kz?si=b26cecab2cf24608")  # cSpell: ignore DPLVAUL

    @commands.cooldown(rate=1, per=60, bucket=commands.Bucket.channel)
    @commands.command(aliases=["rr", "russianroulette"])
    async def roulette(self, ctx: commands.Context) -> None:
        """Russian roulette"""
        mention: str = ctx.author.mention  # type: ignore
        user_id: int = ctx.author.id  # type: ignore # in reality it's str and timeout accepts it just fine

        for phrase in [
            f"/me places the revolver to {mention}'s head {const.FFZ.monkaGIGAGUN}",
            f"{const.DIGITS[3]} {const.Global.monkaS} ... ",
            f"{const.DIGITS[2]} {const.FFZ.monkaH} ... ",
            f"{const.DIGITS[1]} {const.FFZ.monkaGIGA} ... The trigger is pulled... ",
        ]:
            await ctx.send(phrase)
            await asyncio.sleep(0.77)

        if ctx.author.is_mod:  # type: ignore
            # Special case: we will not kill any moderators
            await ctx.send(f"Revolver malfunctions! {mention} is miraculously alive! {const.STV.PogChampPepe}")
        elif random.randint(0, 1):
            await ctx.send(f"Revolver clicks! {mention} has lived to survive roulette! {const.STV.POGCRAZY}")
        else:
            await ctx.send(f"Revolver fires! {mention} lies dead in chat {const.STV.Deadge}")
            streamer = await ctx.channel.user()
            await streamer.timeout_user(config.TTG_ACCESS_TOKEN, const.ID.Bot, user_id, 30, "Lost in !russianroulette")

    @checks.is_mod()
    @commands.command(aliases=["so"])
    async def shoutout(self, ctx: commands.Context, user: twitchio.User) -> None:
        """Shoutout"""
        streamer = await ctx.channel.user()
        await streamer.shoutout(config.TTG_IRENE_ACCESS_TOKEN, user.id, const.ID.Irene)

    @commands.command()
    async def song(self, ctx: commands.Context) -> None:
        """Get currently played song on Spotify"""
        url = f"https://spotify.aidenwallis.co.uk/u/{config.SPOTIFY_AIDENWALLIS_CODE}"
        async with self.bot.session.get(url) as resp:
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
        streamer = await ctx.channel.user()
        stream = next(iter(await self.bot.fetch_streams(user_ids=[streamer.id])), None)  # None if offline
        if stream is None:
            await ctx.send(f"The stream is offline {const.STV.Offline}")
        else:
            uptime = datetime.datetime.now(datetime.UTC) - stream.started_at
            await ctx.send(f"{formats.seconds_to_words(uptime)} {const.STV.peepoDapper}")

    @commands.command(aliases=["seppuku"])
    async def vanish(self, ctx: commands.Context) -> None:
        """Vanish"""
        if ctx.author.is_mod:  # type: ignore
            if "seppuku" in ctx.message.content:  # type: ignore
                msg = f"Emperor Kappa does not allow you this honor, {ctx.author.mention} (bcs you're a moderator)"  # type: ignore
            else:
                msg = "Moderators can't vanish"
            await ctx.send(msg)
        else:
            user_id: int = ctx.author.id  # type: ignore # in reality it's str and timeout accepts it just fine
            streamer = await ctx.channel.user()
            await streamer.timeout_user(config.TTG_ACCESS_TOKEN, const.ID.Bot, user_id, 1, "Used vanish")

    @commands.command()
    async def vods(self, ctx: commands.Context) -> None:
        """Get a link to youtube vods archive"""
        await ctx.send(f"youtube.com/@Aluerie_VODS/ {const.STV.Cinema}")


def prepare(bot: IrenesBot) -> None:
    bot.add_cog(DefaultCommands(bot))
