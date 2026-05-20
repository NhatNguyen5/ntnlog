# ntnlog

[![Coverage](https://NhatNguyen5.github.io/ntnlog/coverage.svg)](https://NhatNguyen5.github.io/ntnlog/)

Lightweight Python logger with timestamped file output, caller stack tracing, and working-directory-scoped file utilities. Next-To-Nothing setup — just import and log.

## Features

- **Caller stack tracing**: Automatically records where in your code a log came from
- **Timestamped file output**: Logs written to daily files with no configuration required
- **File utilities**: Safe, working-directory-scoped file operations with error handling
- **Thread-safe**: File writes are protected by a lock

## Installation

```bash
pip install ntnlog
```

## Quick Start

```python
from ntnlog import Logger

log = Logger()

log("Application started")
log("Important message", print_to_console=True)
log("Debug info", print_to_console=True, console_message="DEBUG: Debug info")

# Enable detailed call-stack tracing
log.enable_log_tracing(True)
log("Traced message")

# Named loggers — useful when multiple instances log to the same file
app_logger = Logger(name="app")
worker_logger = Logger(name="worker")
# Output: [2026-05-13 15:46:34][app][main.py:12] message
#         [2026-05-13 15:46:34][worker][worker.py:8] message

# Custom log directory
log = Logger(log_dir="my_logs")

# Project-aware frame filtering
log = Logger(project_dir="/path/to/project")
```

## Configuration

```python
from ntnlog.ntn_config import GLOBAL_LOGGING_ENABLED, GLOBAL_LOG_TRACING_ENABLED
```

- `GLOBAL_LOGGING_ENABLED`: Master on/off switch for all loggers (default: `True`)
- `GLOBAL_LOG_TRACING_ENABLED`: Master on/off switch for tracing (default: `True`)

Per-instance controls:
```python
log.enable_logging(False)      # disable this logger
log.enable_log_tracing(True)   # enable tracing for this logger
```

## Modules

### Logger (`ntn_logging.py`)
Main logging class. Writes timestamped entries to `./logs/<date>_logging.txt` and optionally traces the full call stack to show exactly which file and line triggered the log.

### File Utilities (`ntn_file_utils.py`)
Path and file verification scoped to the working directory:
- `file_verify_path(base, directory)` — confirms a directory exists within the working dir
- `file_verify_file(base, filename, operator)` — validates a file for read/write/execute

### Utils (`ntn_utils.py`)
Working-directory-scoped path helpers with a clean exception-based API:
- `ntnlog.utils.get_working_dir()` — returns the current working directory
- `ntnlog.utils.resolve_path(path, must_exist=False)` — resolves a path within the working directory, raises `ValueError` if it escapes

### Configuration (`ntn_config.py`)
Global flags controlling logging and tracing behaviour across all logger instances.

## Development

```bash
pip install -e ".[dev]"
pytest
pytest -v
pytest tests/test_ntn_logging.py
```

## License

MIT

## Author

Nathan T Nguyen
