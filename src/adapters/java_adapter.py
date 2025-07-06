import subprocess
import os
import shutil

BIN_DIR = os.path.join(os.path.dirname(__file__), '../bin')
GOOGLE_JAVA_FORMAT_BIN = os.path.join(BIN_DIR, 'google-java-format')
CHECKSTYLE_BIN = os.path.join(BIN_DIR, 'checkstyle')

def _find_tool(tool_name, bin_path):
    """Find tool in bin/ directory or system PATH."""
    if os.path.isfile(bin_path):
        return bin_path
    # Fallback to system-installed tool
    system_tool = shutil.which(tool_name)
    if system_tool:
        return system_tool
    return None

def run_google_java_format(directory):
    """Run 'google-java-format' and return the output."""
    gjf_path = _find_tool('google-java-format', GOOGLE_JAVA_FORMAT_BIN)
    if not gjf_path:
        return '[ERROR] google-java-format not found in bin/ or system PATH'
    try:
        result = subprocess.run([
            gjf_path, '--dry-run', directory
        ], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] google-java-format: {e}"


def run_checkstyle(directory):
    """Run 'checkstyle' and return the output."""
    checkstyle_path = _find_tool('checkstyle', CHECKSTYLE_BIN)
    if not checkstyle_path:
        return '[ERROR] checkstyle not found in bin/ or system PATH'
    try:
        result = subprocess.run([
            checkstyle_path, '-c', 'google_checks.xml', directory
        ], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] checkstyle: {e}" 