import subprocess
import os
import shutil

BIN_DIR = os.path.join(os.path.dirname(__file__), '../bin')
SHFMT_BIN = os.path.join(BIN_DIR, 'shfmt')
SHELLCHECK_BIN = os.path.join(BIN_DIR, 'shellcheck')

def _find_tool(tool_name, bin_path):
    """Find tool in bin/ directory or system PATH."""
    if os.path.isfile(bin_path):
        return bin_path
    # Fallback to system-installed tool
    system_tool = shutil.which(tool_name)
    if system_tool:
        return system_tool
    return None

def run_shfmt(directory):
    """Run 'shfmt' and return the output."""
    shfmt_path = _find_tool('shfmt', SHFMT_BIN)
    if not shfmt_path:
        return '[ERROR] shfmt not found in bin/ or system PATH'
    try:
        result = subprocess.run([
            shfmt_path, '-d', directory
        ], capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except subprocess.TimeoutExpired:
        return '[TIMEOUT] shfmt timed out after 30s'
    except Exception as e:
        return f"[ERROR] shfmt: {e}"


def run_shellcheck(directory):
    """Run 'shellcheck' and return the output."""
    shellcheck_path = _find_tool('shellcheck', SHELLCHECK_BIN)
    if not shellcheck_path:
        return '[ERROR] shellcheck not found in bin/ or system PATH'
    try:
        result = subprocess.run([
            shellcheck_path, '-x', directory
        ], capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except subprocess.TimeoutExpired:
        return '[TIMEOUT] shellcheck timed out after 30s'
    except Exception as e:
        return f"[ERROR] shellcheck: {e}" 