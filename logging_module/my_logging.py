#######################################################################
#                          
# My Logging Module
#
# Provides logging functionality with timestamping and caller info
# Supports configurable logging and tracing options
#
#######################################################################

import os
from datetime import datetime
from logging_module.file_utils import FileUtilsError, file_verify_path
from inspect import getframeinfo, stack
from logging_module.config import LOGGING_ENABLED, LOG_TRACING_ENABLED

calldepth = 3

class logger:
    def __init__(self):
        self.enable = True

    def __call__(self, msg, prt_msg = False, console_msg = ""):
        self.log(msg, prt_msg = prt_msg, console_msg = console_msg)

    def log(self, message, prt_msg = False, console_msg = ""):
        if not LOGGING_ENABLED or not self.enable:
            return
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H:%M:%S")
        timestamp = f"{date} {time}"
        logistic_data = f"[{timestamp}][{self.get_caller_info()}]"
        padded_space = "".rjust(len(logistic_data)+1)
        message = f"{message}".replace("\n", f"\n{padded_space}")  # Ensure single line log entries
        log_entry = f"{logistic_data} {message}\n"
        file_path = file_verify_path("./", "logs")
        if file_path == FileUtilsError.NOT_A_DIRECTORY.value.format(directory="logs"):
            os.makedirs(os.path.join("./", "logs"), exist_ok=True)
        if isinstance(file_path, str) and not file_path.startswith("Error"):
            file_name = os.path.join("./", "logs", f"{date}_logging.txt")
            if not os.path.isfile(file_name):
                with open(file_name, "w") as log_file:
                    log_file.write(f"Log file created on {date} at {time}\n")
            with open(file_name, "a") as log_file:
                log_file.write(log_entry)
                if prt_msg:
                    print(message if console_msg == "" else console_msg)

    def get_caller_info(self):
        if not LOG_TRACING_ENABLED:
            frameinfo = getframeinfo(stack()[calldepth][0])
            return f"{frameinfo.filename.rsplit('/', 1)[-1]}:{frameinfo.lineno}"
        trace_back_stack = []
        for _depth in range(calldepth, stack().__len__()):
            test_frame = getframeinfo(stack()[_depth][0])
            trace_back_stack.append(f"{test_frame.filename.rsplit('/', 1)[-1]}:{test_frame.lineno}")
        return ">".join(reversed(trace_back_stack))
    