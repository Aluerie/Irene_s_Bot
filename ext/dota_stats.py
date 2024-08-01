from twitchio.ext import commands


class DotaStats(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def mmr(self, ctx: commands.Context) -> None:
        await ctx.send("Not implemented yet!")


def prepare(bot: commands.Bot) -> None:
    bot.add_cog(DotaStats(bot))
