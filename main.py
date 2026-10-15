import sys, atexit, signal
from datetime import datetime
import oracle_engine as fscm

def handle_signal(signum, frame):
    sys.exit(128 + signum)

atexit.register(fscm.dispose)
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

if __name__ == '__main__':
    fscm.prompt_login()
    fscm.start_engine()

    fscm.get_work_order("140128")
