import os
import tempfile
import pytest
from ntnlog.ntn_file_utils import (
    FileUtilsError,
    FileExecutionError,
    FileOperator,
    file_verify_path,
    file_verify_file,
)


class TestFileVerifyPath:
    def test_valid_directory(self):
        """Test verifying a valid directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            sub_dir = os.path.join(temp_dir, "test_dir")
            os.makedirs(sub_dir)
            result = file_verify_path(temp_dir, "test_dir")
            assert result == sub_dir

    def test_invalid_directory_not_exists(self):
        """Test verifying a non-existent directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = file_verify_path(temp_dir, "nonexistent")
            assert result == FileUtilsError.NOT_A_DIRECTORY.value.format(directory="nonexistent")

    def test_outside_working_directory(self):
        """Test verifying a directory outside working directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = file_verify_path(temp_dir, "../outside")
            assert result == FileUtilsError.OUTSIDE_WORKING_DIR.value.format(directory="../outside")


class TestFileVerifyFile:
    def test_valid_read_file(self):
        """Test verifying a valid file for reading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test.txt")
            with open(file_path, "w") as f:
                f.write("test")
            result = file_verify_file(temp_dir, "test.txt", FileOperator.READ_FILE)
            assert result == file_path

    def test_invalid_read_file_not_exists(self):
        """Test verifying a non-existent file for reading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = file_verify_file(temp_dir, "nonexistent.txt", FileOperator.READ_FILE)
            assert result == FileUtilsError.FILE_READ_NOT_FOUND_OR_NOT_REGULAR.value.format(file_path=os.path.join(temp_dir, "nonexistent.txt"))

    def test_outside_working_directory_read(self):
        """Test verifying a file outside working directory for reading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = file_verify_file(temp_dir, "../outside.txt", FileOperator.READ_FILE)
            expected = FileUtilsError.FILE_READ_OUTSIDE_WORKING_DIR.value.format(file_path=os.path.join(temp_dir, "../outside.txt"))
            assert result == expected

    def test_valid_write_file_new(self):
        """Test verifying a new file for writing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = file_verify_file(temp_dir, "new.txt", FileOperator.WRITE_FILE)
            assert result == os.path.join(temp_dir, "new.txt")

    def test_outside_working_directory_write(self):
        """Test verifying a file outside working directory for writing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = file_verify_file(temp_dir, "../outside.txt", FileOperator.WRITE_FILE)
            expected = FileUtilsError.FILE_WRITE_OUTSIDE_WORKING_DIR.value.format(file_path=os.path.join(temp_dir, "../outside.txt"))
            assert result == expected

    def test_valid_execute_file(self):
        """Test verifying a valid Python file for execution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test.py")
            with open(file_path, "w") as f:
                f.write("print('test')")
            result = file_verify_file(temp_dir, "test.py", FileOperator.EXECUTE_FILE)
            assert result == file_path

    def test_invalid_execute_file_not_python(self):
        """Test verifying a non-Python file for execution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test.txt")
            with open(file_path, "w") as f:
                f.write("test")
            result = file_verify_file(temp_dir, "test.txt", FileOperator.EXECUTE_FILE)
            assert result == FileUtilsError.FILE_EXECUTE_NOT_PYTHON.value.format(file_path="test.txt")

    def test_invalid_option(self):
        """Test invalid file operation option."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError, match="Invalid file operation option provided"):
                file_verify_file(temp_dir, "test.txt", "invalid")