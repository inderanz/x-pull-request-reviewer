import subprocess
import os
import shutil

BIN_DIR = os.path.join(os.path.dirname(__file__), '../bin')
TERRAFORM_BIN = os.path.join(BIN_DIR, 'terraform')
TFLINT_BIN = os.path.join(BIN_DIR, 'tflint')

def _find_tool(tool_name, bin_path):
    """Find tool in bin/ directory or system PATH."""
    if os.path.isfile(bin_path):
        return bin_path
    # Fallback to system-installed tool
    system_tool = shutil.which(tool_name)
    if system_tool:
        return system_tool
    return None

def run_terraform_fmt(directory):
    """Run 'terraform fmt' and return the output."""
    terraform_path = _find_tool('terraform', TERRAFORM_BIN)
    if not terraform_path:
        return '[ERROR] terraform not found in bin/ or system PATH'
    try:
        result = subprocess.run([
            terraform_path, 'fmt', '-check', '-diff', directory
        ], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] terraform fmt: {e}"


def run_tflint(directory):
    """Run 'tflint' and return the output."""
    tflint_path = _find_tool('tflint', TFLINT_BIN)
    if not tflint_path:
        return '[ERROR] tflint not found in bin/ or system PATH'
    try:
        result = subprocess.run([
            tflint_path, '--chdir', directory
        ], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] tflint: {e}" 