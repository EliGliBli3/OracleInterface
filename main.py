import os
import sys, atexit, signal

from Engines import oracle_engine as fscm
from pathlib import Path
from logger import *

AUTH_STATE = Path("../Oracle/auth/oracle_auth_state.json")
PROFILE_DIR = "../Oracle/auth/oracle_cookies"
ORACLE_HOST = "https://fa-eovh-test-saasfaprod1.fa.ocs.oraclecloud.com" #"https://fa-eovh-saasfaprod1.fa.ocs.oraclecloud.com"
LOGIN_URL = f"{ORACLE_HOST}/fscmUI/faces/FuseWelcome"

program_start = datetime.now()

def handle_signal(signum, frame):
    sys.exit(128 + signum)

if __name__ == '__main__':
    atexit.register(fscm.dispose)
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    log("Starting Oracle Interface...", LogLevel.PENDING)

    fscm.prompt_login()
    fscm.start_engine()

    log("Oracle Interface Launched!", LogLevel.SUCCESS)
    os.system('cls')



    input()
