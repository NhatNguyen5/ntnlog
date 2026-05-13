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
    OUTSIDE_WORKING_DIR = 'Error: Cannot list {directory} as it is outside the permitted working directory'
    NOT_A_DIRECTORY = 'Error: {directory} is not a directory'
    # File related errors
    # Read file errors
    FILE_READ_OUTSIDE_WORKING_DIR = 'Error: Cannot read {file_path} as it is outside the permitted working directory'
    FILE_READ_NOT_FOUND_OR_NOT_REGULAR = 'Error: File not found or is not a regular file: "{file_path}"'
    # Write file errors
    FILE_WRITE_OUTSIDE_WORKING_DIR = 'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    FILE_WRITE_NOT_FOUND_OR_NOT_REGULAR = 'Error: File not found or is not a regular file: "{file_path}"\n    Create the file before writing to it.'
    # Executable file errors
    FILE_EXECUTE_OUTSIDE_WORKING_DIR = 'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    FILE_EXECUTE_NOT_FOUND_OR_NOT_REGULAR = 'Error: File "{file_path}" not found.'
    FILE_EXECUTE_NOT_PYTHON = 'Error: File "{file_path}" is not a Python file.'

class FileExecutionError(str, Enum):
    EXECUTION_FAILED = 'Error: executing Python file: {error_message}'
    EXECUTION_TIMEOUT = 'Error: Execution of file "{file_path}" timed out after {timeout} seconds.'

class FileOperator(str, Enum):
    READ_FILE = 'read_file'
    WRITE_FILE = 'write_file'
    EXECUTE_FILE = 'execute_file'

def file_verify_path(working_directory, directory):
    path_to_directory = os.path.join(working_directory, directory)
    verify_result = path_to_directory
    if not path_to_directory.startswith(working_directory) or ".." in os.path.relpath(path_to_directory, working_directory):   
        verify_result = FileUtilsError.OUTSIDE_WORKING_DIR.value.format(directory=directory)
    
    if not os.path.isdir(path_to_directory):
        verify_result = FileUtilsError.NOT_A_DIRECTORY.value.format(directory=directory)

    return verify_result

def file_verify_file(working_directory, file, options=None):
    path_to_file = os.path.join(working_directory, file)
    verify_result = path_to_file
    match options:
        case FileOperator.READ_FILE:
            if not path_to_file.startswith(working_directory) or ".." in os.path.relpath(path_to_file, working_directory):   
                verify_result = FileUtilsError.FILE_READ_OUTSIDE_WORKING_DIR.value.format(file_path=path_to_file)
            
            if not os.path.isfile(path_to_file):
                verify_result = FileUtilsError.FILE_READ_NOT_FOUND_OR_NOT_REGULAR.value.format(file_path=path_to_file)
        case FileOperator.WRITE_FILE:
            if not path_to_file.startswith(working_directory) or ".." in os.path.relpath(path_to_file, working_directory):
                verify_result = FileUtilsError.FILE_WRITE_OUTSIDE_WORKING_DIR.value.format(file_path=path_to_file)

            # For write operations, allow creating new files. The caller should ensure
            # the parent directory exists (or create it) before writing. Here we only
            # validate that the file path is within the working directory and return
            # the resolved path so the writer can open/create the file.

        case FileOperator.EXECUTE_FILE:
            if not path_to_file.startswith(working_directory) or ".." in os.path.relpath(path_to_file, working_directory):
                verify_result = FileUtilsError.FILE_EXECUTE_OUTSIDE_WORKING_DIR.value.format(file_path=file)
            
            if not os.path.isfile(path_to_file):
                verify_result = FileUtilsError.FILE_EXECUTE_NOT_FOUND_OR_NOT_REGULAR.value.format(file_path=file)

            if not path_to_file.endswith('.py'):
                verify_result = FileUtilsError.FILE_EXECUTE_NOT_PYTHON.value.format(file_path=file)

        case _:
            raise ValueError("Invalid file operation option provided.")

    return verify_result