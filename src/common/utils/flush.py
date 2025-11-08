import sys
import threading

def flush_stdout_periodically(interval=1.0):
    """Flush stdout and stderr every `interval` seconds in a separate daemon thread."""
    t = threading.Thread(target=flush, args=(interval,), daemon=True)
    t.start()

def flush(interval):
    """Flush stdout and stderr every `interval` seconds."""
    while True:
        sys.stdout.flush()
        sys.stderr.flush()
        threading.Event().wait(interval)