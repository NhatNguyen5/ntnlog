#######################################################################
#
# Logging Module Configuration
#
# Configuration for logging and tracing
#
#######################################################################

from .ntn_levels import Level

GLOBAL_LOGGING_ENABLED     = True
GLOBAL_LOG_TRACING_ENABLED = True

GLOBAL_LOG_LEVEL    = Level.INFO
GLOBAL_MAX_BYTES    = 10_000_000
GLOBAL_BACKUP_COUNT = 1
GLOBAL_LOG_COLORS: dict[int, str] = {
    Level.TRACE:    "\033[37m",
    Level.DEBUG:    "\033[36m",
    Level.INFO:     "\033[32m",
    Level.WARNING:  "\033[33m",
    Level.ERROR:    "\033[31m",
    Level.CRITICAL: "\033[35m",
}
