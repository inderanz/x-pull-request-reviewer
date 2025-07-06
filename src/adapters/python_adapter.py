import subprocess
import os

BIN_DIR = os.path.join(os.path.dirname(__file__), '../bin')
BLACK_BIN = os.path.join(BIN_DIR, 'black-bin')
FLAKE8_BIN = os.path.join(BIN_DIR, 'flake8-bin')

def run_black_check(directory):
    """Run local 'black --check' and return the output."""
    if not os.path.isfile(BLACK_BIN):
        return '[ERROR] black binary not found in bin/'
    try:
        result = subprocess.run([
            BLACK_BIN, '--check', directory
        ], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] black: {e}"


def run_flake8(directory):
    """Run local 'flake8' and return the output."""
    if not os.path.isfile(FLAKE8_BIN):
        return '[ERROR] flake8 binary not found in bin/'
    try:
        result = subprocess.run([
            FLAKE8_BIN, directory
        ], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] flake8: {e}" 