from __future__ import annotations

from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    import datetime


class plural:  # noqa: N801
    """Helper class to format tricky plural nouns.

    Examples: ::

        >>> format(plural(1), 'child|children')  # '1 child'
        >>> format(plural(8), 'week|weeks')  # '8 weeks'
        >>> f'{plural(3):reminder}' # 3 reminders
    """

    # licensed MPL v2 from Rapptz/RoboDanny
    # https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/utils/formats.py

    def __init__(self, value: int) -> None:
        self.value: int = value

    @override
    def __format__(self, format_spec: str) -> str:
        v = self.value
        singular, separator, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if abs(v) != 1:
            return f"{v} {plural}"
        return f"{v} {singular}"


def seconds_to_words(delta: datetime.timedelta) -> str:
    total_seconds = int(delta.total_seconds())

    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)

    timeunit_dict = {"hour": hours, "minute": minutes, "second": seconds}
    return " ".join(format(plural(number), word) for word, number in timeunit_dict.items() if number)
