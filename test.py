from ntnlog import *

test_logger = Logger(colorize=True)

test_logger("hello", level="DEBUG", console_message="")
test_logger("hello", level="ERROR", console_message="")
test_logger("hello", level="INFO", console_message="")
test_logger("hello", level="CRITICAL", console_message="")
test_logger("hello", level="TRACE", console_message="")
test_logger("hello", level="WARN", console_message="")