## Installation

```bash
pip install ntnlog
```

---

## Logger

### Constructor

```python
Logger(
    log_dir: str = "logs",
    project_dir: str | None = None,
    name: str | None = None,
    level: LevelLike | None = None,
    colorize: bool = False,
    colors: dict[int, str] | None = None,
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `log_dir` | `str` | `"logs"` | Directory where log files are written. Created automatically if it doesn't exist. |
| `project_dir` | `str` | `None` | Root of your project source tree. When set, only frames inside this directory appear in caller info. When `None`, a built-in blocklist filters out framework/infra files. |
| `name` | `str` | `None` | Optional label for this logger instance. Appears as a bracket segment in every log entry. |
| `level` | `LevelLike \| None` | `None` | Minimum level threshold for **console output only**. All entries are always written to the file. Accepts a `Level` member or a case-insensitive string (`"WARN"`, `"ERROR"`, etc.). Falls back to `GLOBAL_LOG_LEVEL` when `None`. |
| `colorize` | `bool` | `False` | Wrap console output in ANSI color codes. File output is never colorized. |
| `colors` | `dict[int, str] \| None` | `None` | Per-level ANSI color overrides. Merged on top of `GLOBAL_LOG_COLORS`; omitted levels keep the global default. Keys are `int(Level)`. |

### Output format

```
[YYYY-MM-DD HH:MM:SS][LEVEL][name][file.py:line] message
```

- `[name]` bracket is omitted when no name is set
- With tracing enabled, caller info becomes a chain: `file1.py:10>file2.py:20`
- Multi-line messages are indented to align continuation lines with the message body

**Examples:**

```
[2026-05-18 10:30:00][INFO][main.py:42] Server started
[2026-05-18 10:30:01][WARNING][app][main.py:55] Low disk space
[2026-05-18 10:30:02][ERROR][worker][worker.py:12>main.py:55] Task failed
```

### Log files

Entries are appended to `<log_dir>/<YYYY-MM-DD>_logging.txt`. A new file is created each day automatically. A header line (`Log file created on ...`) is written at the top of each new file.

### Log rotation

Rotation is configured globally via `GLOBAL_MAX_BYTES` and `GLOBAL_BACKUP_COUNT`. When a log file exceeds the threshold, it is rotated before the next write:

- The oldest backup beyond `backup_count` is deleted
- Existing backups are shifted: `.txt.1` → `.txt.2`, etc.
- The current file is renamed to `.txt.1`
- A fresh file is opened with a new header

```python
from ntnlog.ntn_config import GLOBAL_MAX_BYTES, GLOBAL_BACKUP_COUNT
# defaults: 10 MB threshold, 1 backup kept
```

Set `GLOBAL_BACKUP_COUNT = 0` to simply delete the current file on rotation (no backups kept).

---

### Methods

#### `log(message, level=Level.INFO, console_message=None)`

Write a log entry.

```python
app_log("Server started")
app_log("Request received", console_message="")           # prints full log entry to stdout
app_log("Error occurred", console_message="Check logs")   # prints override to stdout
app_log("Debug detail", Level.DEBUG)
app_log("Warning!", Level.WARNING, "Hey!")                # level + console override
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `message` | `str` | — | Message written to the log file. |
| `level` | `Level \| str` | `Level.INFO` | Level for this entry. Dropped silently if below the instance threshold. |
| `console_message` | `str \| None` | `None` | `None` — no stdout output. `""` — prints the full formatted log entry to stdout. Any other string — prints that string to stdout instead. |

#### `__call__` (shorthand)

The logger is callable — identical to `log()`:

```python
app_log("Server started")
app_log("Warning!", level=Level.WARNING)
```

#### `exception(message, level=Level.ERROR, console_message=None)`

Write a log entry and append the currently active traceback. Call from inside an `except` block; outside a handler, the message is written without a traceback.

```python
try:
    risky_operation()
except ValueError:
    app_log.exception("Validation failed")
    # Writes message + full traceback to file

app_log.exception("No active exception")
# Writes message only — no traceback appended
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `message` | `str` | — | Message written to the log file. |
| `level` | `Level \| str` | `Level.ERROR` | Level for this entry. |
| `console_message` | `str \| None` | `None` | `None` — no stdout output. `""` — prints the full formatted log entry to stdout. Any other string — prints that string to stdout instead. |

#### `alog(message, level=Level.INFO, console_message=None)` *(async)*

Async equivalent of `log()`. Offloads the file write to a thread so the event loop is not blocked.

```python
await app_log.alog("Async operation complete")
await app_log.alog("High severity", Level.CRITICAL)
```

#### `aexception(message, level=Level.ERROR, console_message=None)` *(async)*

Async equivalent of `exception()`. Captures the traceback from the calling coroutine before offloading to a thread (because `sys.exc_info()` is thread-local and would be empty inside the worker thread).

```python
try:
    await risky_coroutine()
except Exception:
    await app_log.aexception("Async task failed")
```

#### `enable_logging(enable: bool)`

Enable or disable this logger instance without affecting others.

```python
app_log.enable_logging(False)  # silence this logger
app_log.enable_logging(True)   # re-enable
```

#### `enable_log_tracing(enable: bool)`

Enable or disable full call-stack tracing for this instance.

```python
app_log.enable_log_tracing(True)
# Output: [2026-05-18 10:30:00][INFO][worker.py:8>main.py:42] message
```

Tracing is also gated by `GLOBAL_LOG_TRACING_ENABLED` — both must be `True` for the chain to appear.

---

### Level enum

```python
from ntnlog import Level

Level.TRACE     # 5
Level.DEBUG     # 10
Level.INFO      # 20
Level.WARNING   # 30
Level.ERROR     # 40
Level.CRITICAL  # 50
```

`Level` is an `IntEnum` — levels compare and sort numerically. The default threshold is `Level.INFO`, meaning `TRACE` and `DEBUG` entries are dropped unless the threshold is lowered.

String aliases accepted by `Logger(level=...)` and `log(..., level=...)`:
- Case-insensitive: `"INFO"`, `"info"`, `"Info"` all work
- `"WARN"` is the canonical string alias for `Level.WARNING`

`LevelStr` and `LevelLike` are exported from `ntnlog` for use in type annotations:

```python
from ntnlog import LevelStr, LevelLike
```

---

### Global configuration

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

| Flag | Default | Effect |
|---|---|---|
| `GLOBAL_LOGGING_ENABLED` | `True` | Master on/off switch. When `False`, all logger instances are silenced. |
| `GLOBAL_LOG_TRACING_ENABLED` | `True` | Master tracing switch. When `False`, tracing is disabled globally even if enabled per-instance. |
| `GLOBAL_LOG_LEVEL` | `Level.INFO` | Default minimum level used when a logger's `level` is `None`. |
| `GLOBAL_MAX_BYTES` | `10_000_000` | Default file size threshold for rotation (10 MB). |
| `GLOBAL_BACKUP_COUNT` | `1` | Default number of backup files kept on rotation. |
| `GLOBAL_LOG_COLORS` | see config | Default ANSI color map keyed by `int(Level)`. |

Instance-level settings always take precedence over globals when set.

### Thread safety

File writes are protected by a per-instance `threading.Lock()`. Two separate logger instances writing to the same file concurrently are **not** protected — use a single shared instance in that case.

---

## Utils

High-level, user-facing path helpers scoped to the working directory. Raises exceptions on failure (unlike the lower-level `file_verify_*` functions which return error strings).

```python
import ntnlog

root = ntnlog.utils.get_working_dir()
log_file = ntnlog.utils.resolve_path("logs/latest.log")
```

### `get_working_dir() → str`

Returns the current working directory as an absolute path (`os.getcwd()`).

### `resolve_path(path, must_exist=False) → str`

Resolves `path` relative to the working directory and verifies it stays within it.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `path` | `str` | — | Relative or absolute path to resolve. |
| `must_exist` | `bool` | `False` | If `True`, raises `FileNotFoundError` when the path doesn't exist. |

Raises `ValueError` if the path escapes the working directory via `..` traversal.

```python
import ntnlog

# Resolve a path (no existence check)
path = ntnlog.utils.resolve_path("logs/app.txt")

# Resolve and verify exists
path = ntnlog.utils.resolve_path("config.json", must_exist=True)

# Raises ValueError
path = ntnlog.utils.resolve_path("../../etc/passwd")
```

---

## File Utilities

### `file_verify_path(working_directory, directory) → str`

Verify that `directory` exists inside `working_directory`. Returns the resolved path on success, or a `FileUtilsError` string on failure.

```python
from ntnlog import file_verify_path

path = file_verify_path("./", "logs")
```

### `file_verify_file(working_directory, file, options) → str`

Verify that `file` inside `working_directory` is valid for the requested operation. Returns the resolved path on success, or a `FileUtilsError` string on failure.

```python
from ntnlog import file_verify_file, FileOperator

path = file_verify_file("./", "data.txt", FileOperator.READ_FILE)
path = file_verify_file("./", "output.txt", FileOperator.WRITE_FILE)
path = file_verify_file("./", "script.py", FileOperator.EXECUTE_FILE)
```

| `FileOperator` | Description |
|---|---|
| `READ_FILE` | File must exist and be a regular file inside the working directory. |
| `WRITE_FILE` | Path must be inside the working directory. File need not exist yet. |
| `EXECUTE_FILE` | File must exist, be a `.py` file, and be inside the working directory. |

Both functions reject paths that escape the working directory via `..` traversal.

---

## Examples

### Basic usage

```python
from ntnlog import Logger, Level

app_log = Logger()
app_log("Application started")
app_log("Request received", console_message="")   # also prints to stdout
app_log("Low memory", Level.WARNING)
```

### Multiple named loggers

```python
from ntnlog import Logger

app_logger = Logger(name="app")
worker_logger = Logger(name="worker")

app_logger("Server ready")
worker_logger("Processing task")
```

Log output:
```
[2026-05-18 10:30:00][INFO][app][main.py:6] Server ready
[2026-05-18 10:30:01][INFO][worker][main.py:7] Processing task
```

### Level filtering

`level` controls console output only — all entries are always written to the file.

```python
from ntnlog import Logger, Level

app_log = Logger(level=Level.WARNING)

# All four written to file
app_log("Debug detail", Level.DEBUG)
app_log("All good", Level.INFO)
app_log("Disk almost full", Level.WARNING)
app_log("Service crashed", Level.CRITICAL)

# Console output only for WARNING and above (when console_message is set)
app_log("Debug detail", Level.DEBUG, console_message="")    # suppressed
app_log("Disk almost full", Level.WARNING, console_message="")  # printed
```

### Exception capturing

```python
from ntnlog import Logger

app_log = Logger()

try:
    result = int("not a number")
except ValueError:
    app_log.exception("Conversion failed")
    # Writes message + full traceback including file, line, and exception type
```

### Async logging

```python
import asyncio
from ntnlog import Logger, Level

app_log = Logger()

async def handle_request():
    await app_log.alog("Handling request")
    try:
        await fetch_data()
    except Exception:
        await app_log.aexception("Fetch failed", level=Level.CRITICAL)

asyncio.run(handle_request())
```

### Log rotation

```python
import ntnlog.ntn_config as config

# Rotate at 5 MB, keep 3 backups
config.GLOBAL_MAX_BYTES   = 5_000_000
config.GLOBAL_BACKUP_COUNT = 3
# Files: log.txt, log.txt.1, log.txt.2, log.txt.3

# Rotate and delete (no backups)
config.GLOBAL_BACKUP_COUNT = 0
```

### Console colorization

```python
from ntnlog import Logger, Level

# Default ANSI colors per level
app_log = Logger(colorize=True)
app_log("All good", level=Level.INFO)       # green
app_log("Watch out", level=Level.WARNING)   # yellow
app_log("Failed", level=Level.ERROR)        # red

# Custom color for one level
app_log = Logger(colorize=True, colors={int(Level.INFO): "\033[94m"})  # bright blue INFO
```

### Call-stack tracing

```python
from ntnlog import Logger

app_log = Logger(name="api")
app_log.enable_log_tracing(True)

def handle_request():
    app_log("Handling request")

def main():
    handle_request()
```

Log output:
```
[2026-05-18 10:30:00][INFO][api][handle_request.py:5>main.py:9] Handling request
```

### Project-aware frame filtering

```python
app_log = Logger(project_dir="/path/to/my_project")
```

Only frames inside `my_project` appear in caller info — framework and library frames are excluded.
