# ntnlog — Next-To-Nothing Logging for Python

Lightweight Python logger with timestamped file output, caller stack tracing, and working-directory-scoped path utilities. Zero boilerplate — just import and log.

## Install

```bash
pip install ntnlog
```

## Quick start

```python
from ntnlog import Logger, Level

log = Logger()
log("Server started")
log("Request received", console_message="")   # also prints to stdout
log("Low disk space", Level.WARNING)           # WARNING level, no console
```

Log output (`logs/2026-05-18_logging.txt`):
```
[2026-05-18 10:30:00][INFO][main.py:4] Server started
[2026-05-18 10:30:01][INFO][main.py:5] Request received
[2026-05-18 10:30:02][WARNING][main.py:6] Low disk space
```

## Named loggers

```python
app    = Logger(name="app")
worker = Logger(name="worker")

app("Listening on port 8000")
worker("Processing task")
```

```
[2026-05-18 10:30:00][INFO][app][main.py:4] Listening on port 8000
[2026-05-18 10:30:01][INFO][worker][main.py:5] Processing task
```

## Level filtering

```python
log = Logger(level=Level.WARNING)   # only WARNING and above written
log = Logger(level="warning")       # string form also accepted
```

## Exception capturing

```python
try:
    risky_operation()
except Exception:
    log.exception("Operation failed")  # attaches full traceback automatically
```

## Async logging

```python
await log.alog("Async message")
await log.aexception("Async error")  # captures traceback from calling coroutine
```

## Log rotation

```python
log = Logger(max_bytes=5_000_000, backup_count=3)
# Keeps up to 3 backups: log.txt.1, log.txt.2, log.txt.3
```

## Console colorization

```python
log = Logger(colorize=True)                          # default colors per level
log = Logger(colorize=True, colors={int(Level.ERROR): "\033[91m"})  # custom
```

## Path utilities

```python
import ntnlog

root = ntnlog.utils.get_working_dir()
path = ntnlog.utils.resolve_path("logs/app.log")
```

---

For full API reference and usage details, see the **[Instructions](Instructions)** page.
