#######################################################################
#
# My Logging Module
#
# Provides logging functionality with timestamping and caller info
# Supports configurable logging and tracing options
#
#######################################################################

import asyncio
import os
import sys
import traceback
import threading
from datetime import datetime
from .ntn_file_utils import FileUtilsError, file_verify_path
from inspect import getframeinfo, stack
from .ntn_levels import Level, LevelLike

from .ntn_config import (
    GLOBAL_LOGGING_ENABLED,
    GLOBAL_LOG_TRACING_ENABLED,
    GLOBAL_LOG_LEVEL,
    GLOBAL_MAX_BYTES,
    GLOBAL_BACKUP_COUNT,
    GLOBAL_LOG_COLORS,
)

_ANSI_RESET = "\033[0m"


# ---------------------------------------------------------------------------
# Frame-filtering constants
# ---------------------------------------------------------------------------

# Prefixes of filenames/paths to always skip (logger internals, frozen frames)
_IGNORED_PREFIXES = (
    "<frozen",
    "<string>",
)

# Basenames of framework/infra files to skip (blocklist fallback mode)
_IGNORED_FILES = {
    "spawn.py",
    "process.py",
    "_subprocess.py",
    "server.py",
    "runners.py",
    "config.py",
    "importer.py",
    "__init__.py",
    "cli.py",
    "discover.py",
    "ntn_logging.py",  # skip this file itself
    "ntn_utils.py",
}

# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

class Logger:
    """
    Lightweight file logger with optional call-stack tracing.

    Usage
    -----
        log = Logger()
        log("Something happened")
        log.log("Something happened", console_message="Hey!")

    Parameters
    ----------
    log_dir : str
        Directory (relative or absolute) where log files are written.
        Defaults to ``./logs``.
    project_dir : str | None
        Root of your project source tree. When supplied, only frames whose
        absolute path starts with this directory (and are not inside
        ``site-packages``) are considered "your code". When ``None`` the
        module falls back to the blocklist defined by ``_IGNORED_FILES`` /
        ``_IGNORED_PREFIXES``.
    name : str | None
        Optional label for this logger instance. Appears as a bracket segment
        in every log entry.
    level : Level | str | None
        Minimum level threshold for this instance. Accepts a ``Level`` member
        or a case-insensitive string name (e.g. ``"warn"``, ``"WARNING"``).
        Entries below this level are silently dropped. When ``None``,
        ``GLOBAL_LOG_LEVEL`` is used.
    colorize : bool
        When ``True``, console output is wrapped in ANSI color codes taken
        from *colors* (or ``GLOBAL_LOG_COLORS`` when *colors* is ``None``).
        File output is never colorized.
    colors : dict[int, str] | None
        Per-instance color map keyed by ``int(Level)``. Merged on top of
        ``GLOBAL_LOG_COLORS`` at construction time; missing entries fall back
        to the global value.
    """

    DEFAULT_LOG_DIR = "logs"

    _LEVEL_ALIASES: dict[str, str] = {"WARN": "WARNING"}

    @staticmethod
    def _parse_level(value: "Level | str | None") -> "Level | None":
        if value is None:
            return None
        if isinstance(value, Level):
            return value
        name = str(value).upper()
        name = Logger._LEVEL_ALIASES.get(name, name)
        try:
            return Level[name]
        except KeyError:
            valid = [lvl.name for lvl in Level]
            raise ValueError(f"Unknown log level {value!r}. Valid levels: {valid}")

    def __init__(
        self,
        log_dir: str = DEFAULT_LOG_DIR,
        project_dir: str | None = None,
        name: str | None = None,
        level: "Level | str | None" = None,
        max_bytes: int | None = None,
        backup_count: int | None = None,
        colorize: bool = False,
        colors: dict[int, str] | None = None,
    ):
        self._enable: bool = True
        self._enable_log_tracing: bool = False
        self._log_dir: str = log_dir
        self._project_dir: str | None = (
            os.path.abspath(project_dir) if project_dir is not None else None
        )
        self._name: str | None = name
        self._level: Level | None = self._parse_level(level)
        self._max_bytes: int | None = max_bytes
        self._backup_count: int | None = backup_count
        self._colorize: bool = colorize
        self._colors: dict[int, str] = {**GLOBAL_LOG_COLORS, **(colors or {})}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def __call__(
        self,
        message: str,
        level: LevelLike = Level.INFO,
        console_message: str | None = None,
    ) -> None:
        """
        Write a log entry. Alias for :meth:`log`.

        Parameters
        ----------
        message : str
            Text to write to the log file.
        level : LevelLike
            Severity of this entry. Accepts a ``Level`` enum member or a
            case-insensitive string: ``"TRACE"`` (5), ``"DEBUG"`` (10),
            ``"INFO"`` (20), ``"WARNING"`` (30), ``"ERROR"`` (40),
            ``"CRITICAL"`` (50).
        console_message : str | None
            When ``None`` (default), nothing is printed to stdout.
            When ``""`` (empty string), prints *message* to stdout.
            When any other string, prints that string to stdout instead of *message*.
        """
        self.log(message, level=level, console_message=console_message)

    def log(
        self,
        message: str,
        level: LevelLike = Level.INFO,
        console_message: str | None = None,
    ) -> None:
        """
        Write a log entry.

        Parameters
        ----------
        message : str
            Text to write to the log file.
        level : LevelLike
            Severity of this entry. Accepts a ``Level`` enum member or a
            case-insensitive string: ``"TRACE"`` (5), ``"DEBUG"`` (10),
            ``"INFO"`` (20), ``"WARNING"`` (30), ``"ERROR"`` (40),
            ``"CRITICAL"`` (50).
        console_message : str | None
            When ``None`` (default), nothing is printed to stdout.
            When ``""`` (empty string), prints *message* to stdout.
            When any other string, prints that string to stdout instead of *message*.
        """
        if isinstance(level, str):
            level = self._parse_level(level) or Level.INFO

        if not GLOBAL_LOGGING_ENABLED or not self._enable:
            return

        threshold = self._level if self._level is not None else GLOBAL_LOG_LEVEL
        if level < threshold:
            return

        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        timestamp = f"{date} {time_str}"

        name_segment  = f"[{self._name}]" if self._name else ""
        level_segment = f"[{level.name}]"
        logistic_data = f"[{timestamp}]{level_segment}{name_segment}[{self.get_caller_info()}]"
        padded_space = "".rjust(len(logistic_data) + 1)
        formatted_message = str(message).replace("\n", f"\n{padded_space}")
        log_entry = f"{logistic_data} {formatted_message}\n"

        self._write_to_file(log_entry, date, time_str)

        if console_message is not None:
            text = message if console_message == "" else console_message
            if self._colorize:
                color = self._colors.get(int(level), "")
                text = f"{color}{text}{_ANSI_RESET}"
            print(text)

    def enable_logging(self, enable_logging: bool) -> None:
        self._enable = enable_logging

    def enable_log_tracing(self, enable_log_tracing: bool) -> None:
        self._enable_log_tracing = enable_log_tracing

    def exception(
        self,
        message: str,
        level: LevelLike = Level.ERROR,
        console_message: str | None = None,
    ) -> None:
        """
        Log the current exception with a traceback appended.

        Parameters
        ----------
        message : str
            Text prepended to the traceback in the log entry.
        level : LevelLike
            Severity of this entry. Accepts a ``Level`` enum member or a
            case-insensitive string: ``"TRACE"`` (5), ``"DEBUG"`` (10),
            ``"INFO"`` (20), ``"WARNING"`` (30), ``"ERROR"`` (40),
            ``"CRITICAL"`` (50).
        console_message : str | None
            When ``None`` (default), nothing is printed to stdout.
            When ``""`` (empty string), prints *message* to stdout.
            When any other string, prints that string to stdout instead of *message*.
        """
        if sys.exc_info()[0] is None:
            tb_text = ""
        else:
            tb_text = "\n" + traceback.format_exc().rstrip()
        self.log(
            f"{message}{tb_text}",
            level=level,
            console_message=console_message,
        )

    async def alog(
        self,
        message: str,
        level: LevelLike = Level.INFO,
        console_message: str | None = None,
    ) -> None:
        """
        Async version of :meth:`log`.

        Parameters
        ----------
        message : str
            Text to write to the log file.
        level : LevelLike
            Severity of this entry. Accepts a ``Level`` enum member or a
            case-insensitive string: ``"TRACE"`` (5), ``"DEBUG"`` (10),
            ``"INFO"`` (20), ``"WARNING"`` (30), ``"ERROR"`` (40),
            ``"CRITICAL"`` (50).
        console_message : str | None
            When ``None`` (default), nothing is printed to stdout.
            When ``""`` (empty string), prints *message* to stdout.
            When any other string, prints that string to stdout instead of *message*.
        """
        await asyncio.to_thread(
            self.log, message, level, console_message
        )

    async def aexception(
        self,
        message: str,
        level: LevelLike = Level.ERROR,
        console_message: str | None = None,
    ) -> None:
        """
        Async version of :meth:`exception`.

        Parameters
        ----------
        message : str
            Text prepended to the traceback in the log entry.
        level : LevelLike
            Severity of this entry. Accepts a ``Level`` enum member or a
            case-insensitive string: ``"TRACE"`` (5), ``"DEBUG"`` (10),
            ``"INFO"`` (20), ``"WARNING"`` (30), ``"ERROR"`` (40),
            ``"CRITICAL"`` (50).
        console_message : str | None
            When ``None`` (default), nothing is printed to stdout.
            When ``""`` (empty string), prints *message* to stdout.
            When any other string, prints that string to stdout instead of *message*.
        """
        # Capture traceback now — sys.exc_info() is thread-local and will be
        # empty inside the worker thread spawned by asyncio.to_thread().
        if sys.exc_info()[0] is None:
            tb_text = ""
        else:
            tb_text = "\n" + traceback.format_exc().rstrip()
        await asyncio.to_thread(
            self.log,
            f"{message}{tb_text}",
            level,
            console_message,
        )

    # ------------------------------------------------------------------
    # Caller info
    # ------------------------------------------------------------------

    def get_caller_info(self) -> str:
        tracing_active = GLOBAL_LOG_TRACING_ENABLED and self._enable_log_tracing
        frames = self._collect_project_frames()

        if not frames:
            return "unknown:0"

        if not tracing_active:
            return frames[0]

        return ">".join(frames)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _is_project_frame(self, filename: str) -> bool:
        """
        Return True when *filename* belongs to project code.

        Allowlist mode (project_dir set):
            Frame must live inside the project directory and not inside
            a ``site-packages`` folder.

        Blocklist mode (project_dir is None):
            Frame must not match any entry in ``_IGNORED_FILES`` or
            ``_IGNORED_PREFIXES``.
        """
        # Always skip frozen / string pseudo-files regardless of mode
        if any(filename.startswith(prefix) for prefix in _IGNORED_PREFIXES):
            return False

        if self._project_dir is not None:
            abs_filename = os.path.abspath(filename)
            return (
                abs_filename.startswith(self._project_dir)
                and "site-packages" not in abs_filename
            )

        # Blocklist fallback
        return os.path.basename(filename) not in _IGNORED_FILES

    def _collect_project_frames(self) -> list[str]:
        """Walk the call stack and return frame strings for project code only."""
        frames: list[str] = []
        for frame_record in stack():
            try:
                info = getframeinfo(frame_record[0])
                if self._is_project_frame(info.filename):
                    frames.append(f"{os.path.basename(info.filename)}:{info.lineno}")
            except (IndexError, TypeError):
                # IndexError: stack shorter than expected
                # TypeError: frame_record is not subscriptable (e.g. test mocks using None)
                continue
        return frames

    def _write_to_file(self, log_entry: str, date: str, time_str: str) -> None:
        """Create the log directory/file if needed, then append *log_entry*."""
        log_dir_path = os.path.join("./", self._log_dir)

        # Ensure the log directory exists
        file_path = file_verify_path("./", self._log_dir)
        if file_path == FileUtilsError.NOT_A_DIRECTORY.value.format(directory=self._log_dir):
            os.makedirs(log_dir_path, exist_ok=True)
            file_path = file_verify_path("./", self._log_dir)  # re-verify after creation

        # Bail out if the path is still an error (e.g. outside working dir)
        if not isinstance(file_path, str) or file_path.startswith("Error"):
            return

        file_name = os.path.join(file_path, f"{date}_logging.txt")

        max_bytes    = self._max_bytes    if self._max_bytes    is not None else GLOBAL_MAX_BYTES
        backup_count = self._backup_count if self._backup_count is not None else GLOBAL_BACKUP_COUNT

        with self._lock:
            if os.path.exists(file_name) and os.path.getsize(file_name) >= max_bytes:
                if backup_count == 0:
                    os.remove(file_name)
                else:
                    oldest = f"{file_name}.{backup_count}"
                    if os.path.exists(oldest):
                        os.remove(oldest)
                    for i in range(backup_count - 1, 0, -1):
                        src = f"{file_name}.{i}"
                        dst = f"{file_name}.{i + 1}"
                        if os.path.exists(src):
                            os.rename(src, dst)
                    os.rename(file_name, f"{file_name}.1")

            with open(file_name, "a") as log_file:
                # Write a header only on the very first entry (empty file)
                if log_file.tell() == 0:
                    log_file.write(f"Log file created on {date} at {time_str}\n")
                log_file.write(log_entry)
