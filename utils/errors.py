"""CUSTOM ERRORS.

All exceptions raised by me should be defined in this file.
It's just my small code practice.
"""

from __future__ import annotations


class IrenesBotError(Exception):
    """The base exception for Irene's Bot. All other exceptions should inherit from this."""

    __slots__: tuple[str, ...] = ()


class TranslateError(IrenesBotError):
    """Raised when there is an error in translate functionality."""

    def __init__(self, status_code: int, text: str) -> None:
        self.status_code: int = status_code
        self.text: str = text
        super().__init__(f"Google Translate responded with HTTP Status Code {status_code}")


class CheckError(IrenesBotError):
    """My own `commands.CheckFailure` Error.

    Used in my own command checks.
    """

    __slots__: tuple[str, ...] = ()
