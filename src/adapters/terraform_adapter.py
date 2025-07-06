import subprocess
import os

BIN_DIR = os.path.join(os.path.dirname(__file__), '../bin')
TERRAFORM_BIN = os.path.join(BIN_DIR, 'terraform')
TFLINT_BIN = os.path.join(BIN_DIR, 'tflint')

def run_terraform_fmt(directory):
    """Run local 'terraform fmt' and return the output."""
    if not os.path.isfile(TERRAFORM_BIN):
        return '[ERROR] terraform binary not found in bin/'
    try:
        result = subprocess.run([
            TERRAFORM_BIN, 'fmt', '-check', '-diff', directory
        ], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] terraform fmt: {e}"


def run_tflint(directory):
    """Run local 'tflint' and return the output."""
    if not os.path.isfile(TFLINT_BIN):
        return '[ERROR] tflint binary not found in bin/'
    try:
        result = subprocess.run([
            TFLINT_BIN, '--chdir', directory
        ], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] tflint: {e}" 