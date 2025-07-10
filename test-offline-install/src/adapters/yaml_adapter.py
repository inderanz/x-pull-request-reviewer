import subprocess
import os
import shutil

BIN_DIR = os.path.join(os.path.dirname(__file__), '../bin')
YAMLLINT_BIN = os.path.join(BIN_DIR, 'yamllint')
PRETTIER_BIN = os.path.join(BIN_DIR, 'prettier')

def _find_tool(tool_name, bin_path):
    """Find tool in bin/ directory or system PATH."""
    if os.path.isfile(bin_path):
        return bin_path
    # Fallback to system-installed tool
    system_tool = shutil.which(tool_name)
    if system_tool:
        return system_tool
    return None

def run_yamllint(directory):
    """Run 'yamllint' and return the output."""
    yamllint_path = _find_tool('yamllint', YAMLLINT_BIN)
    if not yamllint_path:
        return '[ERROR] yamllint not found in bin/ or system PATH'
    try:
        result = subprocess.run([
            yamllint_path, directory
        ], capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except subprocess.TimeoutExpired:
        return '[TIMEOUT] yamllint timed out after 30s'
    except Exception as e:
        return f"[ERROR] yamllint: {e}"


def run_prettier(directory):
    """Run 'prettier' and return the output."""
    prettier_path = _find_tool('prettier', PRETTIER_BIN)
    if not prettier_path:
        return '[ERROR] prettier not found in bin/ or system PATH'
    try:
        result = subprocess.run([
            prettier_path, '--check', '--parser', 'yaml', directory
        ], capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except subprocess.TimeoutExpired:
        return '[TIMEOUT] prettier timed out after 30s'
    except Exception as e:
        return f"[ERROR] prettier: {e}" 