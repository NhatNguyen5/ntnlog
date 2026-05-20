import pytest
from ntnlog.ntn_config import (
    GLOBAL_LOGGING_ENABLED,
    GLOBAL_LOG_TRACING_ENABLED,
    GLOBAL_LOG_LEVEL,
    GLOBAL_MAX_BYTES,
    GLOBAL_BACKUP_COUNT,
    GLOBAL_LOG_COLORS,
)
from ntnlog.ntn_levels import Level
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
        import ntnlog.ntn_config as cfg
        # Mutating one flag must not affect the other
        try:
            cfg.GLOBAL_LOG_TRACING_ENABLED = False
            assert cfg.GLOBAL_LOGGING_ENABLED is True
        finally:
            cfg.GLOBAL_LOG_TRACING_ENABLED = True


class TestNewGlobalConfig:
    def test_global_log_level_is_info(self):
        assert GLOBAL_LOG_LEVEL is Level.INFO

    def test_global_log_level_importable_from_ntnlog(self):
        from ntnlog import GLOBAL_LOG_LEVEL as g
        assert g is Level.INFO

    def test_global_max_bytes_value(self):
        assert GLOBAL_MAX_BYTES == 10_000_000

    def test_global_max_bytes_is_int(self):
        assert isinstance(GLOBAL_MAX_BYTES, int)

    def test_global_max_bytes_importable_from_ntnlog(self):
        from ntnlog import GLOBAL_MAX_BYTES as g
        assert g == 10_000_000

    def test_global_backup_count_value(self):
        assert GLOBAL_BACKUP_COUNT == 1

    def test_global_backup_count_is_int(self):
        assert isinstance(GLOBAL_BACKUP_COUNT, int)

    def test_global_backup_count_importable_from_ntnlog(self):
        from ntnlog import GLOBAL_BACKUP_COUNT as g
        assert g == 1

    def test_global_log_colors_is_dict(self):
        assert isinstance(GLOBAL_LOG_COLORS, dict)

    def test_global_log_colors_has_six_keys(self):
        assert len(GLOBAL_LOG_COLORS) == 6

    def test_global_log_colors_has_all_levels(self):
        for lvl in Level:
            assert int(lvl) in GLOBAL_LOG_COLORS

    def test_global_log_colors_values_are_ansi_strings(self):
        for value in GLOBAL_LOG_COLORS.values():
            assert isinstance(value, str)
            assert value.startswith("\033[")

    def test_global_log_colors_importable_from_ntnlog(self):
        from ntnlog import GLOBAL_LOG_COLORS as g
        assert isinstance(g, dict)
        assert len(g) == 6

    def test_version_is_updated(self):
        assert ntnlog.__version__ == "0.5.1"
