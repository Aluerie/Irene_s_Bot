from __future__ import annotations

from typing import TYPE_CHECKING

from twitchio.ext import commands

from bot import IrenesCog

if TYPE_CHECKING:
    from bot import IrenesBot


class DotaStats(IrenesCog):
    """Cog responsible for Dota 2 related commands.

    This functionality is supposed to be an analogy to 9kmmrbot/dotabod features.
    """

    @commands.command(aliases=["gm"])
    async def game_medals(self, ctx: commands.Context) -> None:
        """Fetch each player rank medals in the current game."""
        irene = await self.bot.dota.fetch_user(76561198072901893)  # todo: put steam id into config/const
        print(irene, f"{irene!r}")
        rich_presence = irene.rich_presence
        print(rich_presence)

        if rich_presence is None:
            await ctx.send("Sorry, couldn't fetch Irene's steam rich presence.")
            return

        watchable_game_id = rich_presence.get("WatchableGameID")
        if watchable_game_id is None:
            await ctx.send("Sorry, couldn't fetch Irene's watchable_game_id")
            return
        if watchable_game_id == "0":
            await ctx.send("Irene is not in lobby.")
            return

        watchable_game_id = int(watchable_game_id)
        live_match = next(iter(await self.bot.dota.live_matches(lobby_ids=[watchable_game_id])))

        join_parts: list[str] = []
        for player in live_match.players:
            print(f"{player!r}", type(player))
            card = await player.dota2_profile_card()
            print(card.rank_tier)
            print(card.leaderboard_rank)

            join_parts.append(f"{player.hero} - {card.rank_tier} {card.leaderboard_rank}")

        await ctx.send(", ".join(join_parts))


def prepare(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    bot.add_cog(DotaStats(bot))
