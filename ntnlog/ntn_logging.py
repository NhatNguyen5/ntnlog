#######################################################################
#
# My Logging Module
#
# Provides logging functionality with timestamping and caller info
# Supports configurable logging and tracing options
#
#######################################################################

import os
import threading
from datetime import datetime
from .ntn_file_utils import FileUtilsError, file_verify_path
from inspect import getframeinfo, stack
from .ntn_config import GLOBAL_LOGGING_ENABLED, GLOBAL_LOG_TRACING_ENABLED


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
        log.log("Something happened", print_to_console=True, console_message="Hey!")

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
    """

    DEFAULT_LOG_DIR = "logs"

    def __init__(
        self,
        log_dir: str = DEFAULT_LOG_DIR,
        project_dir: str | None = None,
        name: str | None = None,
    ):
        self._enable: bool = True
        self._enable_log_tracing: bool = False
        self._log_dir: str = log_dir
        self._project_dir: str | None = (
            os.path.abspath(project_dir) if project_dir is not None else None
        )
        self._name: str | None = name
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def __call__(
        self,
        message: str,
        print_to_console: bool = False,
        console_message: str = "",
    ) -> None:
        self.log(message, print_to_console=print_to_console, console_message=console_message)

    def log(
        self,
        message: str,
        print_to_console: bool = False,
        console_message: str = "",
    ) -> None:
        if not GLOBAL_LOGGING_ENABLED or not self._enable:
            return

        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        timestamp = f"{date} {time_str}"

        name_segment = f"[{self._name}]" if self._name else ""
        logistic_data = f"[{timestamp}]{name_segment}[{self.get_caller_info()}]"
        padded_space = "".rjust(len(logistic_data) + 1)
        formatted_message = str(message).replace("\n", f"\n{padded_space}")
        log_entry = f"{logistic_data} {formatted_message}\n"

        self._write_to_file(log_entry, date, time_str)

        if print_to_console:
            print(message if console_message == "" else console_message)

    def enable_logging(self, enable_logging: bool) -> None:
        self._enable = enable_logging

    def enable_log_tracing(self, enable_log_tracing: bool) -> None:
        self._enable_log_tracing = enable_log_tracing

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
        with self._lock:
            with open(file_name, "a") as log_file:
                # Write a header only on the very first entry (empty file)
                if log_file.tell() == 0:
                    log_file.write(f"Log file created on {date} at {time_str}\n")
                log_file.write(log_entry)