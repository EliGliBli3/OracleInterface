import os
import sys, signal
import traceback

lazy from Engines import oracle_engine as fscm, cli_engine as cli

from logger import *

AUTH_STATE = Path("../Oracle/auth/oracle_auth_state.json")
PROFILE_DIR = "../Oracle/auth/oracle_cookies"
ORACLE_HOST =  "https://fa-eovh-saasfaprod1.fa.ocs.oraclecloud.com"
ORACLE_TEST_HOST = "https://fa-eovh-test-saasfaprod1.fa.ocs.oraclecloud.com"

AUTHORIZED_USER: str = ""

test_environment: bool = False

program_start = datetime.now()
sys_exit = sys.exit

def get_signal_info(exit_code):
    signum = exit_code - 128 if 128 < exit_code <= 255 else exit_code

    try:
        sig = signal.Signals(signum)
        description = signal.strsignal(signum)
        print(repr(description))
        return {"name": sig.name, "description": description}
    except ValueError:
        return {"name": "UNKNOWN", "description": "Unknown signal"}

def handle_signal(signum, frame):
    sys.exit(128 + signum)

def handle_exception(exc_type, value, tb):
    log(f"{exc_type}: {value}\n\nTraceback Info: {''.join(traceback.format_exception(value))}", LogLevel.ERROR)

def close(code: int = 0):
    sig = get_signal_info(code)

    log(f"Exiting with code {code} ({sig['name']}: {sig['description']}).")
    fscm.dispose()
    sys_exit(code)

if __name__ == '__main__':
    sys.exit = close

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    sys.excepthook = handle_exception

    log("Starting Oracle Interface...", LogLevel.PENDING)

    fscm.prompt_login(test_environment=False)
    fscm.start_engine()

    log("Oracle Interface Launched!", LogLevel.SUCCESS)

#   -  -  -  -  -

    cli.go_to_page(cli.get_home_page())

    input()
