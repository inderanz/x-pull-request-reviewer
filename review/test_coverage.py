import os
import subprocess

def analyze_python_coverage(repo_dir):
    try:
        result = subprocess.run([
            'pytest', '--cov', repo_dir
        ], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if 'TOTAL' in line and '%' in line:
                    return f"Python test coverage: {line.strip()}"
            return "Python test coverage: Could not parse coverage output."
        else:
            return f"Python test coverage error: {result.stderr.strip()}"
    except Exception as e:
        return f"Python test coverage error: {e}"

def analyze_go_coverage(repo_dir):
    try:
        result = subprocess.run([
            'go', 'test', '-cover', './...'
        ], cwd=repo_dir, capture_output=True, text=True)
        if result.returncode == 0:
            lines = [l for l in result.stdout.splitlines() if 'coverage:' in l]
            if lines:
                return f"Go test coverage: {lines[-1].strip()}"
            return "Go test coverage: No coverage info found."
        else:
            return f"Go test coverage error: {result.stderr.strip()}"
    except Exception as e:
        return f"Go test coverage error: {e}"

def analyze_java_coverage(repo_dir):
    jacoco_report = os.path.join(repo_dir, 'target', 'site', 'jacoco', 'index.html')
    if os.path.exists(jacoco_report):
        return "Java test coverage: JaCoCo report found. Review index.html for details."
    return "Java test coverage: No JaCoCo report found."

def analyze_terraform_coverage(repo_dir):
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file.startswith('test_') and file.endswith('.go'):
                return "Terraform test coverage: Test files detected (via Terratest)."
    return "Terraform test coverage: No test files detected."

def analyze_test_coverage(repo_dir, language):
    if language.lower() == 'python':
        return analyze_python_coverage(repo_dir)
    if language.lower() == 'go':
        return analyze_go_coverage(repo_dir)
    if language.lower() == 'java':
        return analyze_java_coverage(repo_dir)
    if language.lower() == 'terraform':
        return analyze_terraform_coverage(repo_dir)
    return "Test coverage analysis not supported for this language." 