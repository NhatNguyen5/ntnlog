# ntnlog

[![Coverage](https://NhatNguyen5.github.io/ntnlog/coverage.svg)](https://NhatNguyen5.github.io/ntnlog/)

Lightweight Python logger with timestamped file output, caller stack tracing, and working-directory-scoped file utilities. Next-To-Nothing setup — just import and log.

## Features

- **Log levels**: `TRACE`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` with per-instance and global thresholds
- **Caller stack tracing**: Automatically records where in your code a log came from
- **Timestamped file output**: Logs written to daily files with no configuration required
- **Log rotation**: Size-based rotation with configurable backup count
- **Console colorization**: ANSI color output per log level, customizable per instance
- **Exception capturing**: `exception()` attaches the active traceback automatically
- **Async support**: `alog()` and `aexception()` for async/await code
- **File utilities**: Safe, working-directory-scoped file operations with error handling
- **Thread-safe**: File writes are protected by a per-instance lock

## Installation

```bash
pip install ntnlog
```

## Quick Start

```python
from ntnlog import Logger, Level

log = Logger()

log("Application started")
log("Important message", print_to_console=True)
log("Something suspicious", level=Level.WARNING)

# Exception capturing — attaches the active traceback automatically
try:
    do_something()
except Exception:
    log.exception("Something went wrong")

# Async logging
await log.alog("Async message")
await log.aexception("Async error")

# Enable detailed call-stack tracing
log.enable_log_tracing(True)
log("Traced message")

# Named loggers — useful when multiple instances log to the same file
app_logger = Logger(name="app")
worker_logger = Logger(name="worker")
# Output: [2026-05-13 15:46:34][INFO][app][main.py:12] message
#         [2026-05-13 15:46:34][INFO][worker][worker.py:8] message

# Level filtering — string or enum, both work
log = Logger(level=Level.WARNING)
log = Logger(level="warning")

# Log rotation
log = Logger(max_bytes=5_000_000, backup_count=3)

# Console colorization
log = Logger(colorize=True)

# Custom log directory
log = Logger(log_dir="my_logs")

# Project-aware frame filtering
log = Logger(project_dir="/path/to/project")
```

## Configuration

```python
from ntnlog.ntn_config import (
    GLOBAL_LOGGING_ENABLED,
    GLOBAL_LOG_TRACING_ENABLED,
    GLOBAL_LOG_LEVEL,
    GLOBAL_MAX_BYTES,
    GLOBAL_BACKUP_COUNT,
    GLOBAL_LOG_COLORS,
)
```

| Global | Default | Description |
|---|---|---|
| `GLOBAL_LOGGING_ENABLED` | `True` | Master on/off switch for all loggers |
| `GLOBAL_LOG_TRACING_ENABLED` | `True` | Master tracing switch |
| `GLOBAL_LOG_LEVEL` | `Level.INFO` | Default minimum level when instance `level` is `None` |
| `GLOBAL_MAX_BYTES` | `10_000_000` | Default rotation threshold (10 MB) |
| `GLOBAL_BACKUP_COUNT` | `1` | Default number of backup files kept on rotation |
| `GLOBAL_LOG_COLORS` | see config | ANSI color code per level |

Per-instance controls:
```python
log.enable_logging(False)      # disable this logger
log.enable_log_tracing(True)   # enable tracing for this logger
```

## Modules

### Logger (`ntn_logging.py`)
Main logging class. Writes timestamped, level-tagged entries to `./logs/<date>_logging.txt` and optionally traces the full call stack to show exactly which file and line triggered the log.

### File Utilities (`ntn_file_utils.py`)
Path and file verification scoped to the working directory:
- `file_verify_path(base, directory)` — confirms a directory exists within the working dir
- `file_verify_file(base, filename, operator)` — validates a file for read/write/execute

### Utils (`ntn_utils.py`)
Working-directory-scoped path helpers with a clean exception-based API:
- `ntnlog.utils.get_working_dir()` — returns the current working directory
- `ntnlog.utils.resolve_path(path, must_exist=False)` — resolves a path within the working directory, raises `ValueError` if it escapes

### Configuration (`ntn_config.py`)
Global flags and defaults controlling logging behaviour across all logger instances.

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
