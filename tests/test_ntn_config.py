import pytest
from ntnlog.ntn_config import GLOBAL_LOGGING_ENABLED, GLOBAL_LOG_TRACING_ENABLED
import ntnlog


class TestGlobalConfig:
    def test_logging_enabled_is_bool(self):
        assert isinstance(GLOBAL_LOGGING_ENABLED, bool)

    def test_logging_enabled_default_true(self):
        assert GLOBAL_LOGGING_ENABLED is True

    def test_tracing_enabled_is_bool(self):
        assert isinstance(GLOBAL_LOG_TRACING_ENABLED, bool)

    def test_tracing_enabled_default_true(self):
        assert GLOBAL_LOG_TRACING_ENABLED is True

    def test_importable_from_ntnlog_package(self):
        from ntnlog import GLOBAL_LOGGING_ENABLED as g1, GLOBAL_LOG_TRACING_ENABLED as g2
        assert g1 is True
        assert g2 is True

    def test_flags_are_independent(self):
        assert GLOBAL_LOGGING_ENABLED is not GLOBAL_LOG_TRACING_ENABLED or (
            GLOBAL_LOGGING_ENABLED is True and GLOBAL_LOG_TRACING_ENABLED is True
        )
