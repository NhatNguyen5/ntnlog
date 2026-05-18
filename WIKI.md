# ntnlog

Lightweight Python logger with timestamped file output, caller stack tracing, and working-directory-scoped file utilities. Next-To-Nothing setup — just import and log.

---

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
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `log_dir` | `str` | `"logs"` | Directory where log files are written. Created automatically if it doesn't exist. |
| `project_dir` | `str` | `None` | Root of your project source tree. When set, only frames inside this directory appear in caller info. When `None`, a built-in blocklist filters out framework/infra files. |
| `name` | `str` | `None` | Optional label for this logger instance. Appears as a bracket segment in every log entry. Useful when multiple loggers write to the same file. |

### Output format

```
[YYYY-MM-DD HH:MM:SS][name][file.py:line] message
```

- `name` bracket is omitted when no name is set
- With tracing enabled, caller info becomes a chain: `file1.py:10>file2.py:20`

**Examples:**

```
[2026-05-18 10:30:00][main.py:42] Server started
[2026-05-18 10:30:01][app][main.py:55] Request received
[2026-05-18 10:30:02][worker][worker.py:12>main.py:55] Task complete
```

### Log files

Entries are appended to `<log_dir>/<YYYY-MM-DD>_logging.txt`. A new file is created each day automatically.

### Methods

#### `log(message, print_to_console=False, console_message="")`

Write a log entry.

```python
log.log("Server started")
log.log("Request received", print_to_console=True)
log.log("Error occurred", print_to_console=True, console_message="ERROR: check logs")
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `message` | `str` | — | Message to write to the log file. |
| `print_to_console` | `bool` | `False` | Also print to stdout. |
| `console_message` | `str` | `""` | Custom stdout message. Falls back to `message` when empty. |

#### `__call__` (shorthand)

The logger is callable — equivalent to `log()` with no extra options:

```python
log("Server started")
```

#### `enable_logging(enable: bool)`

Enable or disable this logger instance without affecting others.

```python
log.enable_logging(False)  # silence this logger
log.enable_logging(True)   # re-enable
```

#### `enable_log_tracing(enable: bool)`

Enable or disable full call-stack tracing for this instance.

```python
log.enable_log_tracing(True)
# Output: [2026-05-18 10:30:00][worker.py:8>main.py:42] message
```

Tracing is also gated by `GLOBAL_LOG_TRACING_ENABLED` — both must be `True` for the chain to appear.

### Global flags

```python
from ntnlog.ntn_config import GLOBAL_LOGGING_ENABLED, GLOBAL_LOG_TRACING_ENABLED
```

| Flag | Default | Effect |
|---|---|---|
| `GLOBAL_LOGGING_ENABLED` | `True` | Master on/off switch. When `False`, all logger instances are silenced. |
| `GLOBAL_LOG_TRACING_ENABLED` | `True` | Master tracing switch. When `False`, tracing is disabled globally even if enabled per-instance. |

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
from ntnlog import Logger

log = Logger()
log("Application started")
log("Request received", print_to_console=True)
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
[2026-05-18 10:30:00][app][main.py:6] Server ready
[2026-05-18 10:30:01][worker][main.py:7] Processing task
```

### Call-stack tracing

```python
from ntnlog import Logger

log = Logger(name="api")
log.enable_log_tracing(True)

def handle_request():
    log("Handling request")

def main():
    handle_request()
```

Log output:
```
[2026-05-18 10:30:00][api][main.py:5>main.py:9] Handling request
```

### Project-aware frame filtering

```python
log = Logger(project_dir="/path/to/my_project")
```

Only frames inside `my_project` appear in caller info — framework and library frames are excluded.
