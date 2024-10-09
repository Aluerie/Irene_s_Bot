from __future__ import annotations

import asyncio
import logging
import os
from typing import TYPE_CHECKING

from twitchio.ext import commands

from bot import IrenesCog, irenes_loop
from core import CORE_EXTENSIONS
from ext import WORK_EXTENSIONS
from utils import checks, errors

if TYPE_CHECKING:
    from bot import IrenesBot

log = logging.getLogger(__name__)


class Development(IrenesCog):
    """Dev Only Commands."""

    if TYPE_CHECKING:
        ext_alias_mapping: dict[str, str]

    def __init__(self, bot: IrenesBot) -> None:
        super().__init__(bot)
        self.create_ext_aliases.start()

    @irenes_loop(count=1)
    async def create_ext_aliases(self) -> None:
        core_mapping = {ext.removeprefix("core."): ext for ext in CORE_EXTENSIONS}
        work_mapping = {ext.removeprefix("ext."): ext for ext in WORK_EXTENSIONS}

        if intersection := core_mapping.keys() & work_mapping.keys():
            msg = f"We have repeating aliases for core/work extensions. Overlapping keys: {intersection}."
            raise errors.SomethingWentWrong(msg)
        else:
            self.ext_alias_mapping = core_mapping | work_mapping

    @checks.is_vps()
    @checks.is_irene()
    @commands.command(aliases=["kill"])
    async def maintenance(self, ctx: commands.Context) -> None:
        """Kill the bot process on VPS.

        Usable for bot testing so I don't have double responses.

        Note that this will turn off the whole bot functionality so things like main bot alerts will also stop.
        """
        await ctx.send("Shutting down the bot in 3 2 1")
        await asyncio.sleep(3)
        try:
            # non systemctl users - sorry
            os.system("sudo systemctl stop luebyt")
        except Exception as error:
            log.error(error, stack_info=True)
            # it might not go off
            await ctx.send("Something went wrong.")

    @checks.is_vps()
    @checks.is_irene()
    @commands.command(aliases=["restart"])
    async def reboot(self, ctx: commands.Context) -> None:
        """Restart the bot process on VPS.

        Usable to restart the bot without logging to VPS machine or committing something.
        """
        await ctx.send("Rebooting in 3 2 1")
        await asyncio.sleep(3)
        try:
            # non systemctl users - sorry
            os.system("sudo systemctl restart luebyt")
        except Exception as error:
            log.error(error, stack_info=True)
            # it might not go off
            await ctx.send("Something went wrong.")

    @checks.is_vps()
    @checks.is_irene()
    @commands.command()
    async def unload(self, ctx: commands.Context, *, extension: str) -> None:
        ext = self.ext_alias_mapping[extension.lower()]
        self.bot.unload_module(ext)
        await ctx.send(f"Successfully unloaded `{ext}`.")

    @checks.is_vps()
    @checks.is_irene()
    @commands.command()
    async def reload(self, ctx: commands.Context, *, extension: str) -> None:
        ext = self.ext_alias_mapping[extension.lower()]
        self.bot.reload_module(ext)
        await ctx.send(f"Successfully reloaded `{ext}`.")

    @checks.is_vps()
    @checks.is_irene()
    @commands.command()
    async def load(self, ctx: commands.Context, *, extension: str) -> None:
        ext = self.ext_alias_mapping[extension.lower()]
        self.bot.load_module(ext)
        await ctx.send(f"Successfully loaded `{ext}`.")


def prepare(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    bot.add_cog(Development(bot))
