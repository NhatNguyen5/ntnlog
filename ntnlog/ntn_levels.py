from enum import IntEnum
from typing import Literal, TypeAlias


class Level(IntEnum):
    """
    Severity levels for log entries, ordered from lowest to highest.

    Members
    -------
    TRACE    :  5  — Fine-grained diagnostic noise, below DEBUG.
    DEBUG    : 10  — Development-time diagnostics.
    INFO     : 20  — Normal operational messages.
    WARNING  : 30  — Something unexpected but recoverable.
    ERROR    : 40  — A failure that needs attention.
    CRITICAL : 50  — A severe failure; the process may not be able to continue.
    """

    TRACE    = 5
    DEBUG    = 10
    INFO     = 20
    WARNING  = 30
    ERROR    = 40
    CRITICAL = 50


LevelStr: TypeAlias = Literal["TRACE", "DEBUG", "INFO", "WARNING", "WARN", "ERROR", "CRITICAL"]
LevelLike: TypeAlias = Level | LevelStr
