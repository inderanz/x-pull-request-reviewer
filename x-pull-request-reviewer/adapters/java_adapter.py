import subprocess
import os

BIN_DIR = os.path.join(os.path.dirname(__file__), '../bin')
GOOGLE_JAVA_FORMAT_BIN = os.path.join(BIN_DIR, 'google-java-format')
CHECKSTYLE_BIN = os.path.join(BIN_DIR, 'checkstyle')

def run_google_java_format_check(target):
    """Run local 'google-java-format --dry-run --set-exit-if-changed' and return the output."""
    if not os.path.isfile(GOOGLE_JAVA_FORMAT_BIN):
        return '[ERROR] google-java-format binary not found in bin/'
    try:
        result = subprocess.run([
            GOOGLE_JAVA_FORMAT_BIN, '--dry-run', '--set-exit-if-changed', target
        ], capture_output=True, text=True)
        if result.returncode == 0:
            return "All Java files are properly formatted."
        return result.stdout.strip() if result.stdout else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] google-java-format: {e}"


def run_checkstyle(target, config_file=None):
    """Run local 'checkstyle' with optional config and return the output."""
    if not os.path.isfile(CHECKSTYLE_BIN):
        return '[ERROR] checkstyle binary not found in bin/'
    try:
        cmd = [CHECKSTYLE_BIN, '-c', config_file, target] if config_file else [CHECKSTYLE_BIN, target]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[ERROR] checkstyle: {e}" 