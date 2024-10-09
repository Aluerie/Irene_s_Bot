from __future__ import annotations

from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    import datetime


class plural:  # noqa: N801
    """Helper class to format tricky number + singular/plural noun situations.

    Returns a human-readable string combining number and a proper noun.
    `format_spec` in this case is supposed to list both singular/plural forms with a separator "|".
    See examples.

    Examples
    --------
        >>> format(plural(1), 'child|children')  # '1 child'
        >>> format(plural(8), 'week|weeks')  # '8 weeks'
        >>> f'{plural(3):reminder}' # 3 reminders

    """

    # licensed MPL v2 from Rapptz/RoboDanny
    # https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/utils/formats.py

    def __init__(self, number: int) -> None:
        self.number: int = number

    @override
    def __format__(self, format_spec: str) -> str:
        number = self.number
        singular, separator, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if abs(number) != 1:
            return f"{number} {plural}"
        return f"{number} {singular}"


def timedelta_to_words(delta: datetime.timedelta, *, accuracy: int = 2, full_words: bool = True) -> str:
    """Convert `datetime.timedelta` to a string of humanly readable words.

    Example:
    -------
        >>> x = datetime.timedelta(seconds=66)
        >>> timedelta_to_words(x)
        >>> "1 minute 6 seconds"

    """
    total_seconds = int(delta.total_seconds())

    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    if full_words:
        timeunit_dict = {"days": days, "hour": hours, "minute": minutes, "second": seconds}
        output = [format(plural(number), word) for word, number in timeunit_dict.items() if number]
        return " ".join(output[:accuracy])
    else:
        timeunit_dict = {"d": days, "h": hours, "m": minutes, "s": seconds}
        output = [f"{number}{letter}" for letter, number in timeunit_dict.items() if number]
        return "".join(output[:accuracy])


def ordinal(n: int | str) -> str:
    """Convert an integer into its ordinal representation, i.e. 0->'0th', '3'->'3rd'."""
    # Remember that there is always funny lambda possibility
    # ```py
    # ordinal = lambda n: "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])
    # print([ordinal(n) for n in range(1,32)])
    # ```
    n = int(n)
    suffix = "th" if 11 <= n % 100 <= 13 else ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix
