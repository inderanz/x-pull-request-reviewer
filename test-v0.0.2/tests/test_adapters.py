import pytest
from unittest.mock import patch, MagicMock
from src.adapters import terraform_adapter, python_adapter, go_adapter, java_adapter, shell_adapter, yaml_adapter
import os
import subprocess

# Add the bin directory to PATH for mock binaries
os.environ['PATH'] = os.path.join(os.path.dirname(__file__), '..', 'bin') + os.pathsep + os.environ.get('PATH', '')

@patch('os.path.isfile', return_value=True)
@patch('subprocess.run')
def test_terraform_adapter_fmt_success(mock_run, mock_isfile):
    mock_run.return_value = MagicMock(returncode=0, stdout='ok', stderr='')
    assert terraform_adapter.run_terraform_fmt('.') == 'ok'

@patch('os.path.isfile', return_value=True)
@patch('subprocess.run')
def test_terraform_adapter_fmt_error(mock_run, mock_isfile):
    mock_run.return_value = MagicMock(returncode=1, stdout='', stderr='error')
    assert 'error' in terraform_adapter.run_terraform_fmt('.')

@patch('os.path.isfile', return_value=True)
@patch('subprocess.run')
def test_python_adapter_black_success(mock_run, mock_isfile):
    mock_run.return_value = MagicMock(returncode=0, stdout='ok', stderr='')
    assert python_adapter.run_black_check('.') == 'ok'

@patch('os.path.isfile', return_value=True)
@patch('subprocess.run')
def test_python_adapter_black_error(mock_run, mock_isfile):
    mock_run.return_value = MagicMock(returncode=1, stdout='', stderr='error')
    assert 'error' in python_adapter.run_black_check('.')

@patch('os.path.exists', return_value=True)
@patch('subprocess.run')
def test_go_adapter_gofmt_success(mock_run, mock_exists):
    # Skip if gofmt binary not found
    try:
        subprocess.run(['gofmt', '--help'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("gofmt binary not found, skipping ...")
    
    mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
    assert 'properly formatted' in go_adapter.run_gofmt_check('foo.go')

@patch('os.path.isfile', return_value=True)
@patch('subprocess.run')
def test_java_adapter_format_success(mock_run, mock_isfile):
    mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
    assert 'properly formatted' in java_adapter.run_google_java_format_check('foo.java')

@patch('os.path.isfile', return_value=True)
@patch('subprocess.run')
def test_shell_adapter_shfmt_success(mock_run, mock_isfile):
    mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')
    assert 'properly formatted' in shell_adapter.run_shfmt_check('foo.sh')

@patch('os.path.isfile', return_value=True)
@patch('subprocess.run')
def test_yaml_adapter_yamllint_success(mock_run, mock_isfile):
    mock_run.return_value = MagicMock(returncode=0, stdout='ok', stderr='')
    assert yaml_adapter.run_yamllint('foo.yaml') == 'ok' 