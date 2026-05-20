"""
ntnlog - Lightweight Python logger with timestamped file output,
caller stack tracing, and working-directory-scoped file utilities.
"""

from .ntn_levels import Level
from .ntn_logging import Logger
from .ntn_config import (
    GLOBAL_LOGGING_ENABLED,
    GLOBAL_LOG_TRACING_ENABLED,
    GLOBAL_LOG_LEVEL,
    GLOBAL_MAX_BYTES,
    GLOBAL_BACKUP_COUNT,
    GLOBAL_LOG_COLORS,
)
from .ntn_file_utils import (
    FileUtilsError,
    FileExecutionError,
    FileOperator,
    file_verify_path,
    file_verify_file,
)
from . import ntn_utils as utils

__version__ = "0.4.1"
__author__ = "Nathan T Nguyen"

__all__ = [
    "Level",
    "Logger",
    "GLOBAL_LOGGING_ENABLED",
    "GLOBAL_LOG_TRACING_ENABLED",
    "GLOBAL_LOG_LEVEL",
    "GLOBAL_MAX_BYTES",
    "GLOBAL_BACKUP_COUNT",
    "GLOBAL_LOG_COLORS",
    "FileUtilsError",
    "FileExecutionError",
    "FileOperator",
    "file_verify_path",
    "file_verify_file",
    "utils",
]
