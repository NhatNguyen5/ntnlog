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
from logging_module import Logger

# Create a logger instance
app_logger = Logger()

# Basic logging
app_logger.log("Application started")

# Log with console output
app_logger.log("Important message", print_to_console=True)

# Log with custom console message
app_logger.log("Debug info", print_to_console=True, console_message="DEBUG: Debug info")

# Use as a callable (shortcut for log())
app_logger("Quick log message")

# Control logging behavior
app_logger.enable_logging(False)  # Disable this logger instance
app_logger.enable_log_tracing(True)  # Enable detailed tracing for this instance

# Configure custom log directory
custom_logger = Logger(log_dir="my_logs")

# Configure project directory for better frame filtering
project_logger = Logger(project_dir="/path/to/project")
```

## Configuration

### Logging Config (`config.py`)
- `GLOBAL_LOGGING_ENABLED`: Enable/disable logging (default: `True`)
- `GLOBAL_LOG_TRACING_ENABLED`: Enable/disable detailed tracing (default: `True`)

```python
from logging_module.config import GLOBAL_LOGGING_ENABLED, GLOBAL_LOG_TRACING_ENABLED
```

## Modules

### Logger (`my_logging.py`)
Main logging class providing timestamped, structured logging with caller information.

**Key Features:**
- Automatic timestamping and file logging
- Caller information tracking with configurable frame filtering
- Configurable log directory and project directory
- Thread-safe file operations
- Configurable tracing depth
- Console output options
- Instance-level enable/disable controls

### File Utilities (`file_utils.py`)
Safe file operations with comprehensive error handling:
- Path verification with security checks
- File verification for different operations (read/write/execute)
- Directory operations with working directory constraints

### Configuration (`config.py`)
Global configuration settings for logging behavior:
- `GLOBAL_LOGGING_ENABLED`: Master switch for all logging
- `GLOBAL_LOG_TRACING_ENABLED`: Master switch for tracing features

## Development

### Prerequisites
- Python 3.10+

### Installing in Development Mode
```bash
cd logging_module
pip install -e .
```

### Running Tests
```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_my_logging.py
```

## License

MIT

## Author

Nathan T Nguyen
