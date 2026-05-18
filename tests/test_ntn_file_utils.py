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


# ---------------------------------------------------------------------------
# file_verify_path
# ---------------------------------------------------------------------------

class TestFileVerifyPath:
    def test_valid_directory_returns_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            sub = os.path.join(tmp, "sub")
            os.makedirs(sub)
            assert file_verify_path(tmp, "sub") == sub

    def test_nested_valid_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            nested = os.path.join(tmp, "a", "b")
            os.makedirs(nested)
            result = file_verify_path(tmp, "a/b")
            assert result == os.path.join(tmp, "a/b")

    def test_nonexistent_directory_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = file_verify_path(tmp, "ghost")
            assert result == FileUtilsError.NOT_A_DIRECTORY.value.format(directory="ghost")

    def test_path_is_a_file_not_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = os.path.join(tmp, "file.txt")
            open(f, "w").close()
            result = file_verify_path(tmp, "file.txt")
            assert result == FileUtilsError.NOT_A_DIRECTORY.value.format(directory="file.txt")

    def test_dotdot_escape_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = file_verify_path(tmp, "../outside")
            assert result == FileUtilsError.OUTSIDE_WORKING_DIR.value.format(directory="../outside")

    def test_deep_dotdot_escape_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = file_verify_path(tmp, "../../etc")
            assert result == FileUtilsError.OUTSIDE_WORKING_DIR.value.format(directory="../../etc")

    def test_error_strings_are_str_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = file_verify_path(tmp, "nonexistent")
            assert isinstance(result, str)


# ---------------------------------------------------------------------------
# file_verify_file — READ
# ---------------------------------------------------------------------------

class TestFileVerifyFileRead:
    def test_valid_file_returns_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = os.path.join(tmp, "data.txt")
            open(f, "w").close()
            assert file_verify_file(tmp, "data.txt", FileOperator.READ_FILE) == f

    def test_nonexistent_file_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = file_verify_file(tmp, "ghost.txt", FileOperator.READ_FILE)
            assert result == FileUtilsError.FILE_READ_NOT_FOUND_OR_NOT_REGULAR.value.format(
                file_path=os.path.join(tmp, "ghost.txt")
            )

    def test_directory_instead_of_file_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            sub = os.path.join(tmp, "subdir")
            os.makedirs(sub)
            result = file_verify_file(tmp, "subdir", FileOperator.READ_FILE)
            assert result == FileUtilsError.FILE_READ_NOT_FOUND_OR_NOT_REGULAR.value.format(
                file_path=sub
            )

    def test_dotdot_escape_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = file_verify_file(tmp, "../outside.txt", FileOperator.READ_FILE)
            assert result == FileUtilsError.FILE_READ_OUTSIDE_WORKING_DIR.value.format(
                file_path=os.path.join(tmp, "../outside.txt")
            )


# ---------------------------------------------------------------------------
# file_verify_file — WRITE
# ---------------------------------------------------------------------------

class TestFileVerifyFileWrite:
    def test_new_file_returns_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = file_verify_file(tmp, "new.txt", FileOperator.WRITE_FILE)
            assert result == os.path.join(tmp, "new.txt")

    def test_existing_file_also_returns_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = os.path.join(tmp, "existing.txt")
            open(f, "w").close()
            assert file_verify_file(tmp, "existing.txt", FileOperator.WRITE_FILE) == f

    def test_dotdot_escape_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = file_verify_file(tmp, "../outside.txt", FileOperator.WRITE_FILE)
            assert result == FileUtilsError.FILE_WRITE_OUTSIDE_WORKING_DIR.value.format(
                file_path=os.path.join(tmp, "../outside.txt")
            )

    def test_deep_dotdot_escape_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = file_verify_file(tmp, "../../bad.txt", FileOperator.WRITE_FILE)
            assert result == FileUtilsError.FILE_WRITE_OUTSIDE_WORKING_DIR.value.format(
                file_path=os.path.join(tmp, "../../bad.txt")
            )


# ---------------------------------------------------------------------------
# file_verify_file — EXECUTE
# ---------------------------------------------------------------------------

class TestFileVerifyFileExecute:
    def test_valid_python_file_returns_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = os.path.join(tmp, "script.py")
            open(f, "w").close()
            assert file_verify_file(tmp, "script.py", FileOperator.EXECUTE_FILE) == f

    def test_non_python_extension_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = os.path.join(tmp, "script.sh")
            open(f, "w").close()
            result = file_verify_file(tmp, "script.sh", FileOperator.EXECUTE_FILE)
            assert result == FileUtilsError.FILE_EXECUTE_NOT_PYTHON.value.format(file_path="script.sh")

    def test_txt_extension_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = os.path.join(tmp, "notes.txt")
            open(f, "w").close()
            result = file_verify_file(tmp, "notes.txt", FileOperator.EXECUTE_FILE)
            assert result == FileUtilsError.FILE_EXECUTE_NOT_PYTHON.value.format(file_path="notes.txt")

    def test_nonexistent_python_file_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = file_verify_file(tmp, "ghost.py", FileOperator.EXECUTE_FILE)
            assert result == FileUtilsError.FILE_EXECUTE_NOT_FOUND_OR_NOT_REGULAR.value.format(
                file_path="ghost.py"
            )

    def test_directory_with_py_name_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            sub = os.path.join(tmp, "fake.py")
            os.makedirs(sub)
            result = file_verify_file(tmp, "fake.py", FileOperator.EXECUTE_FILE)
            assert result == FileUtilsError.FILE_EXECUTE_NOT_FOUND_OR_NOT_REGULAR.value.format(
                file_path="fake.py"
            )

    def test_dotdot_escape_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = file_verify_file(tmp, "../outside.py", FileOperator.EXECUTE_FILE)
            # EXECUTE uses the relative path (file arg), not the joined absolute path
            assert result == FileUtilsError.FILE_EXECUTE_OUTSIDE_WORKING_DIR.value.format(
                file_path="../outside.py"
            )


# ---------------------------------------------------------------------------
# file_verify_file — invalid options
# ---------------------------------------------------------------------------

class TestFileVerifyFileInvalidOption:
    def test_string_invalid_option_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with pytest.raises(ValueError, match="Invalid file operation option provided"):
                file_verify_file(tmp, "test.txt", "invalid")

    def test_none_option_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with pytest.raises(ValueError, match="Invalid file operation option provided"):
                file_verify_file(tmp, "test.txt", None)

    def test_integer_option_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with pytest.raises(ValueError, match="Invalid file operation option provided"):
                file_verify_file(tmp, "test.txt", 42)


# ---------------------------------------------------------------------------
# FileUtilsError / FileExecutionError enums
# ---------------------------------------------------------------------------

class TestErrorEnums:
    def test_all_error_values_are_strings(self):
        for member in FileUtilsError:
            assert isinstance(member.value, str)

    def test_execution_error_values_are_strings(self):
        for member in FileExecutionError:
            assert isinstance(member.value, str)

    def test_file_operator_values(self):
        assert FileOperator.READ_FILE.value == "read_file"
        assert FileOperator.WRITE_FILE.value == "write_file"
        assert FileOperator.EXECUTE_FILE.value == "execute_file"

    def test_error_messages_contain_format_placeholders(self):
        formatted = FileUtilsError.NOT_A_DIRECTORY.value.format(directory="mydir")
        assert "mydir" in formatted
