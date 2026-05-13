# Logging Module

A comprehensive Python logging and file utility module designed for easy integration into FastAPI projects and other Python applications.

## Features

- **Flexible Logging**: Timestamp-based logging with caller information
- **File Utilities**: Safe file operations with error handling
- **Configuration**: Easy-to-configure logging and tracing options
- **Error Management**: Comprehensive error tracking and reporting

## Installation

### From PyPI (when published)
```bash
pip install logging-module
```

### From Local Directory
```bash
pip install ./logging_module
# or in editable mode for development
pip install -e ./logging_module
```

## Quick Start

```python
from logging_module import logger, setup_logging

# Create a logger instance
app_logger = logger()

# Log a message
app_logger.log("Application started")

# Log with console output
app_logger.log("Important message", prt_msg=True)
```

## Configuration

### Logging Config (`config.py`)
- `LOGGING_ENABLED`: Enable/disable logging (default: `True`)
- `LOG_TRACING_ENABLED`: Enable/disable detailed tracing (default: `False`)

```python
from logging_module.config import LOGGING_ENABLED, LOG_TRACING_ENABLED
```

## Modules

### Logger (`my_logging.py`)
Main logging class providing timestamped, structured logging with caller information.

### File Utilities (`file_utils.py`)
Safe file operations with comprehensive error handling:
- Path verification
- File verification
- Directory operations

### Configuration (`config.py`)
Global configuration settings for logging behavior.

## Development

### Prerequisites
- Python 3.10+

### Installing in Development Mode
```bash
cd logging_module
pip install -e .
```

## License

MIT

## Author

Nathan Nguyen
