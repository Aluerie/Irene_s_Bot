from __future__ import annotations

import platform
from pkgutil import iter_modules

__all__ = ("EXTENSIONS",)

try:
    import _test

    TEST_EXTENSIONS = _test.TEST_EXTENSIONS
    TEST_USE_ALL_EXTENSIONS = _test.TEST_USE_ALL_EXTENSIONS
except ModuleNotFoundError:
    TEST_EXTENSIONS: tuple[str, ...] = ()  # pyright: ignore[reportConstantRedefinition]
    TEST_USE_ALL_EXTENSIONS: bool = True  # pyright: ignore[reportConstantRedefinition]

# EXTENSIONS

# write extensions (!) with "ext." prefix here:
DISABLED_EXTENSIONS = (
    "ext.beta",
    "ext.dota",
)


def get_extensions() -> tuple[str, ...]:
    if platform.system() == "Windows" and not TEST_USE_ALL_EXTENSIONS:
        # assume testing specific extensions from `_test.py`
        return tuple(f"{__package__}.{ext}" for ext in TEST_EXTENSIONS)
    else:
        # assume running full bot functionality (besides `DISABLED_EXTENSIONS`)

        # I want "core_extensions" to be loaded asap
        core_extensions: tuple[str, ...] = ("ext.logs_via_webhook",)
        all_extensions = tuple(
            module.name
            for module in iter_modules(__path__, f"{__package__}.")
            if module.name not in DISABLED_EXTENSIONS
        )
        temp = tuple(set(all_extensions).difference(core_extensions))

        return core_extensions + temp


EXTENSIONS = get_extensions()
