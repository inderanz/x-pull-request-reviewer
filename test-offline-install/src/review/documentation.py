import os
import re

def analyze_python_docs(repo_dir):
    findings = []
    readme = os.path.join(repo_dir, 'README.md')
    if not os.path.exists(readme):
        findings.append('Missing README.md')
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file)) as f:
                    content = f.read()
                    if 'def ' in content and '"""' not in content:
                        findings.append(f'{file}: Missing function/class docstrings')
    return findings or ['Python documentation: Looks good.']

def analyze_go_docs(repo_dir):
    findings = []
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('.go'):
                with open(os.path.join(root, file)) as f:
                    content = f.read()
                    if re.search(r'package \w+', content) and '//' not in content:
                        findings.append(f'{file}: Missing package comment')
    return findings or ['Go documentation: Looks good.']

def analyze_java_docs(repo_dir):
    findings = []
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('.java'):
                with open(os.path.join(root, file)) as f:
                    content = f.read()
                    if 'public class' in content and '/**' not in content:
                        findings.append(f'{file}: Missing Javadoc for class')
    return findings or ['Java documentation: Looks good.']

def analyze_terraform_docs(repo_dir):
    findings = []
    readme = os.path.join(repo_dir, 'README.md')
    if not os.path.exists(readme):
        findings.append('Missing README.md')
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('.tf'):
                with open(os.path.join(root, file)) as f:
                    content = f.read()
                    if 'variable' in content and 'description' not in content:
                        findings.append(f'{file}: Variable missing description')
                    if 'resource' in content and 'description' not in content:
                        findings.append(f'{file}: Resource missing description')
    return findings or ['Terraform documentation: Looks good.']

def analyze_documentation(repo_dir, language):
    if language.lower() == 'python':
        return analyze_python_docs(repo_dir)
    if language.lower() == 'go':
        return analyze_go_docs(repo_dir)
    if language.lower() == 'java':
        return analyze_java_docs(repo_dir)
    if language.lower() == 'terraform':
        return analyze_terraform_docs(repo_dir)
    return ['Documentation analysis not supported for this language.'] 