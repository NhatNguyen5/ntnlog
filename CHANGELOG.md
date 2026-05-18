# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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