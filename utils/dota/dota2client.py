from __future__ import annotations

import logging
from typing import TYPE_CHECKING, override

from steam import PersonaState
from steam.ext.dota2 import Client

try:
    import config
except ImportError:
    import sys

    sys.path.append("D:/LAPTOP/AluBot")
    import config

if TYPE_CHECKING:
    from bot import IrenesBot

log = logging.getLogger(__name__)

__all__ = ("Dota2Client",)


class Dota2Client(Client):
    """Subclass for SteamIO's Client.

    Used to communicate with Dota 2 Game Coordinator in order to track information about my profile real-time.
    """

    def __init__(self, twitch_bot: IrenesBot) -> None:
        super().__init__(state=PersonaState.Invisible)
        self.twitch_bot: IrenesBot = twitch_bot

    @override
    async def login(self) -> None:
        await super().login(config.STEAM_USERNAME, config.STEAM_PASSWORD)

    @override
    async def on_ready(self) -> None:
        log.info("Successfully logged into Steam: %s", self.user.name)

        irene = await self.fetch_user(76561198072901893)  # todo: put steam id into config/const
        print(irene)
        print(irene.rich_presence)
