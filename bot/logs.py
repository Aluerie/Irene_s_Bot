from __future__ import annotations

import logging
import platform
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Generator

__all__ = ("setup_logging",)

ASCII_STARTING_UP_ART = r"""
    ___ ____  _____ _   _ _____ _ ____    ____   ___ _____   ____ _____  _    ____ _____ ___ _   _  ____
|_ _|  _ \| ____| \ | | ____( ) ___|  | __ ) / _ \_   _| / ___|_   _|/ \  |  _ \_   _|_ _| \ | |/ ___|
 | || |_) |  _| |  \| |  _| |/\___ \  |  _ \| | | || |   \___ \ | | / _ \ | |_) || |  | ||  \| | |  _
 | ||  _ <| |___| |\  | |___   ___) | | |_) | |_| || |    ___) || |/ ___ \|  _ < | |  | || |\  | |_| |
|___|_| \_\_____|_| \_|_____| |____/  |____/ \___/ |_|   |____/ |_/_/   \_\_| \_\|_| |___|_| \_|\____|

                   [ IRENE_S_BOT IS STARTING NOW ]
"""


@contextmanager
def setup_logging() -> Generator[Any, Any, Any]:
    """Setup logging."""
    log = logging.getLogger()
    log.setLevel(logging.INFO)

    try:
        # Stream Handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "{asctime} | {levelname:<7} | {name:<23} | {lineno:<4} | {funcName:<30} | {message}",
            "%H:%M:%S %d/%m",
            style="{",
        )
        handler.setFormatter(formatter)
        log.addHandler(handler)

        # ensure logs folder
        Path(".temp/").mkdir(parents=True, exist_ok=True)
        # File Handler
        file_handler = RotatingFileHandler(
            filename=".temp/irenesbot.log",
            encoding="utf-8",
            mode="w",
            maxBytes=16 * 1024 * 1024,  # 16 MiB
            backupCount=2,  # Rotate through 2 files
        )
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)

        if platform.system() == "Linux":
            # so start-ups in logs are way more noticeable
            log.info(ASCII_STARTING_UP_ART)

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for h in handlers:
            h.close()
            log.removeHandler(h)
