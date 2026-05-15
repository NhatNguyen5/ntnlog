"""
Logging Module - A comprehensive logging and file utility package.

This module provides:
- Logging configuration and management
- File utilities for logging operations
- Tracing and debug capabilities
"""

from .my_logging import Logger
from .config import GLOBAL_LOGGING_ENABLED, GLOBAL_LOG_TRACING_ENABLED
from .file_utils import (
    FileUtilsError,
    FileExecutionError,
    FileOperator,
    file_verify_path,
    file_verify_file,
)

__version__ = "0.1.2"
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
]