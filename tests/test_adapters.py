import pytest
from unittest.mock import patch, MagicMock
from adapters import terraform_adapter, python_adapter, go_adapter, java_adapter, shell_adapter, yaml_adapter

@patch('subprocess.run')
def test_terraform_adapter_fmt_success(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout='ok', stderr='')
    assert terraform_adapter.run_terraform_fmt('.') == 'ok'

@patch('subprocess.run')
def test_terraform_adapter_fmt_error(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stdout='', stderr='error')
    assert 'error' in terraform_adapter.run_terraform_fmt('.')

@patch('subprocess.run')
def test_python_adapter_black_success(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout='ok', stderr='')
    assert python_adapter.run_black_check('.') == 'ok'

@patch('subprocess.run')
def test_python_adapter_black_error(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stdout='', stderr='error')
    assert 'error' in python_adapter.run_black_check('.')

@patch('subprocess.run')
def test_go_adapter_gofmt_success(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
    assert 'properly formatted' in go_adapter.run_gofmt_check('foo.go')

@patch('subprocess.run')
def test_java_adapter_format_success(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
    assert 'properly formatted' in java_adapter.run_google_java_format_check('foo.java')

@patch('subprocess.run')
def test_shell_adapter_shfmt_success(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
    assert 'properly formatted' in shell_adapter.run_shfmt_check('foo.sh')

@patch('subprocess.run')
def test_yaml_adapter_yamllint_success(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout='ok', stderr='')
    assert yaml_adapter.run_yamllint('foo.yaml') == 'ok' 