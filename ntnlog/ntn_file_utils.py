#######################################################################
#
# File Utils
#
# Utility functions for file and directory operations
# Handles path verification and error management
#
#######################################################################

import os
from enum import Enum


class FileUtilsError(str, Enum):
    # Directory related errors
    OUTSIDE_WORKING_DIR = "Error: Cannot list {directory} as it is outside the permitted working directory"
    NOT_A_DIRECTORY = "Error: {directory} is not a directory"
    # Read file errors
    FILE_READ_OUTSIDE_WORKING_DIR = "Error: Cannot read {file_path} as it is outside the permitted working directory"
    FILE_READ_NOT_FOUND_OR_NOT_REGULAR = 'Error: File not found or is not a regular file: "{file_path}"'
    # Write file errors
    FILE_WRITE_OUTSIDE_WORKING_DIR = 'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    FILE_WRITE_NOT_FOUND_OR_NOT_REGULAR = 'Error: File not found or is not a regular file: "{file_path}"\n    Create the file before writing to it.'
    # Executable file errors
    FILE_EXECUTE_OUTSIDE_WORKING_DIR = 'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    FILE_EXECUTE_NOT_FOUND_OR_NOT_REGULAR = 'Error: File "{file_path}" not found.'
    FILE_EXECUTE_NOT_PYTHON = 'Error: File "{file_path}" is not a Python file.'


class FileExecutionError(str, Enum):
    EXECUTION_FAILED = "Error: executing Python file: {error_message}"
    EXECUTION_TIMEOUT = 'Error: Execution of file "{file_path}" timed out after {timeout} seconds.'


class FileOperator(str, Enum):
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    EXECUTE_FILE = "execute_file"


def file_verify_path(working_directory: str, directory: str) -> str:
    """
    Verify that *directory* (relative to *working_directory*) exists and is
    inside the working directory.

    Returns the resolved path on success, or a ``FileUtilsError`` string on
    failure.
    """
    path_to_directory = os.path.join(working_directory, directory)
    if (
        not path_to_directory.startswith(working_directory)
        or ".." in os.path.relpath(path_to_directory, working_directory)
    ):
        return FileUtilsError.OUTSIDE_WORKING_DIR.value.format(directory=directory)

    if not os.path.isdir(path_to_directory):
        return FileUtilsError.NOT_A_DIRECTORY.value.format(directory=directory)

    return path_to_directory


def file_verify_file(working_directory: str, file: str, options: FileOperator | None = None) -> str:
    """
    Verify that *file* (relative to *working_directory*) is valid for the
    requested *options* operation.

    Returns the resolved path on success, or a ``FileUtilsError`` string on
    failure.

    Raises
    ------
    ValueError
        If *options* is not a recognised ``FileOperator`` value.
    """
    path_to_file = os.path.join(working_directory, file)

    def _is_outside() -> bool:
        return (
            not path_to_file.startswith(working_directory)
            or ".." in os.path.relpath(path_to_file, working_directory)
        )

    match options:
        case FileOperator.READ_FILE:
            if _is_outside():
                return FileUtilsError.FILE_READ_OUTSIDE_WORKING_DIR.value.format(file_path=path_to_file)
            if not os.path.isfile(path_to_file):
                return FileUtilsError.FILE_READ_NOT_FOUND_OR_NOT_REGULAR.value.format(file_path=path_to_file)

        case FileOperator.WRITE_FILE:
            if _is_outside():
                return FileUtilsError.FILE_WRITE_OUTSIDE_WORKING_DIR.value.format(file_path=path_to_file)
            # Write operations may target a not-yet-existing file; the caller is
            # responsible for creating any missing parent directories. We only
            # validate the path is inside the working directory and return it.

        case FileOperator.EXECUTE_FILE:
            if _is_outside():
                return FileUtilsError.FILE_EXECUTE_OUTSIDE_WORKING_DIR.value.format(file_path=file)
            if not os.path.isfile(path_to_file):
                return FileUtilsError.FILE_EXECUTE_NOT_FOUND_OR_NOT_REGULAR.value.format(file_path=file)
            if not path_to_file.endswith(".py"):
                return FileUtilsError.FILE_EXECUTE_NOT_PYTHON.value.format(file_path=file)

        case _:
            raise ValueError(f"Invalid file operation option provided: {options!r}")

    return path_to_file  # reached by all arms that don't return early