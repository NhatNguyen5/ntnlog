# ntnlog — Next-To-Nothing Logging for Python

Lightweight Python logger with timestamped file output, caller stack tracing, and working-directory-scoped path utilities. Zero boilerplate — just import and log.

## Install

```bash
pip install ntnlog
```

## Quick start

```python
from ntnlog import Logger

log = Logger()
log("Server started")
log("Request received", print_to_console=True)
```

Log output (`logs/2026-05-18_logging.txt`):
```
[2026-05-18 10:30:00][main.py:4] Server started
[2026-05-18 10:30:01][main.py:5] Request received
```

## Named loggers

```python
app    = Logger(name="app")
worker = Logger(name="worker")

app("Listening on port 8000")
worker("Processing task")
```

```
[2026-05-18 10:30:00][app][main.py:4] Listening on port 8000
[2026-05-18 10:30:01][worker][main.py:5] Processing task
```

## Path utilities

```python
import ntnlog

root = ntnlog.utils.get_working_dir()
path = ntnlog.utils.resolve_path("logs/app.log")
```

---

For full API reference and usage details, see the **[Instructions](Instructions)** page.
