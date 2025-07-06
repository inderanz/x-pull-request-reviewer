import subprocess
import os

BIN_DIR = os.path.join(os.path.dirname(__file__), '../bin')
YAMLLINT_BIN = os.path.join(BIN_DIR, 'yamllint-bin')
PRETTIER_BIN = os.path.join(BIN_DIR, 'prettier-bin')

def run_yamllint(target):
    """Run local 'yamllint' and return the output."""
    if not os.path.isfile(YAMLLINT_BIN):
        return '[ERROR] yamllint binary not found in bin/'
    try:
        result = subprocess.run([
            YAMLLINT_BIN, target
        ], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] yamllint: {e}"


def run_prettier_check(target):
    """Run local 'prettier --check' and return the output."""
    if not os.path.isfile(PRETTIER_BIN):
        return '[ERROR] prettier binary not found in bin/'
    try:
        result = subprocess.run([
            PRETTIER_BIN, '--check', target
        ], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] prettier: {e}" 