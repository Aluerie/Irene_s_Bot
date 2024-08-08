from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Embed

from bot import IrenesCog, irenes_routine
from utils import const

if TYPE_CHECKING:
    from bot import IrenesBot


class SevenTV(IrenesCog):
    def __init__(self, bot: IrenesBot) -> None:
        super().__init__(bot)
        self.check_emotes.start()

    async def send_error_embed(self, emote: str, service: str, colour: int) -> None:
        content = const.ERROR_ROLE_MENTION
        embed = Embed(
            title=f"Problem with {service} emotes",
            description=f"Looks like emote `{emote}` is no longer present in the channel.",
            colour=colour,
        ).set_footer(text="but it was previously used for @Irene_s_Bot emotes")
        await self.bot.exc_manager.error_webhook.send(content=content, embed=embed)

    @irenes_routine(hours=23, minutes=59, wait_first=True)
    async def check_emotes(self) -> None:
        # SEVEN TV
        async with self.bot.session.get(f"https://7tv.io/v3/users/twitch/{const.ID.Irene}") as resp:
            stv_json = await resp.json()
            stv_emote_list = [emote["name"] for emote in stv_json["emote_set"]["emotes"]]

        for emote in const.STV:
            if emote not in stv_emote_list:
                await self.send_error_embed(emote, "7TV", 0x3493EE)

        # FFZ
        async with self.bot.session.get(f"https://api.frankerfacez.com/v1/room/id/{const.ID.Irene}") as resp:
            ffz_json = await resp.json()
            # if we ever need this "654554" then it exists as `ffz_json["room"]["set"]`
            ffz_emote_list = [emote["name"] for emote in ffz_json["sets"]["654554"]["emoticons"]]

        for emote in const.FFZ:
            if emote not in ffz_emote_list:
                await self.send_error_embed(emote, "FFZ", 0x271F3E)

        # BTTV

        async with self.bot.session.get(f"https://api.betterttv.net/3/cached/users/twitch/{const.ID.Irene}") as resp:
            bttv_json = await resp.json()
            bttv_emote_list = [emote["code"] for emote in bttv_json["channelEmotes"] + bttv_json["sharedEmotes"]]

        for emote in const.BTTV:
            if emote not in bttv_emote_list:
                await self.send_error_embed(emote, "BTTV", 0xD50014)


def prepare(bot: IrenesBot) -> None:
    bot.add_cog(SevenTV(bot))
