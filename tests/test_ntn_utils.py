import os
import tempfile
import pytest
from ntnlog.ntn_utils import get_working_dir, resolve_path
import ntnlog


# ---------------------------------------------------------------------------
# get_working_dir
# ---------------------------------------------------------------------------

class TestGetWorkingDir:
    def test_returns_cwd(self):
        assert get_working_dir() == os.getcwd()

    def test_returns_string(self):
        assert isinstance(get_working_dir(), str)

    def test_returns_absolute_path(self):
        assert os.path.isabs(get_working_dir())

    def test_directory_exists(self):
        assert os.path.isdir(get_working_dir())

    def test_accessible_via_ntnlog_utils(self):
        assert ntnlog.utils.get_working_dir() == os.getcwd()


# ---------------------------------------------------------------------------
# resolve_path — happy paths
# ---------------------------------------------------------------------------

class TestResolvePathValid:
    def test_simple_relative_path(self):
        result = resolve_path("logs")
        assert result == os.path.normpath(os.path.join(os.getcwd(), "logs"))

    def test_nested_relative_path(self):
        result = resolve_path("a/b/c")
        assert result == os.path.normpath(os.path.join(os.getcwd(), "a/b/c"))

    def test_current_dir_dot(self):
        result = resolve_path(".")
        assert result == os.path.normpath(os.getcwd())

    def test_absolute_path_within_cwd(self):
        abs_path = os.path.join(os.getcwd(), "logs")
        assert resolve_path(abs_path) == os.path.normpath(abs_path)

    def test_returns_absolute_path(self):
        result = resolve_path("some/dir")
        assert os.path.isabs(result)

    def test_must_exist_false_nonexistent_ok(self):
        result = resolve_path("totally_nonexistent_xyz", must_exist=False)
        assert result.endswith("totally_nonexistent_xyz")

    def test_must_exist_true_with_existing_dir(self):
        with tempfile.TemporaryDirectory(dir=os.getcwd()) as tmp:
            name = os.path.basename(tmp)
            result = resolve_path(name, must_exist=True)
            assert result == tmp

    def test_must_exist_true_with_existing_file(self):
        with tempfile.NamedTemporaryFile(dir=os.getcwd(), delete=False) as f:
            name = os.path.basename(f.name)
        try:
            result = resolve_path(name, must_exist=True)
            assert result == os.path.join(os.getcwd(), name)
        finally:
            os.unlink(os.path.join(os.getcwd(), name))

    def test_path_with_redundant_slashes_normalised(self):
        result = resolve_path("logs//subdir")
        assert "//" not in result

    def test_subdir_dot_dot_within_cwd(self):
        # "a/../b" resolves to cwd/b — still inside cwd
        result = resolve_path("a/../logs")
        assert result == os.path.normpath(os.path.join(os.getcwd(), "logs"))

    def test_child_and_return_trip_stay_inside_when_sibling_exists(self, tmp_path, monkeypatch):
        # ``x/f`` and ``../x/f`` stay inside ``x`` even when sibling ``xy`` exists.
        x = tmp_path / "x"
        xy = tmp_path / "xy"
        x.mkdir()
        xy.mkdir()
        (x / "f").write_text("ok")
        monkeypatch.chdir(x)

        assert resolve_path("f") == os.path.normpath(os.path.join(os.getcwd(), "f"))
        assert resolve_path("../x/f") == os.path.normpath(os.path.join(os.getcwd(), "f"))

    def test_symlink_inside_cwd_allowed(self, tmp_path, monkeypatch):
        x = tmp_path / "x"
        x.mkdir()
        target = x / "data.txt"
        target.write_text("ok")
        (x / "link").symlink_to(target)
        monkeypatch.chdir(x)

        assert resolve_path("link") == os.path.normpath(os.path.join(os.getcwd(), "link"))
        assert resolve_path("link", must_exist=True) == os.path.join(os.getcwd(), "link")

    def test_accessible_via_ntnlog_utils(self):
        result = ntnlog.utils.resolve_path("logs")
        assert os.path.isabs(result)


# ---------------------------------------------------------------------------
# resolve_path — escape detection
# ---------------------------------------------------------------------------

class TestResolvePathEscape:
    def test_single_dotdot_raises(self):
        with pytest.raises(ValueError, match="escapes the working directory"):
            resolve_path("../outside")

    def test_multiple_dotdot_raises(self):
        with pytest.raises(ValueError, match="escapes the working directory"):
            resolve_path("../../etc/passwd")

    def test_absolute_path_outside_cwd_raises(self):
        with pytest.raises(ValueError, match="escapes the working directory"):
            resolve_path("/tmp/outside")

    def test_error_message_contains_original_path(self):
        with pytest.raises(ValueError, match="../bad"):
            resolve_path("../bad")

    def test_sibling_prefix_raises(self, tmp_path, monkeypatch):
        # ``/tmp/home/xy`` startswith ``/tmp/home/x``; the sibling is still outside.
        x = tmp_path / "x"
        xy = tmp_path / "xy"
        x.mkdir()
        xy.mkdir()
        (xy / "f").write_text("secret")
        monkeypatch.chdir(x)

        with pytest.raises(ValueError, match="escapes the working directory"):
            resolve_path("../xy/f")

    def test_symlink_escape_raises(self, tmp_path, monkeypatch):
        x = tmp_path / "x"
        outside = tmp_path / "outside"
        x.mkdir()
        outside.mkdir()
        target = outside / "secret"
        target.write_text("secret")
        (x / "link").symlink_to(target)
        monkeypatch.chdir(x)

        with pytest.raises(ValueError, match="escapes the working directory"):
            resolve_path("link")


# ---------------------------------------------------------------------------
# resolve_path — must_exist failures
# ---------------------------------------------------------------------------

class TestResolvePathMustExist:
    def test_raises_file_not_found_for_missing_path(self):
        with pytest.raises(FileNotFoundError):
            resolve_path("definitely_not_here_xyz123", must_exist=True)

    def test_error_message_contains_resolved_path(self):
        with pytest.raises(FileNotFoundError, match="does not exist"):
            resolve_path("not_here_xyz123", must_exist=True)
