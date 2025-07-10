import os
import subprocess
import signal
from ..adapters import terraform_adapter, python_adapter, yaml_adapter, go_adapter, java_adapter, shell_adapter

LANG_EXT_MAP = {
    '.tf': 'terraform',
    '.py': 'python',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.go': 'go',
    '.java': 'java',
    '.sh': 'shell',
}


def run_with_timeout(cmd, timeout=10):
    """Run a command with timeout to prevent hanging."""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except subprocess.TimeoutExpired:
        return f"[TIMEOUT] Command timed out after {timeout}s: {' '.join(cmd)}"
    except FileNotFoundError:
        return f"[ERROR] Tool not found: {cmd[0]}"
    except Exception as e:
        return f"[ERROR] {e}"


def analyze_directory(directory):
    """Detect file types and run format/lint checks. Return a summary dict."""
    summary = {}
    
    # Check if we're in an offline environment (no external tools)
    bin_dir = os.path.join(os.path.dirname(__file__), '../bin')
    has_external_tools = any([
        os.path.exists(os.path.join(bin_dir, 'terraform')),
        os.path.exists(os.path.join(bin_dir, 'tflint')),
        os.path.exists(os.path.join(bin_dir, 'black')),
        os.path.exists(os.path.join(bin_dir, 'flake8')),
    ])
    
    if not has_external_tools:
        # In offline mode, skip external tool checks
        return {"[INFO]": {"format": "Skipped (offline mode)", "lint": "Skipped (offline mode)"}}
    
    for root, _, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1]
            lang = LANG_EXT_MAP.get(ext)
            if not lang:
                continue
            path = os.path.join(root, file)
            
            try:
                if lang == 'terraform':
                    fmt = terraform_adapter.run_terraform_fmt(root)
                    lint = terraform_adapter.run_tflint(root)
                    summary[path] = {'format': fmt, 'lint': lint}
                elif lang == 'python':
                    fmt = python_adapter.run_black_check(root)
                    lint = python_adapter.run_flake8(root)
                    summary[path] = {'format': fmt, 'lint': lint}
                elif lang == 'yaml':
                    fmt = yaml_adapter.run_prettier(path)
                    lint = yaml_adapter.run_yamllint(path)
                    summary[path] = {'format': fmt, 'lint': lint}
                elif lang == 'go':
                    fmt = go_adapter.run_gofmt(path)
                    lint = go_adapter.run_golint(path)
                    summary[path] = {'format': fmt, 'lint': lint}
                elif lang == 'java':
                    fmt = java_adapter.run_google_java_format(path)
                    lint = java_adapter.run_checkstyle(path)
                    summary[path] = {'format': fmt, 'lint': lint}
                elif lang == 'shell':
                    fmt = shell_adapter.run_shfmt(path)
                    lint = shell_adapter.run_shellcheck(path)
                    summary[path] = {'format': fmt, 'lint': lint}
            except Exception as e:
                summary[path] = {'format': f'[ERROR] {e}', 'lint': f'[ERROR] {e}'}
    
    return summary 