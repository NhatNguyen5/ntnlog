"""
ntnlog - Lightweight Python logger with timestamped file output,
caller stack tracing, and working-directory-scoped file utilities.
"""

from .ntn_logging import Logger
from .ntn_config import GLOBAL_LOGGING_ENABLED, GLOBAL_LOG_TRACING_ENABLED
from .ntn_file_utils import (
    FileUtilsError,
    FileExecutionError,
    FileOperator,
    file_verify_path,
    file_verify_file,
)
from . import ntn_utils as utils

__version__ = "0.2.1"
__author__ = "Nathan T Nguyen"

__all__ = [
    "Logger",
    "GLOBAL_LOGGING_ENABLED",
    "GLOBAL_LOG_TRACING_ENABLED",
    "FileUtilsError",
    "FileExecutionError",
    "FileOperator",
    "file_verify_path",
    "file_verify_file",
    "utils",
]