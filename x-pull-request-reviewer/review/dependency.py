import os
import re
import toml
import xml.etree.ElementTree as ET

def analyze_python_dependencies(repo_dir):
    findings = []
    req_path = os.path.join(repo_dir, 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path) as f:
            for line in f:
                if '==' in line:
                    pkg, ver = line.strip().split('==')
                    if ver.startswith('0.'):
                        findings.append(f"Python package {pkg} is pre-1.0 (potentially unstable)")
    pyproject = os.path.join(repo_dir, 'pyproject.toml')
    if os.path.exists(pyproject):
        data = toml.load(pyproject)
        deps = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
        for pkg, ver in deps.items():
            if isinstance(ver, str) and ver.startswith('0.'):
                findings.append(f"Python package {pkg} is pre-1.0 (potentially unstable)")
    return findings

def analyze_go_dependencies(repo_dir):
    findings = []
    go_mod = os.path.join(repo_dir, 'go.mod')
    if os.path.exists(go_mod):
        with open(go_mod) as f:
            for line in f:
                if re.match(r'^require ', line):
                    parts = line.strip().split()
                    if len(parts) == 3 and parts[2].startswith('v0.'):
                        findings.append(f"Go module {parts[1]} is pre-1.0 (potentially unstable)")
    return findings

def analyze_java_dependencies(repo_dir):
    findings = []
    pom = os.path.join(repo_dir, 'pom.xml')
    if os.path.exists(pom):
        tree = ET.parse(pom)
        root = tree.getroot()
        for dep in root.iter('dependency'):
            group = dep.find('groupId').text if dep.find('groupId') is not None else ''
            artifact = dep.find('artifactId').text if dep.find('artifactId') is not None else ''
            version = dep.find('version').text if dep.find('version') is not None else ''
            if version.startswith('0.'):
                findings.append(f"Java dependency {group}:{artifact} is pre-1.0 (potentially unstable)")
    # TODO: Add build.gradle support
    return findings

def analyze_terraform_dependencies(repo_dir):
    findings = []
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('.tf'):
                with open(os.path.join(root, file)) as f:
                    content = f.read()
                    if 'provider' in content and 'version = "0.' in content:
                        findings.append(f"Terraform provider in {file} is pre-1.0 (potentially unstable)")
    return findings

def analyze_dependencies(repo_dir, language):
    if language.lower() == 'python':
        return analyze_python_dependencies(repo_dir)
    if language.lower() == 'go':
        return analyze_go_dependencies(repo_dir)
    if language.lower() == 'java':
        return analyze_java_dependencies(repo_dir)
    if language.lower() == 'terraform':
        return analyze_terraform_dependencies(repo_dir)
    return [] 