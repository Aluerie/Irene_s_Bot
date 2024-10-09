from __future__ import annotations

import platform
from pkgutil import iter_modules

__all__ = ("WORK_EXTENSIONS",)

try:
    import _test

    TEST_EXTENSIONS = _test.TEST_EXTENSIONS
    TEST_USE_ALL_EXTENSIONS = _test.TEST_USE_ALL_EXTENSIONS
except ModuleNotFoundError:
    _test = None
    TEST_EXTENSIONS = ()  # type: ignore
    TEST_USE_ALL_EXTENSIONS = True  # type: ignore

# EXTENSIONS

# write extensions (!) with "ext." prefix here:
DISABLED_EXTENSIONS = (
    "ext.beta",
    "ext.dota",
)


def get_extensions() -> tuple[str, ...]:
    if platform.system() == "Windows" and not TEST_USE_ALL_EXTENSIONS:
        # assume testing
        return tuple(f"{__package__}.{ext}" for ext in TEST_EXTENSIONS)
    else:
        return tuple(
            module.name
            for module in iter_modules(__path__, f"{__package__}.")
            if module.name not in DISABLED_EXTENSIONS
        )


WORK_EXTENSIONS = get_extensions()
