#######################################################################
#
# Logging Module Configuration
#
# Configuration for logging and tracing
#
#######################################################################

from typing import Final
from .ntn_levels import Level

GLOBAL_LOGGING_ENABLED: Final[bool] = True
"""Master on/off switch. When ``False``, all ``Logger`` instances are silenced."""

GLOBAL_LOG_TRACING_ENABLED: Final[bool] = True
"""When ``True``, call-stack tracing is enabled for instances that opt in via
``enable_log_tracing(True)``."""

GLOBAL_LOG_LEVEL: Final[Level] = Level.INFO
"""Minimum severity threshold applied to every ``Logger`` instance that has no
instance-level *level* set. Entries below this level are silently dropped."""

GLOBAL_MAX_BYTES: Final[int] = 10_000_000
"""Maximum size of a single log file in bytes (default 10 MB) before rotation."""

GLOBAL_BACKUP_COUNT: Final[int] = 1
"""Number of rotated backup files to keep alongside the active log file.
``0`` deletes the active file on rotation instead of renaming it."""

GLOBAL_LOG_COLORS: Final[dict[int, str]] = {
    Level.TRACE:    "\033[37m",   # white
    Level.DEBUG:    "\033[36m",   # cyan
    Level.INFO:     "\033[32m",   # green
    Level.WARNING:  "\033[33m",   # yellow
    Level.ERROR:    "\033[31m",   # red
    Level.CRITICAL: "\033[35m",   # magenta
}
"""ANSI color codes used for console output when ``colorize=True``.
Keys are ``int(Level)`` values; values are ANSI escape sequences."""
