import os
import threading
import tempfile
import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime
from ntnlog.ntn_logging import Logger, _IGNORED_FILES, _IGNORED_PREFIXES
from ntnlog.ntn_config import GLOBAL_LOGGING_ENABLED, GLOBAL_LOG_TRACING_ENABLED


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

from contextlib import contextmanager

@contextmanager
def _in_temp_dir():
    """Context manager: chdir into a fresh temp dir, restore cwd on exit."""
    original = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        try:
            yield tmp
        finally:
            os.chdir(original)


def _make_logger(log_dir="logs", **kwargs):
    """Return a Logger using a relative log_dir (cwd must already be the temp dir)."""
    return Logger(log_dir=log_dir, **kwargs)


def _read_log(log_dir="logs"):
    """Read all content from the log file written into log_dir (relative to cwd)."""
    files = [f for f in os.listdir(log_dir) if f.endswith(".txt")]
    assert files, "No log file was created"
    with open(os.path.join(log_dir, files[0])) as f:
        return f.read()


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

class TestInit:
    def test_defaults(self):
        log = Logger()
        assert log._enable is True
        assert log._enable_log_tracing is False
        assert log._log_dir == "logs"
        assert log._project_dir is None
        assert log._name is None

    def test_name_stored(self):
        log = Logger(name="app")
        assert log._name == "app"

    def test_name_none_by_default(self):
        log = Logger()
        assert log._name is None

    def test_project_dir_stored_as_abspath(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Logger(project_dir=tmp)
            assert log._project_dir == os.path.abspath(tmp)

    def test_project_dir_none_stays_none(self):
        log = Logger(project_dir=None)
        assert log._project_dir is None

    def test_custom_log_dir(self):
        log = Logger(log_dir="custom_logs")
        assert log._log_dir == "custom_logs"

    def test_lock_created(self):
        log = Logger()
        assert isinstance(log._lock, type(threading.Lock()))


# ---------------------------------------------------------------------------
# enable_logging / enable_log_tracing
# ---------------------------------------------------------------------------

class TestEnableControls:
    def test_enable_logging_false(self):
        log = Logger()
        log.enable_logging(False)
        assert log._enable is False

    def test_enable_logging_true(self):
        log = Logger()
        log.enable_logging(False)
        log.enable_logging(True)
        assert log._enable is True

    def test_enable_log_tracing_true(self):
        log = Logger()
        log.enable_log_tracing(True)
        assert log._enable_log_tracing is True

    def test_enable_log_tracing_false(self):
        log = Logger()
        log.enable_log_tracing(True)
        log.enable_log_tracing(False)
        assert log._enable_log_tracing is False

    def test_disable_does_not_write(self):
        log = Logger()
        log.enable_logging(False)
        with patch("builtins.open") as mock_open:
            log.log("silent")
            mock_open.assert_not_called()

    def test_global_disable_does_not_write(self):
        log = Logger()
        with patch("ntnlog.ntn_logging.GLOBAL_LOGGING_ENABLED", False):
            with patch("builtins.open") as mock_open:
                log.log("silent")
                mock_open.assert_not_called()

    def test_both_disabled_does_not_write(self):
        log = Logger()
        log.enable_logging(False)
        with patch("ntnlog.ntn_logging.GLOBAL_LOGGING_ENABLED", False):
            with patch("builtins.open") as mock_open:
                log.log("silent")
                mock_open.assert_not_called()


# ---------------------------------------------------------------------------
# Log output format
# ---------------------------------------------------------------------------

class TestLogFormat:
    def test_no_name_format(self):
        with _in_temp_dir():
            log = _make_logger()
            log.log("hello")
            content = _read_log()
            assert "hello" in content

    def test_named_logger_bracket_in_output(self):
        with _in_temp_dir():
            log = _make_logger(name="myapp")
            log.log("hello")
            content = _read_log()
            assert "[myapp]" in content

    def test_named_logger_bracket_before_caller(self):
        with _in_temp_dir():
            log = _make_logger(name="svc")
            log.log("hello")
            content = _read_log()
            # Format: [timestamp][svc][caller] message
            name_pos = content.index("[svc]")
            caller_pos = content.index("]", name_pos + 1)
            assert name_pos < caller_pos

    def test_unnamed_logger_no_extra_bracket(self):
        with _in_temp_dir():
            log = _make_logger()
            log.log("hello")
            content = _read_log()
            log_line = [l for l in content.splitlines() if "hello" in l][0]
            # [timestamp][caller] — exactly 2 opening brackets
            assert log_line.count("[") == 2

    def test_named_logger_three_brackets(self):
        with _in_temp_dir():
            log = _make_logger(name="x")
            log.log("hello")
            content = _read_log()
            log_line = [l for l in content.splitlines() if "hello" in l][0]
            assert log_line.count("[") == 3

    def test_header_written_on_first_entry(self):
        with _in_temp_dir():
            log = _make_logger()
            log.log("first")
            content = _read_log()
            assert "Log file created on" in content

    def test_header_not_duplicated_on_second_entry(self):
        with _in_temp_dir():
            log = _make_logger()
            log.log("first")
            log.log("second")
            content = _read_log()
            assert content.count("Log file created on") == 1

    def test_multiline_message_indented(self):
        with _in_temp_dir():
            log = _make_logger()
            log.log("line1\nline2")
            content = _read_log()
            assert "line1" in content
            assert "line2" in content

    def test_timestamp_format_in_output(self):
        import re
        with _in_temp_dir():
            log = _make_logger()
            log.log("ts test")
            content = _read_log()
            assert re.search(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]", content)


# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------

class TestConsoleOutput:
    def test_print_to_console_prints_message(self):
        log = Logger()
        with patch("builtins.open", MagicMock()):
            with patch("ntnlog.ntn_logging.file_verify_path", return_value="/tmp"):
                with patch("builtins.print") as mock_print:
                    log.log("hello", print_to_console=True)
                    mock_print.assert_called_once_with("hello")

    def test_print_to_console_uses_custom_message(self):
        log = Logger()
        with patch("builtins.open", MagicMock()):
            with patch("ntnlog.ntn_logging.file_verify_path", return_value="/tmp"):
                with patch("builtins.print") as mock_print:
                    log.log("hello", print_to_console=True, console_message="CUSTOM")
                    mock_print.assert_called_once_with("CUSTOM")

    def test_no_console_output_by_default(self):
        log = Logger()
        with patch("builtins.open", MagicMock()):
            with patch("ntnlog.ntn_logging.file_verify_path", return_value="/tmp"):
                with patch("builtins.print") as mock_print:
                    log.log("hello")
                    mock_print.assert_not_called()

    def test_empty_console_message_falls_back_to_message(self):
        log = Logger()
        with patch("builtins.open", MagicMock()):
            with patch("ntnlog.ntn_logging.file_verify_path", return_value="/tmp"):
                with patch("builtins.print") as mock_print:
                    log.log("hello", print_to_console=True, console_message="")
                    mock_print.assert_called_once_with("hello")


# ---------------------------------------------------------------------------
# __call__ shorthand
# ---------------------------------------------------------------------------

class TestCallable:
    def test_call_delegates_to_log(self):
        log = Logger()
        with patch.object(log, "log") as mock_log:
            log("msg", print_to_console=True, console_message="c")
            mock_log.assert_called_once_with("msg", print_to_console=True, console_message="c")

    def test_call_default_args(self):
        log = Logger()
        with patch.object(log, "log") as mock_log:
            log("msg")
            mock_log.assert_called_once_with("msg", print_to_console=False, console_message="")


# ---------------------------------------------------------------------------
# Frame filtering (_is_project_frame)
# ---------------------------------------------------------------------------

class TestIsProjectFrame:
    def test_frozen_prefix_always_rejected(self):
        log = Logger()
        for prefix in _IGNORED_PREFIXES:
            assert log._is_project_frame(f"{prefix}importlib") is False

    def test_ignored_file_rejected_in_blocklist_mode(self):
        log = Logger()
        for fname in _IGNORED_FILES:
            assert log._is_project_frame(f"/some/path/{fname}") is False

    def test_non_ignored_file_accepted_in_blocklist_mode(self):
        log = Logger()
        assert log._is_project_frame("/project/myapp.py") is True

    def test_project_dir_allowlist_accepts_inside(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Logger(project_dir=tmp)
            assert log._is_project_frame(os.path.join(tmp, "app.py")) is True

    def test_project_dir_allowlist_rejects_outside(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Logger(project_dir=tmp)
            assert log._is_project_frame("/other/project/app.py") is False

    def test_project_dir_allowlist_rejects_site_packages(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Logger(project_dir=tmp)
            site_pkg_path = os.path.join(tmp, "lib/site-packages/somelib.py")
            assert log._is_project_frame(site_pkg_path) is False

    def test_frozen_rejected_even_in_allowlist_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Logger(project_dir=tmp)
            assert log._is_project_frame("<frozen importlib>") is False


# ---------------------------------------------------------------------------
# get_caller_info
# ---------------------------------------------------------------------------

class TestGetCallerInfo:
    def test_returns_unknown_when_no_frames(self):
        log = Logger()
        with patch.object(log, "_collect_project_frames", return_value=[]):
            assert log.get_caller_info() == "unknown:0"

    def test_returns_first_frame_when_tracing_off(self):
        log = Logger()
        log.enable_log_tracing(False)
        with patch.object(log, "_collect_project_frames", return_value=["a.py:1", "b.py:2"]):
            assert log.get_caller_info() == "a.py:1"

    def test_returns_chain_when_tracing_on(self):
        log = Logger()
        log.enable_log_tracing(True)
        with patch("ntnlog.ntn_logging.GLOBAL_LOG_TRACING_ENABLED", True):
            with patch.object(log, "_collect_project_frames", return_value=["a.py:1", "b.py:2"]):
                assert log.get_caller_info() == "a.py:1>b.py:2"

    def test_tracing_disabled_globally_returns_first_frame(self):
        log = Logger()
        log.enable_log_tracing(True)
        with patch("ntnlog.ntn_logging.GLOBAL_LOG_TRACING_ENABLED", False):
            with patch.object(log, "_collect_project_frames", return_value=["a.py:1", "b.py:2"]):
                assert log.get_caller_info() == "a.py:1"

    def test_single_frame_no_chain_separator(self):
        log = Logger()
        log.enable_log_tracing(True)
        with patch("ntnlog.ntn_logging.GLOBAL_LOG_TRACING_ENABLED", True):
            with patch.object(log, "_collect_project_frames", return_value=["a.py:5"]):
                result = log.get_caller_info()
                assert ">" not in result
                assert result == "a.py:5"


# ---------------------------------------------------------------------------
# _collect_project_frames exception handling
# ---------------------------------------------------------------------------

class TestCollectProjectFrames:
    def test_skips_frame_on_index_error(self):
        log = Logger()
        bad_frame = MagicMock()
        with patch("ntnlog.ntn_logging.stack", return_value=[bad_frame]):
            with patch("ntnlog.ntn_logging.getframeinfo", side_effect=IndexError):
                result = log._collect_project_frames()
                assert result == []

    def test_skips_frame_on_type_error(self):
        log = Logger()
        bad_frame = MagicMock()
        with patch("ntnlog.ntn_logging.stack", return_value=[bad_frame]):
            with patch("ntnlog.ntn_logging.getframeinfo", side_effect=TypeError):
                result = log._collect_project_frames()
                assert result == []


# ---------------------------------------------------------------------------
# _write_to_file: bail on error path
# ---------------------------------------------------------------------------

class TestWriteToFile:
    def test_bails_when_path_is_error_string(self):
        log = Logger()
        with patch("ntnlog.ntn_logging.file_verify_path", return_value="Error: something went wrong"):
            with patch("builtins.open") as mock_open:
                log._write_to_file("entry\n", "2026-01-01", "10:00:00")
                mock_open.assert_not_called()

    def test_creates_log_dir_if_missing(self):
        with _in_temp_dir():
            log = _make_logger(log_dir="new_logs")
            log.log("test")
            assert os.path.isdir("new_logs")


# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------

class TestThreadSafety:
    def test_concurrent_writes_do_not_raise(self):
        with _in_temp_dir():
            log = _make_logger()
            errors = []

            def write():
                try:
                    for _ in range(20):
                        log.log("concurrent")
                except Exception as e:
                    errors.append(e)

            threads = [threading.Thread(target=write) for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert errors == []
