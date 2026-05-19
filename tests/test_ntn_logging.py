import os
import threading
import tempfile
import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime
from ntnlog.ntn_logging import Logger, _IGNORED_FILES, _IGNORED_PREFIXES
from ntnlog.ntn_config import GLOBAL_LOGGING_ENABLED, GLOBAL_LOG_TRACING_ENABLED
from ntnlog.ntn_levels import Level


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
        from ntnlog.ntn_config import GLOBAL_LOG_COLORS
        log = Logger()
        assert log._enable is True
        assert log._enable_log_tracing is False
        assert log._log_dir == "logs"
        assert log._project_dir is None
        assert log._name is None
        assert log._level is None
        assert log._colorize is False
        assert log._colors == GLOBAL_LOG_COLORS

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

    def test_level_stored(self):
        log = Logger(level=Level.WARNING)
        assert log._level == Level.WARNING

    def test_level_none_by_default(self):
        log = Logger()
        assert log._level is None


# ---------------------------------------------------------------------------
# Logger(level=...) string coercion
# ---------------------------------------------------------------------------

class TestParseLevelInit:
    def test_level_enum_stored_directly(self):
        log = Logger(level=Level.WARNING)
        assert log._level is Level.WARNING

    def test_level_string_uppercase(self):
        log = Logger(level="WARNING")
        assert log._level is Level.WARNING

    def test_level_string_lowercase(self):
        log = Logger(level="warning")
        assert log._level is Level.WARNING

    def test_level_string_mixed_case(self):
        log = Logger(level="Warning")
        assert log._level is Level.WARNING

    def test_level_warn_alias(self):
        log = Logger(level="WARN")
        assert log._level is Level.WARNING

    def test_level_warn_alias_lowercase(self):
        log = Logger(level="warn")
        assert log._level is Level.WARNING

    def test_level_string_info(self):
        log = Logger(level="INFO")
        assert log._level is Level.INFO

    def test_level_string_error(self):
        log = Logger(level="ERROR")
        assert log._level is Level.ERROR

    def test_level_string_debug(self):
        log = Logger(level="DEBUG")
        assert log._level is Level.DEBUG

    def test_level_string_trace(self):
        log = Logger(level="TRACE")
        assert log._level is Level.TRACE

    def test_level_string_critical(self):
        log = Logger(level="CRITICAL")
        assert log._level is Level.CRITICAL

    def test_level_none_stays_none(self):
        log = Logger(level=None)
        assert log._level is None

    def test_level_invalid_string_raises(self):
        with pytest.raises(ValueError, match="Unknown log level"):
            Logger(level="VERBOSE")

    def test_level_invalid_string_mentions_valid_levels(self):
        with pytest.raises(ValueError, match="TRACE"):
            Logger(level="GARBAGE")

    def test_string_level_filters_correctly(self):
        with _in_temp_dir():
            log = _make_logger(level="ERROR")
            log.log("dropped", level=Level.WARNING)
            log.log("kept", level=Level.ERROR)
            content = _read_log()
        assert "kept" in content
        assert "dropped" not in content


# ---------------------------------------------------------------------------
# log() / __call__ / exception / alog / aexception — level is last param
# ---------------------------------------------------------------------------

class TestLevelParamOrder:
    """Verify that level sits at the end and print_to_console is still 2nd."""

    # log()

    def test_log_positional_print_to_console(self, capsys):
        with _in_temp_dir():
            log = _make_logger()
            log.log("msg", True)   # print_to_console=True, level defaults to INFO
        assert "msg" in capsys.readouterr().out

    def test_log_positional_console_message(self, capsys):
        with _in_temp_dir():
            log = _make_logger()
            log.log("msg", True, "Hey")   # print_to_console=True, console_message="Hey"
        assert "Hey" in capsys.readouterr().out

    def test_log_positional_all_params(self, capsys):
        with _in_temp_dir():
            log = _make_logger()
            log.log("msg", True, "Hey", Level.WARNING)   # all four positional
            content = _read_log()
        assert "[WARNING]" in content
        assert "Hey" in capsys.readouterr().out

    def test_log_level_keyword_still_works(self):
        with _in_temp_dir():
            log = _make_logger()
            log.log("msg", level=Level.ERROR)
            content = _read_log()
        assert "[ERROR]" in content

    def test_log_omit_level_defaults_to_info(self):
        with _in_temp_dir():
            log = _make_logger()
            log.log("msg")
            content = _read_log()
        assert "[INFO]" in content

    # __call__

    def test_call_positional_print_to_console(self, capsys):
        with _in_temp_dir():
            log = _make_logger()
            log("msg", True)
        assert "msg" in capsys.readouterr().out

    def test_call_positional_console_message(self, capsys):
        with _in_temp_dir():
            log = _make_logger()
            log("msg", True, "Hey")
        assert "Hey" in capsys.readouterr().out

    def test_call_positional_all_params(self, capsys):
        with _in_temp_dir():
            log = _make_logger()
            log("msg", True, "Hey", Level.ERROR)
            content = _read_log()
        assert "[ERROR]" in content
        assert "Hey" in capsys.readouterr().out

    def test_call_omit_level_defaults_to_info(self):
        with _in_temp_dir():
            log = _make_logger()
            log("msg")
            content = _read_log()
        assert "[INFO]" in content

    # exception()

    def test_exception_positional_print_to_console(self, capsys):
        with _in_temp_dir():
            log = _make_logger()
            try:
                raise ValueError("e")
            except ValueError:
                log.exception("msg", True)
        assert "msg" in capsys.readouterr().out

    def test_exception_positional_all_params(self):
        with _in_temp_dir():
            log = _make_logger()
            try:
                raise ValueError("e")
            except ValueError:
                log.exception("msg", False, "", Level.CRITICAL)
            content = _read_log()
        assert "[CRITICAL]" in content

    def test_exception_omit_level_defaults_to_error(self):
        with _in_temp_dir():
            log = _make_logger()
            try:
                raise ValueError("e")
            except ValueError:
                log.exception("msg")
            content = _read_log()
        assert "[ERROR]" in content

    # alog()

    def test_alog_positional_print_to_console(self, capsys):
        import asyncio
        with _in_temp_dir():
            log = _make_logger()
            asyncio.run(log.alog("msg", True))
        assert "msg" in capsys.readouterr().out

    def test_alog_positional_all_params(self):
        import asyncio
        with _in_temp_dir():
            log = _make_logger()
            asyncio.run(log.alog("msg", False, "", Level.WARNING))
            content = _read_log()
        assert "[WARNING]" in content

    def test_alog_omit_level_defaults_to_info(self):
        import asyncio
        with _in_temp_dir():
            log = _make_logger()
            asyncio.run(log.alog("msg"))
            content = _read_log()
        assert "[INFO]" in content

    # aexception()

    def test_aexception_positional_print_to_console(self, capsys):
        import asyncio
        with _in_temp_dir():
            log = _make_logger()
            try:
                raise RuntimeError("e")
            except RuntimeError:
                asyncio.run(log.aexception("msg", True))
        assert "msg" in capsys.readouterr().out

    def test_aexception_positional_all_params(self):
        import asyncio
        with _in_temp_dir():
            log = _make_logger()
            try:
                raise RuntimeError("e")
            except RuntimeError:
                asyncio.run(log.aexception("msg", False, "", Level.CRITICAL))
            content = _read_log()
        assert "[CRITICAL]" in content

    def test_aexception_omit_level_defaults_to_error(self):
        import asyncio
        with _in_temp_dir():
            log = _make_logger()
            try:
                raise RuntimeError("e")
            except RuntimeError:
                asyncio.run(log.aexception("msg"))
            content = _read_log()
        assert "[ERROR]" in content


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
            # Format: [timestamp][LEVEL][svc][caller] message
            name_pos = content.index("[svc]")
            caller_pos = content.index("]", name_pos + 1)
            assert name_pos < caller_pos

    def test_unnamed_logger_no_extra_bracket(self):
        with _in_temp_dir():
            log = _make_logger()
            log.log("hello")
            content = _read_log()
            log_line = [l for l in content.splitlines() if "hello" in l][0]
            # [timestamp][LEVEL][caller] — exactly 3 opening brackets
            assert log_line.count("[") == 3

    def test_named_logger_four_brackets(self):
        with _in_temp_dir():
            log = _make_logger(name="x")
            log.log("hello")
            content = _read_log()
            log_line = [l for l in content.splitlines() if "hello" in l][0]
            # [timestamp][LEVEL][name][caller] — exactly 4 opening brackets
            assert log_line.count("[") == 4

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
            mock_log.assert_called_once_with("msg", level=Level.INFO, print_to_console=True, console_message="c")

    def test_call_default_args(self):
        log = Logger()
        with patch.object(log, "log") as mock_log:
            log("msg")
            mock_log.assert_called_once_with("msg", level=Level.INFO, print_to_console=False, console_message="")

    def test_call_with_level(self):
        log = Logger()
        with patch.object(log, "log") as mock_log:
            log("msg", level=Level.ERROR)
            mock_log.assert_called_once_with("msg", level=Level.ERROR, print_to_console=False, console_message="")


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


# ---------------------------------------------------------------------------
# Log Levels — Level enum
# ---------------------------------------------------------------------------

class TestLevel:
    def test_trace_value(self):
        assert Level.TRACE == 5

    def test_debug_value(self):
        assert Level.DEBUG == 10

    def test_info_value(self):
        assert Level.INFO == 20

    def test_warning_value(self):
        assert Level.WARNING == 30

    def test_error_value(self):
        assert Level.ERROR == 40

    def test_critical_value(self):
        assert Level.CRITICAL == 50

    def test_ordering(self):
        assert Level.TRACE < Level.DEBUG < Level.INFO < Level.WARNING < Level.ERROR < Level.CRITICAL

    def test_is_int(self):
        assert isinstance(Level.INFO, int)

    def test_name_attribute(self):
        assert Level.ERROR.name == "ERROR"
        assert Level.WARNING.name == "WARNING"
        assert Level.INFO.name == "INFO"

    def test_importable_from_ntnlog(self):
        import ntnlog
        assert ntnlog.Level.INFO == 20


# ---------------------------------------------------------------------------
# Log Levels — filtering behavior
# ---------------------------------------------------------------------------

class TestLogLevelFiltering:
    def test_entry_below_threshold_not_written(self):
        log = Logger(level=Level.WARNING)
        with patch("builtins.open") as mock_open:
            with patch("ntnlog.ntn_logging.file_verify_path", return_value="/tmp"):
                log.log("silent", level=Level.INFO)
                mock_open.assert_not_called()

    def test_entry_at_threshold_is_written(self):
        with _in_temp_dir():
            log = _make_logger(level=Level.WARNING)
            log.log("visible", level=Level.WARNING)
            content = _read_log()
            assert "visible" in content

    def test_entry_above_threshold_is_written(self):
        with _in_temp_dir():
            log = _make_logger(level=Level.WARNING)
            log.log("critical", level=Level.CRITICAL)
            content = _read_log()
            assert "critical" in content

    def test_trace_below_info_default_not_written(self):
        log = Logger()
        with patch("builtins.open") as mock_open:
            with patch("ntnlog.ntn_logging.file_verify_path", return_value="/tmp"):
                log.log("trace msg", level=Level.TRACE)
                mock_open.assert_not_called()

    def test_info_at_default_threshold_written(self):
        with _in_temp_dir():
            log = _make_logger()
            log.log("info msg", level=Level.INFO)
            content = _read_log()
            assert "info msg" in content

    def test_global_level_used_when_instance_level_is_none(self):
        log = Logger()
        assert log._level is None
        with patch("ntnlog.ntn_logging.GLOBAL_LOG_LEVEL", Level.CRITICAL):
            with patch("builtins.open") as mock_open:
                with patch("ntnlog.ntn_logging.file_verify_path", return_value="/tmp"):
                    log.log("below", level=Level.ERROR)
                    mock_open.assert_not_called()

    def test_instance_level_overrides_global(self):
        with _in_temp_dir():
            log = _make_logger(level=Level.TRACE)
            with patch("ntnlog.ntn_logging.GLOBAL_LOG_LEVEL", Level.CRITICAL):
                log.log("trace visible", level=Level.TRACE)
            content = _read_log()
            assert "trace visible" in content


# ---------------------------------------------------------------------------
# Log Levels — output format
# ---------------------------------------------------------------------------

class TestLogLevelFormat:
    def test_level_name_in_file_output(self):
        with _in_temp_dir():
            log = _make_logger(level=Level.TRACE)
            log.log("msg", level=Level.ERROR)
            content = _read_log()
            assert "[ERROR]" in content

    def test_warning_level_name_in_output(self):
        with _in_temp_dir():
            log = _make_logger()
            log.log("msg", level=Level.WARNING)
            content = _read_log()
            assert "[WARNING]" in content

    def test_info_level_name_in_output(self):
        with _in_temp_dir():
            log = _make_logger()
            log.log("msg", level=Level.INFO)
            content = _read_log()
            assert "[INFO]" in content

    def test_trace_level_name_in_output(self):
        with _in_temp_dir():
            log = _make_logger(level=Level.TRACE)
            log.log("msg", level=Level.TRACE)
            content = _read_log()
            assert "[TRACE]" in content

    def test_level_bracket_between_timestamp_and_caller_unnamed(self):
        import re
        with _in_temp_dir():
            log = _make_logger()
            log.log("msg")
            content = _read_log()
            log_line = [l for l in content.splitlines() if "msg" in l][0]
            # [YYYY-MM-DD HH:MM:SS][LEVEL][caller] message
            assert re.match(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]\[INFO\]\[", log_line)

    def test_level_bracket_between_timestamp_and_name(self):
        import re
        with _in_temp_dir():
            log = _make_logger(name="app")
            log.log("msg")
            content = _read_log()
            log_line = [l for l in content.splitlines() if "msg" in l][0]
            # [YYYY-MM-DD HH:MM:SS][LEVEL][name][caller] message
            assert re.match(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]\[INFO\]\[app\]\[", log_line)


# ---------------------------------------------------------------------------
# Log rotation
# ---------------------------------------------------------------------------

class TestLogRotation:
    def test_rotation_creates_backup_when_size_exceeded(self):
        with _in_temp_dir():
            log = _make_logger(max_bytes=50, backup_count=1)
            # Write enough to exceed 50 bytes
            for _ in range(5):
                log.log("x" * 20)
            log_files = os.listdir("logs")
            assert any(f.endswith(".txt.1") for f in log_files)

    def test_rotation_fresh_file_has_header(self):
        with _in_temp_dir():
            log = _make_logger(max_bytes=50, backup_count=1)
            for _ in range(6):
                log.log("x" * 20)
            content = _read_log()
            assert "Log file created on" in content

    def test_no_rotation_below_threshold(self):
        with _in_temp_dir():
            log = _make_logger(max_bytes=10_000_000, backup_count=1)
            log.log("small entry")
            log_files = os.listdir("logs")
            assert not any(f.endswith(".txt.1") for f in log_files)

    def test_backup_shift_with_backup_count_2(self):
        with _in_temp_dir():
            log = _make_logger(max_bytes=50, backup_count=2)
            # Trigger two rotations
            for _ in range(12):
                log.log("x" * 20)
            log_files = os.listdir("logs")
            assert any(f.endswith(".txt.2") for f in log_files)

    def test_files_beyond_backup_count_deleted(self):
        with _in_temp_dir():
            log = _make_logger(max_bytes=50, backup_count=1)
            # Trigger enough rotations to verify no .2 is left
            for _ in range(15):
                log.log("x" * 20)
            log_files = os.listdir("logs")
            assert not any(f.endswith(".txt.2") for f in log_files)

    def test_backup_count_zero_deletes_current(self):
        with _in_temp_dir():
            log = _make_logger(max_bytes=50, backup_count=0)
            for _ in range(5):
                log.log("x" * 20)
            log_files = os.listdir("logs")
            # No .1 backup should ever be created
            assert not any(f.endswith(".txt.1") for f in log_files)
            # Current file should still exist (written after deletion)
            assert any(f.endswith(".txt") and not f.endswith(".txt.1") for f in log_files)

    def test_per_instance_max_bytes_overrides_global(self):
        with _in_temp_dir():
            # Use a tiny max_bytes to trigger rotation quickly
            log = _make_logger(max_bytes=100, backup_count=1)
            for _ in range(5):
                log.log("x" * 30)
            log_files = os.listdir("logs")
            assert any(f.endswith(".txt.1") for f in log_files)

    def test_global_max_bytes_used_when_instance_none(self):
        with _in_temp_dir():
            log = _make_logger()
            assert log._max_bytes is None
            # Write a small amount — well under 10MB global default
            log.log("small")
            log_files = os.listdir("logs")
            assert not any(f.endswith(".txt.1") for f in log_files)

    def test_rotation_thread_safe_with_tiny_max_bytes(self):
        with _in_temp_dir():
            log = _make_logger(max_bytes=100, backup_count=2)
            errors = []

            def write():
                try:
                    for _ in range(20):
                        log.log("concurrent rotation test")
                except Exception as e:
                    errors.append(e)

            threads = [threading.Thread(target=write) for _ in range(4)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert errors == []

    def test_init_stores_max_bytes_and_backup_count(self):
        log = Logger(max_bytes=512, backup_count=3)
        assert log._max_bytes == 512
        assert log._backup_count == 3

    def test_init_defaults_are_none(self):
        log = Logger()
        assert log._max_bytes is None
        assert log._backup_count is None


# ---------------------------------------------------------------------------
# Console colorization
# ---------------------------------------------------------------------------

class TestConsoleColorization:
    def test_colorize_default_is_false(self):
        log = Logger()
        assert log._colorize is False

    def test_colorize_can_be_set_true(self):
        log = Logger(colorize=True)
        assert log._colorize is True

    def test_colors_default_merges_global(self):
        from ntnlog.ntn_config import GLOBAL_LOG_COLORS
        log = Logger()
        assert log._colors == GLOBAL_LOG_COLORS

    def test_colors_custom_overrides_entry(self):
        custom = {int(Level.ERROR): "\033[91m"}
        log = Logger(colors=custom)
        assert log._colors[int(Level.ERROR)] == "\033[91m"

    def test_colors_custom_does_not_remove_other_levels(self):
        from ntnlog.ntn_config import GLOBAL_LOG_COLORS
        custom = {int(Level.ERROR): "\033[91m"}
        log = Logger(colors=custom)
        for lvl in Level:
            if int(lvl) != int(Level.ERROR):
                assert log._colors[int(lvl)] == GLOBAL_LOG_COLORS[int(lvl)]

    def test_colorize_false_no_ansi_in_console_output(self, capsys):
        with _in_temp_dir():
            log = _make_logger(colorize=False)
            log.log("plain", print_to_console=True)
        captured = capsys.readouterr()
        assert "\033[" not in captured.out

    def test_colorize_true_wraps_output_with_ansi(self, capsys):
        with _in_temp_dir():
            log = _make_logger(colorize=True)
            log.log("colorful", print_to_console=True)
        captured = capsys.readouterr()
        assert "\033[" in captured.out
        assert "\033[0m" in captured.out

    def test_colorize_uses_level_color(self, capsys):
        from ntnlog.ntn_config import GLOBAL_LOG_COLORS
        with _in_temp_dir():
            log = _make_logger(colorize=True)
            log.log("err msg", level=Level.ERROR, print_to_console=True)
        captured = capsys.readouterr()
        assert GLOBAL_LOG_COLORS[int(Level.ERROR)] in captured.out

    def test_colorize_console_message_also_colorized(self, capsys):
        with _in_temp_dir():
            log = _make_logger(colorize=True)
            log.log("msg", print_to_console=True, console_message="Hey!")
        captured = capsys.readouterr()
        assert "Hey!" in captured.out
        assert "\033[" in captured.out

    def test_colorize_does_not_write_ansi_to_file(self):
        with _in_temp_dir():
            log = _make_logger(colorize=True)
            log.log("file entry", print_to_console=False)
            content = _read_log()
        assert "\033[" not in content

    def test_colorize_reset_code_appended(self, capsys):
        with _in_temp_dir():
            log = _make_logger(colorize=True)
            log.log("reset test", print_to_console=True)
        captured = capsys.readouterr()
        assert captured.out.rstrip("\n").endswith("\033[0m")

    def test_colorize_custom_color_applied(self, capsys):
        custom_color = "\033[95m"
        with _in_temp_dir():
            log = _make_logger(colorize=True, colors={int(Level.INFO): custom_color})
            log.log("custom color", level=Level.INFO, print_to_console=True)
        captured = capsys.readouterr()
        assert custom_color in captured.out


# ---------------------------------------------------------------------------
# Exception capturing
# ---------------------------------------------------------------------------

class TestExceptionCapturing:
    def test_exception_writes_to_file(self):
        with _in_temp_dir():
            log = _make_logger()
            try:
                raise ValueError("boom")
            except ValueError:
                log.exception("caught error")
            content = _read_log()
        assert "caught error" in content

    def test_exception_includes_traceback(self):
        with _in_temp_dir():
            log = _make_logger()
            try:
                raise ValueError("boom")
            except ValueError:
                log.exception("caught error")
            content = _read_log()
        assert "Traceback" in content
        assert "ValueError" in content

    def test_exception_includes_original_message(self):
        with _in_temp_dir():
            log = _make_logger()
            try:
                raise RuntimeError("original")
            except RuntimeError:
                log.exception("wrapper message")
            content = _read_log()
        assert "wrapper message" in content

    def test_exception_outside_handler_no_traceback(self):
        with _in_temp_dir():
            log = _make_logger()
            log.exception("no active exception")
            content = _read_log()
        assert "no active exception" in content
        assert "Traceback" not in content

    def test_exception_default_level_is_error(self):
        with _in_temp_dir():
            log = _make_logger()
            try:
                raise ValueError("err")
            except ValueError:
                log.exception("level check")
            content = _read_log()
        assert "[ERROR]" in content

    def test_exception_custom_level(self):
        with _in_temp_dir():
            log = _make_logger()
            try:
                raise ValueError("err")
            except ValueError:
                log.exception("level check", level=Level.CRITICAL)
            content = _read_log()
        assert "[CRITICAL]" in content

    def test_exception_print_to_console(self, capsys):
        with _in_temp_dir():
            log = _make_logger()
            try:
                raise ValueError("err")
            except ValueError:
                log.exception("console msg", print_to_console=True)
        captured = capsys.readouterr()
        assert "console msg" in captured.out

    def test_exception_custom_console_message(self, capsys):
        with _in_temp_dir():
            log = _make_logger()
            try:
                raise ValueError("err")
            except ValueError:
                log.exception("file msg", print_to_console=True, console_message="Custom!")
        captured = capsys.readouterr()
        assert "Custom!" in captured.out

    def test_exception_respects_level_threshold(self):
        with _in_temp_dir():
            log = _make_logger(level=Level.CRITICAL)
            try:
                raise ValueError("err")
            except ValueError:
                log.exception("below threshold", level=Level.ERROR)
            # ERROR < CRITICAL so nothing should be written
            log_files = [f for f in os.listdir("logs") if f.endswith(".txt")] if os.path.exists("logs") else []
        assert log_files == []

    def test_exception_traceback_contains_line_info(self):
        with _in_temp_dir():
            log = _make_logger()
            try:
                raise TypeError("type err")
            except TypeError:
                log.exception("line info check")
            content = _read_log()
        assert "test_ntn_logging.py" in content


# ---------------------------------------------------------------------------
# Async support
# ---------------------------------------------------------------------------

import asyncio as _asyncio


class TestAsyncSupport:
    def test_alog_writes_to_file(self):
        with _in_temp_dir():
            log = _make_logger()
            _asyncio.run(log.alog("async message"))
            content = _read_log()
        assert "async message" in content

    def test_alog_default_level_is_info(self):
        with _in_temp_dir():
            log = _make_logger()
            _asyncio.run(log.alog("async info"))
            content = _read_log()
        assert "[INFO]" in content

    def test_alog_custom_level(self):
        with _in_temp_dir():
            log = _make_logger()
            _asyncio.run(log.alog("async warn", level=Level.WARNING))
            content = _read_log()
        assert "[WARNING]" in content

    def test_alog_respects_level_threshold(self):
        with _in_temp_dir():
            log = _make_logger(level=Level.ERROR)
            _asyncio.run(log.alog("below threshold", level=Level.DEBUG))
            log_files = [f for f in os.listdir("logs") if f.endswith(".txt")] if os.path.exists("logs") else []
        assert log_files == []

    def test_alog_print_to_console(self, capsys):
        with _in_temp_dir():
            log = _make_logger()
            _asyncio.run(log.alog("async console", print_to_console=True))
        captured = capsys.readouterr()
        assert "async console" in captured.out

    def test_alog_custom_console_message(self, capsys):
        with _in_temp_dir():
            log = _make_logger()
            _asyncio.run(log.alog("file msg", print_to_console=True, console_message="Hey async!"))
        captured = capsys.readouterr()
        assert "Hey async!" in captured.out

    def test_aexception_writes_to_file(self):
        with _in_temp_dir():
            log = _make_logger()
            try:
                raise ValueError("async boom")
            except ValueError:
                _asyncio.run(log.aexception("async caught"))
            content = _read_log()
        assert "async caught" in content

    def test_aexception_includes_traceback(self):
        with _in_temp_dir():
            log = _make_logger()
            try:
                raise RuntimeError("async runtime")
            except RuntimeError:
                _asyncio.run(log.aexception("async exc"))
            content = _read_log()
        assert "Traceback" in content
        assert "RuntimeError" in content

    def test_aexception_outside_handler_no_traceback(self):
        with _in_temp_dir():
            log = _make_logger()
            _asyncio.run(log.aexception("no active exc"))
            content = _read_log()
        assert "no active exc" in content
        assert "Traceback" not in content

    def test_aexception_default_level_is_error(self):
        with _in_temp_dir():
            log = _make_logger()
            try:
                raise ValueError("err")
            except ValueError:
                _asyncio.run(log.aexception("async level check"))
            content = _read_log()
        assert "[ERROR]" in content

    def test_alog_concurrent_writes_no_errors(self):
        with _in_temp_dir():
            log = _make_logger()

            async def run_many():
                await _asyncio.gather(*[log.alog(f"msg {i}") for i in range(20)])

            _asyncio.run(run_many())
            content = _read_log()
        assert content.count("msg") >= 20

    def test_alog_is_coroutine(self):
        log = Logger()
        import inspect
        assert inspect.iscoroutinefunction(log.alog)

    def test_aexception_is_coroutine(self):
        log = Logger()
        import inspect
        assert inspect.iscoroutinefunction(log.aexception)
