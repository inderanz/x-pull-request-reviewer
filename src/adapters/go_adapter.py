import subprocess
import os

BIN_DIR = os.path.join(os.path.dirname(__file__), '../bin')
GOFMT_BIN = os.path.join(BIN_DIR, 'gofmt')
GOLINT_BIN = os.path.join(BIN_DIR, 'golint')

def run_gofmt_check(target):
    """Run local 'gofmt -l' to list files that need formatting."""
    if not os.path.exists(GOFMT_BIN):
        return '[ERROR] gofmt binary not found in bin/'
    try:
        result = subprocess.run([
            GOFMT_BIN, '-l', target
        ], capture_output=True, text=True)
        if result.returncode == 0 and not result.stdout.strip():
            return "All Go files are properly formatted."
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] gofmt: {e}"


def run_golint(target):
    """Run local 'golint' and return the output."""
    if not os.path.exists(GOLINT_BIN):
        return '[ERROR] golint binary not found in bin/'
    try:
        result = subprocess.run([
            GOLINT_BIN, target
        ], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] golint: {e}" 