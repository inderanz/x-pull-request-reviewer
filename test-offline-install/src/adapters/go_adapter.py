import subprocess
import os
import shutil

BIN_DIR = os.path.join(os.path.dirname(__file__), '../bin')
GOFMT_BIN = os.path.join(BIN_DIR, 'gofmt')
GOLINT_BIN = os.path.join(BIN_DIR, 'golint')

def _find_tool(tool_name, bin_path):
    """Find tool in bin/ directory or system PATH."""
    if os.path.isfile(bin_path):
        return bin_path
    # Fallback to system-installed tool
    system_tool = shutil.which(tool_name)
    if system_tool:
        return system_tool
    return None

def run_gofmt(directory):
    """Run 'gofmt' and return the output."""
    gofmt_path = _find_tool('gofmt', GOFMT_BIN)
    if not gofmt_path:
        return '[ERROR] gofmt not found in bin/ or system PATH'
    try:
        result = subprocess.run([
            gofmt_path, '-l', directory
        ], capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except subprocess.TimeoutExpired:
        return '[TIMEOUT] gofmt timed out after 30s'
    except Exception as e:
        return f"[ERROR] gofmt: {e}"


def run_golint(directory):
    """Run 'golint' and return the output."""
    golint_path = _find_tool('golint', GOLINT_BIN)
    if not golint_path:
        return '[ERROR] golint not found in bin/ or system PATH'
    try:
        result = subprocess.run([
            golint_path, directory
        ], capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except subprocess.TimeoutExpired:
        return '[TIMEOUT] golint timed out after 30s'
    except Exception as e:
        return f"[ERROR] golint: {e}" 