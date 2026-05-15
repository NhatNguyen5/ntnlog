import pytest
from logging_module.config import GLOBAL_LOGGING_ENABLED, GLOBAL_LOG_TRACING_ENABLED


def test_global_logging_enabled():
    """Test that GLOBAL_LOGGING_ENABLED is a boolean."""
    assert isinstance(GLOBAL_LOGGING_ENABLED, bool)
    assert GLOBAL_LOGGING_ENABLED is True  # Default value


def test_global_log_tracing_enabled():
    """Test that GLOBAL_LOG_TRACING_ENABLED is a boolean."""
    assert isinstance(GLOBAL_LOG_TRACING_ENABLED, bool)
    assert GLOBAL_LOG_TRACING_ENABLED is True  # Default value