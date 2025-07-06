from src.review import security, compliance, best_practices, dependency, test_coverage, documentation
import tempfile
import os

# Security
def test_security_python_eval():
    issues = security.security_issues_in_diff('eval("danger")', 'python')
    assert any('eval' in i for i in issues)

def test_security_terraform_sensitive():
    issues = security.security_issues_in_diff('sensitive = false', 'terraform')
    assert any('sensitive' in i for i in issues)

# Compliance
def test_compliance_license():
    issues = compliance.compliance_issues_in_diff('foo', 'python')
    assert any('license' in i for i in issues)

def test_compliance_java_forbidden():
    issues = compliance.compliance_issues_in_diff('import sun.misc', 'java')
    assert any('sun.*' in i for i in issues)

# Best Practices
def test_best_practices_python_docstring():
    issues = best_practices.best_practices_in_diff('def foo(): pass', 'python')
    assert any('docstring' in i for i in issues)

def test_best_practices_terraform_var():
    issues = best_practices.best_practices_in_diff('variable "foo" {}', 'terraform')
    assert any('description' in i for i in issues)

# Dependency
def test_dependency_python(tmp_path):
    req = tmp_path / 'requirements.txt'
    req.write_text('foo==0.1.0')
    findings = dependency.analyze_python_dependencies(str(tmp_path))
    assert any('pre-1.0' in f for f in findings)

def test_dependency_go(tmp_path):
    go_mod = tmp_path / 'go.mod'
    go_mod.write_text('require foo v0.2.0')
    findings = dependency.analyze_go_dependencies(str(tmp_path))
    assert any('pre-1.0' in f for f in findings)

# Test Coverage (mock subprocess)
def test_test_coverage_python(monkeypatch):
    def fake_run(*a, **k):
        class R: returncode=0; stdout='TOTAL 100%'; stderr=''
        return R()
    monkeypatch.setattr('subprocess.run', fake_run)
    result = test_coverage.analyze_python_coverage('.')
    assert '100%' in result

# Documentation
def test_documentation_python(tmp_path):
    readme = tmp_path / 'README.md'
    readme.write_text('Project')
    py = tmp_path / 'foo.py'
    py.write_text('def foo(): pass')
    findings = documentation.analyze_python_docs(str(tmp_path))
    assert any('docstring' in f for f in findings) 