import os
import sys, signal
import traceback
import subprocess
from pathlib import Path

from logger import *

FROZEN = getattr(sys, "frozen", False)


def playwright_driver() -> tuple[Path, Path]:
    import playwright
    base = Path(playwright.__file__).parent / "driver"
    node = base / ("node.exe" if sys.platform == "win32" else "node")
    return node, base / "package" / "cli.js"

def browsers_dir() -> Path | None:
    if not FROZEN:
        return None
    return playwright_driver()[1].parent / ".local-browsers"

def are_browsers_installed() -> bool:
    d = browsers_dir()
    if d is None:
        return True
    return any(d.glob("chromium*"))

def install_browsers():
    node, cli = playwright_driver()
    env = os.environ.copy()
    env["PLAYWRIGHT_BROWSERS_PATH"] = "0"
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

    proc = subprocess.run(
        [str(node), str(cli), "install", "chromium"],
        env=env,
        capture_output=True,
        text=True,
        creationflags=flags,
        timeout=900,
    )
    if proc.returncode != 0:
        err_break(proc.stderr.strip()[-2000:] or f"exit code {proc.returncode}")

    if not are_browsers_installed():
        err_break("Installer finished but the browser folder is missing.")


lazy from Engines import oracle_engine as fscm, cli_engine as cli

AUTH_STATE = Path("../Oracle/auth/oracle_auth_state.json")
PROFILE_DIR = "../Oracle/auth/oracle_cookies"
ORACLE_HOST =  "https://fa-eovh-saasfaprod1.fa.ocs.oraclecloud.com"
ORACLE_TEST_HOST = "https://fa-eovh-test-saasfaprod1.fa.ocs.oraclecloud.com"

AUTHORIZED_USER: str = ""

test_environment: bool = False
alive: bool = True

program_start = datetime.now()
sys_exit = sys.exit

def get_signal_info(exit_code: int):
    if exit_code == -1:
        return {"name": "TERMINATION", "description": "Process was terminated internally"}

    try:
        signum = exit_code - 128 if 128 < exit_code <= 255 else exit_code

        sig = signal.Signals(signum)

        description = signal.strsignal(signum)
        print(repr(description))
        return {"name": sig.name, "description": description}
    except Exception as e:
        log(e)
        return {"name": "UNKNOWN", "description": "Unknown signal"}

def handle_signal(signum, frame):
    sys.exit(128 + signum)

def handle_exception(exc_type, value, tb):
    log(f"{exc_type}: {value}\n\nTraceback Info: {''.join(traceback.format_exception(value))}", LogLevel.ERROR)

def close(code: int = 0):
    if not isinstance(code, int): code = -1
    sig = get_signal_info(code)
    global alive

    log(f"Exiting with code {code} ({sig['name']}: {sig['description']}).")
    alive = False
    fscm.dispose()
    sys_exit(code)

if __name__ == '__main__':
    sys.exit = close

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    sys.excepthook = handle_exception

    if not are_browsers_installed():
        try:
            log("Browsers not installed. Installing...", LogLevel.PENDING)
            install_browsers()
            log("Browsers installed successfully!", LogLevel.SUCCESS)
        except Exception as e:
            err_break(f"Failed to install browsers.\n\t{e}")


    log("Starting Oracle Interface...", LogLevel.PENDING)

    fscm.prompt_login(test_environment=False)
    fscm.start_engine(headless=True)

    log("Oracle Interface Launched!", LogLevel.SUCCESS)

#   -  -  -  -  -

    while alive:
        input("Press any key to return to the home screen...")
        cli.go_to_page(cli.get_home_page())

