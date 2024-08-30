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


def timedelta_to_words(delta: datetime.timedelta) -> str:
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

    timeunit_dict = {"hour": hours, "minute": minutes, "second": seconds}
    return " ".join(format(plural(number), word) for word, number in timeunit_dict.items() if number)
