import os
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


def analyze_directory(directory):
    """Detect file types and run format/lint checks. Return a summary dict."""
    summary = {}
    for root, _, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1]
            lang = LANG_EXT_MAP.get(ext)
            if not lang:
                continue
            path = os.path.join(root, file)
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
    return summary 