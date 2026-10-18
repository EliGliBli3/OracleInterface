from datetime import datetime
from enum import Enum
from pathlib import Path

class LogLevel(Enum):
    SUCCESS = '🟢'
    PENDING = '🔵'
    WARN = '🟡'
    ERROR = '🔴'
    NONE = '⚪'

def log(msg, level: LogLevel = LogLevel.NONE):
    val = str(msg)
    time = datetime.now()

    # For the log (uses ':')
    time_log = time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    # FOr the log's file name (can't use ':')
    time_file = time.strftime("%Y-%m-%d %H-%M-%S.%f")[:-7]

    result = f"{level.value} ({time}) {val}"
    print(result)

    log_path = Path(f"logs/{time_file}.log.txt")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as file:
        file.write(result+"\n")

def break_error(msg):
    log(msg, LogLevel.ERROR)
    raise RuntimeError(msg)