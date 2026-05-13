"""
Logging Module - A comprehensive logging and file utility package.

This module provides:
- Logging configuration and management
- File utilities for logging operations
- Tracing and debug capabilities
"""

from .my_logging import logger
from .config import LOGGING_ENABLED, LOG_TRACING_ENABLED
from .file_utils import (
    FileUtilsError,
    FileExecutionError,
    FileOperator,
    file_verify_path,
    file_verify_file,
)

__version__ = "0.1.0"
__author__ = "Your Name"

__all__ = [
    "logger",
    "LOGGING_ENABLED",
    "LOG_TRACING_ENABLED",
    "FileUtilsError",
    "FileExecutionError",
    "FileOperator",
    "file_verify_path",
    "file_verify_file",
]
