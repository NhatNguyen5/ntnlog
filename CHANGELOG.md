# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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