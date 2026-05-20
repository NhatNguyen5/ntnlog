# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.1] - 2026-05-20
### Changed
- Updated PyPI short description to reflect v0.4.0 features (log levels, rotation, colorization, async support)

## [0.4.0] - 2026-05-20
### Added
- `Level` enum (`TRACE=5`, `DEBUG=10`, `INFO=20`, `WARNING=30`, `ERROR=40`, `CRITICAL=50`) — an `IntEnum` so levels compare and sort numerically
- Per-instance level threshold via `Logger(level=...)` — entries below the threshold are silently dropped; falls back to `GLOBAL_LOG_LEVEL` when `None`
- `GLOBAL_LOG_LEVEL` config constant (default `Level.INFO`) used when no instance level is set
- String coercion for `level=` parameter — accepts case-insensitive strings (`"warning"`, `"WARN"`, etc.) in addition to `Level` members; `"WARN"` is an accepted alias for `WARNING`
- `[LEVEL]` field in log output format between the timestamp and the optional name bracket
- `exception()` method — writes a log entry and appends the currently active traceback; safe to call outside an `except` block (writes message only)
- `alog()` async method — offloads `log()` to a thread via `asyncio.to_thread` so the event loop is not blocked
- `aexception()` async method — captures `sys.exc_info()` in the calling coroutine before offloading to a thread (thread-local `exc_info` would otherwise be empty in the worker)
- Size-based log rotation — `Logger(max_bytes=..., backup_count=...)` rotates the log file when it exceeds `max_bytes`, shifting backups and deleting the oldest beyond `backup_count`; `backup_count=0` deletes without keeping backups
- `GLOBAL_MAX_BYTES` (default `10_000_000`) and `GLOBAL_BACKUP_COUNT` (default `1`) config constants used as fallbacks when instance values are `None`
- Per-instance console colorization via `Logger(colorize=True)` — wraps stdout output in ANSI color codes; file output is never colorized
- `colors` constructor parameter — `dict[int, str]` of per-level ANSI overrides merged on top of `GLOBAL_LOG_COLORS`
- `GLOBAL_LOG_COLORS` config constant mapping each `Level` to a default ANSI color code
- Automated coverage reporting: `pytest-cov` runs on every `pytest` call; CI deploys an HTML report and SVG badge to GitHub Pages on push to `main`

### Changed
- `level` is now the last positional parameter on `log()`, `__call__`, `exception()`, `alog()`, and `aexception()` — `print_to_console` remains second, `console_message` third
- Test suite expanded from 102 to 224 tests; three tests that previously passed vacuously were corrected to assert actual behaviour

## [0.3.0] - 2026-05-18
### Added
- `name` parameter on `Logger` for multi-instance identification — named loggers include a `[name]` bracket in every log entry between the timestamp and caller info
- `ntnlog.utils` submodule with `get_working_dir()` and `resolve_path()` — working-directory-scoped path helpers with an exception-based API
- GitHub Actions workflow to auto-update the GitHub wiki whenever source files change
- `WIKI.md` as the authoritative wiki source, published as the Home page

### Changed
- Package renamed from `logging-module` to `ntnlog` — install name and import name now match (`pip install ntnlog` / `import ntnlog`)
- Source files renamed to `ntn_` prefix (`ntn_logging.py`, `ntn_config.py`, `ntn_file_utils.py`)
- Test suite expanded from 25 to 102 tests with full edge case coverage

## [0.2.1] - 2026-05-17
### Changed
- Corrected package description to accurately reflect the module's scope: removed unsupported FastAPI claim, replaced overstated "error tracking" with accurate description of file-operation error handling

## [0.2.0] - 2026-05-17
### Added
- GitHub Actions publish workflow with PyPI Trusted Publishing (no API tokens required)
- GitHub Actions test workflow with Python 3.10–3.14 matrix CI
- `CHANGELOG.md` to track all releases going forward

### Changed
- Removed legacy `setup.py`; packaging is fully managed by `pyproject.toml`

## [0.1.3] - 2026-05-17
### Added
- `Logger` class with optional call-stack tracing
- `file_verify_path` and `file_verify_file` utilities
- Thread-safe file writes via `threading.Lock`
- Allowlist and blocklist strategies for filtering framework frames
- `project_dir` constructor parameter to scope caller info to project code
- GitHub Actions workflows for testing and PyPI publishing
- `[dev]` extras group for pytest

### Fixed
- Double `datetime.now()` call that could split date and time across midnight
- `WRITE_FILE` match arm silently returning `None` instead of resolved path
- Broken `__all__` exports in `__init__.py` (`LOGGING_ENABLED` → `GLOBAL_LOGGING_ENABLED`)
- Fragile double `open()` replaced with single append-mode open
- `calldepth` magic number replaced with stack-walking frame filter

### Changed
- Class renamed from `logger` to `Logger` (PEP 8)
- Hardcoded `./logs` path replaced with configurable `log_dir` parameter
- `time` variable renamed to `time_str` to avoid shadowing built-in

## [0.1.2] - 2026-05-15
### Fixed
- Initial bug fixes and refactoring

## [0.1.1] - 2026-05-15
### Added
- Initial release