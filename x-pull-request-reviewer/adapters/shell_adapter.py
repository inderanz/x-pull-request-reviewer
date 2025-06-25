import subprocess
import os

BIN_DIR = os.path.join(os.path.dirname(__file__), '../bin')
SHFMT_BIN = os.path.join(BIN_DIR, 'shfmt')
SHELLCHECK_BIN = os.path.join(BIN_DIR, 'shellcheck')

def run_shfmt_check(target):
    """Run local 'shfmt -d' to show formatting diffs."""
    if not os.path.isfile(SHFMT_BIN):
        return '[ERROR] shfmt binary not found in bin/'
    try:
        result = subprocess.run([
            SHFMT_BIN, '-d', target
        ], capture_output=True, text=True)
        if result.returncode == 0 and not result.stdout.strip():
            return "All shell scripts are properly formatted."
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] shfmt: {e}"


def run_shellcheck(target):
    """Run local 'shellcheck' and return the output."""
    if not os.path.isfile(SHELLCHECK_BIN):
        return '[ERROR] shellcheck binary not found in bin/'
    try:
        result = subprocess.run([
            SHELLCHECK_BIN, target
        ], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] shellcheck: {e}" 