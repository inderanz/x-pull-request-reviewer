import subprocess
import os
import shutil

BIN_DIR = os.path.join(os.path.dirname(__file__), '../bin')
BLACK_BIN = os.path.join(BIN_DIR, 'black-bin')
FLAKE8_BIN = os.path.join(BIN_DIR, 'flake8-bin')

def _find_tool(tool_name, bin_path):
    """Find tool in bin/ directory or system PATH."""
    if os.path.isfile(bin_path):
        return bin_path
    # Fallback to system-installed tool
    system_tool = shutil.which(tool_name)
    if system_tool:
        return system_tool
    return None

def run_black_check(directory):
    """Run 'black --check' and return the output."""
    black_path = _find_tool('black', BLACK_BIN)
    if not black_path:
        return '[ERROR] black not found in bin/ or system PATH'
    try:
        result = subprocess.run([
            black_path, '--check', directory
        ], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] black: {e}"


def run_flake8(directory):
    """Run 'flake8' and return the output."""
    flake8_path = _find_tool('flake8', FLAKE8_BIN)
    if not flake8_path:
        return '[ERROR] flake8 not found in bin/ or system PATH'
    try:
        result = subprocess.run([
            flake8_path, directory
        ], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] flake8: {e}" 