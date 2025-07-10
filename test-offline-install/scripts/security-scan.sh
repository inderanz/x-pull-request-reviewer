#!/bin/bash

# XPRR Security Scan Script
# Run this script locally to check security before submitting PRs

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install security tools
install_security_tools() {
    print_status "Installing security tools..."
    
    # Try to find pip in various locations
    PIP_CMD=""
    if command_exists pip; then
        PIP_CMD="pip"
    elif command_exists pip3; then
        PIP_CMD="pip3"
    elif [ -f "venv/bin/pip" ]; then
        PIP_CMD="venv/bin/pip"
    elif [ -f "venv/bin/pip3" ]; then
        PIP_CMD="venv/bin/pip3"
    else
        print_error "pip not found. Please install Python and pip first, or activate your virtual environment."
        exit 1
    fi
    
    print_status "Using pip: $PIP_CMD"
    $PIP_CMD install bandit safety pip-audit semgrep bandit[pyproject] black flake8 mypy
    print_success "Security tools installed"
}

# Function to create reports directory
setup_reports() {
    mkdir -p security-reports
    mkdir -p static-analysis-reports
    print_status "Reports directories created"
}

# Function to run Bandit security scan
run_bandit() {
    print_status "Running Bandit security scan..."
    
    if command_exists bandit; then
        bandit -r src/ -f json -o security-reports/bandit-report.json || true
        bandit -r src/ -f txt -o security-reports/bandit-report.txt || true
        
        if [ -s security-reports/bandit-report.txt ]; then
            print_warning "Bandit found security issues. Check security-reports/bandit-report.txt"
        else
            print_success "Bandit scan completed - no issues found"
        fi
    else
        print_error "Bandit not found. Install with: pip install bandit"
    fi
}

# Function to run Safety dependency check
run_safety() {
    print_status "Running Safety dependency vulnerability check..."
    
    if command_exists safety; then
        safety check --json --output security-reports/safety-report.json || true
        safety check --output security-reports/safety-report.txt || true
        
        if [ -s security-reports/safety-report.txt ]; then
            print_warning "Safety found vulnerabilities. Check security-reports/safety-report.txt"
        else
            print_success "Safety check completed - no vulnerabilities found"
        fi
    else
        print_error "Safety not found. Install with: pip install safety"
    fi
}

# Function to run pip-audit
run_pip_audit() {
    print_status "Running pip-audit vulnerability scan..."
    
    if command_exists pip-audit; then
        pip-audit --format json --output security-reports/pip-audit-report.json || true
        pip-audit --output security-reports/pip-audit-report.txt || true
        
        if [ -s security-reports/pip-audit-report.txt ]; then
            print_warning "pip-audit found vulnerabilities. Check security-reports/pip-audit-report.txt"
        else
            print_success "pip-audit scan completed - no vulnerabilities found"
        fi
    else
        print_error "pip-audit not found. Install with: pip install pip-audit"
    fi
}

# Function to run Semgrep
run_semgrep() {
    print_status "Running Semgrep security scan..."
    
    if command_exists semgrep; then
        semgrep scan --config auto --json --output security-reports/semgrep-report.json || true
        semgrep scan --config auto --output security-reports/semgrep-report.txt || true
        
        if [ -s security-reports/semgrep-report.txt ]; then
            print_warning "Semgrep found issues. Check security-reports/semgrep-report.txt"
        else
            print_success "Semgrep scan completed - no issues found"
        fi
    else
        print_error "Semgrep not found. Install with: pip install semgrep"
    fi
}

# Function to run static analysis
run_static_analysis() {
    print_status "Running static code analysis..."
    
    # Black formatting check
    if command_exists black; then
        black --check --diff src/ tests/ > static-analysis-reports/black-report.txt 2>&1 || true
        if [ -s static-analysis-reports/black-report.txt ]; then
            print_warning "Black found formatting issues. Check static-analysis-reports/black-report.txt"
        else
            print_success "Black formatting check passed"
        fi
    else
        print_error "Black not found. Install with: pip install black"
    fi
    
    # Flake8 linting
    if command_exists flake8; then
        flake8 src/ tests/ --output-file static-analysis-reports/flake8-report.txt --format=default || true
        if [ -s static-analysis-reports/flake8-report.txt ]; then
            print_warning "Flake8 found linting issues. Check static-analysis-reports/flake8-report.txt"
        else
            print_success "Flake8 linting passed"
        fi
    else
        print_error "Flake8 not found. Install with: pip install flake8"
    fi
    
    # MyPy type checking
    if command_exists mypy; then
        mypy src/ --html-report static-analysis-reports/mypy-report || true
        mypy src/ --output-file static-analysis-reports/mypy-report.txt || true
        if [ -s static-analysis-reports/mypy-report.txt ]; then
            print_warning "MyPy found type issues. Check static-analysis-reports/mypy-report.txt"
        else
            print_success "MyPy type checking passed"
        fi
    else
        print_error "MyPy not found. Install with: pip install mypy"
    fi
}

# Function to generate summary
generate_summary() {
    print_status "Generating security summary..."
    
    cat > security-reports/security-summary.md << EOF
# Security Analysis Summary

Generated on: $(date)
Repository: $(basename $(pwd))

## Security Scan Results

### Bandit Security Scan
- **Status**: $(if [ -s security-reports/bandit-report.txt ]; then echo "⚠️ Issues found"; else echo "✅ No issues found"; fi)
- **Report**: [bandit-report.txt](security-reports/bandit-report.txt)

### Safety Dependency Check
- **Status**: $(if [ -s security-reports/safety-report.txt ]; then echo "⚠️ Vulnerabilities found"; else echo "✅ No vulnerabilities found"; fi)
- **Report**: [safety-report.txt](security-reports/safety-report.txt)

### pip-audit Vulnerability Scan
- **Status**: $(if [ -s security-reports/pip-audit-report.txt ]; then echo "⚠️ Vulnerabilities found"; else echo "✅ No vulnerabilities found"; fi)
- **Report**: [pip-audit-report.txt](security-reports/pip-audit-report.txt)

### Semgrep Security Scan
- **Status**: $(if [ -s security-reports/semgrep-report.txt ]; then echo "⚠️ Issues found"; else echo "✅ No issues found"; fi)
- **Report**: [semgrep-report.txt](security-reports/semgrep-report.txt)

## Static Analysis Results

### Code Formatting (Black)
- **Status**: $(if [ -s static-analysis-reports/black-report.txt ]; then echo "⚠️ Formatting issues"; else echo "✅ Properly formatted"; fi)

### Code Quality (Flake8)
- **Status**: $(if [ -s static-analysis-reports/flake8-report.txt ]; then echo "⚠️ Linting issues"; else echo "✅ No linting issues"; fi)

### Type Checking (MyPy)
- **Status**: $(if [ -s static-analysis-reports/mypy-report.txt ]; then echo "⚠️ Type issues"; else echo "✅ No type issues"; fi)

## Overall Security Status
$(if [ -s security-reports/bandit-report.txt ] || [ -s security-reports/safety-report.txt ] || [ -s security-reports/pip-audit-report.txt ] || [ -s security-reports/semgrep-report.txt ]; then echo "⚠️ **SECURITY ISSUES DETECTED**"; else echo "✅ **NO SECURITY VULNERABILITIES FOUND**"; fi)

## Recommendations
- Review all security reports for detailed findings
- Address any high/critical severity issues immediately
- Consider implementing additional security measures for medium/low issues
- Keep dependencies updated regularly
EOF

    print_success "Security summary generated: security-reports/security-summary.md"
}

# Function to display results
display_results() {
    echo
    echo "=========================================="
    echo "           SECURITY SCAN RESULTS          "
    echo "=========================================="
    echo
    
    # Check for security issues
    has_security_issues=false
    if [ -s security-reports/bandit-report.txt ] || [ -s security-reports/safety-report.txt ] || [ -s security-reports/pip-audit-report.txt ] || [ -s security-reports/semgrep-report.txt ]; then
        has_security_issues=true
    fi
    
    # Check for static analysis issues
    has_static_issues=false
    if [ -s static-analysis-reports/black-report.txt ] || [ -s static-analysis-reports/flake8-report.txt ] || [ -s static-analysis-reports/mypy-report.txt ]; then
        has_static_issues=true
    fi
    
    if [ "$has_security_issues" = true ]; then
        print_error "SECURITY ISSUES DETECTED!"
        echo "Please review the following reports:"
        [ -s security-reports/bandit-report.txt ] && echo "  - security-reports/bandit-report.txt"
        [ -s security-reports/safety-report.txt ] && echo "  - security-reports/safety-report.txt"
        [ -s security-reports/pip-audit-report.txt ] && echo "  - security-reports/pip-audit-report.txt"
        [ -s security-reports/semgrep-report.txt ] && echo "  - security-reports/semgrep-report.txt"
    else
        print_success "NO SECURITY VULNERABILITIES FOUND!"
    fi
    
    if [ "$has_static_issues" = true ]; then
        print_warning "STATIC ANALYSIS ISSUES DETECTED!"
        echo "Please review the following reports:"
        [ -s static-analysis-reports/black-report.txt ] && echo "  - static-analysis-reports/black-report.txt"
        [ -s static-analysis-reports/flake8-report.txt ] && echo "  - static-analysis-reports/flake8-report.txt"
        [ -s static-analysis-reports/mypy-report.txt ] && echo "  - static-analysis-reports/mypy-report.txt"
    else
        print_success "NO STATIC ANALYSIS ISSUES FOUND!"
    fi
    
    echo
    echo "Detailed summary: security-reports/security-summary.md"
    echo
}

# Main execution
main() {
    echo "🔒 XPRR Security Scan"
    echo "====================="
    echo
    
    # Check if we're in the right directory
    if [ ! -f "pyproject.toml" ] && [ ! -f "requirements.txt" ]; then
        print_error "This script must be run from the XPRR project root directory"
        exit 1
    fi
    
    # Install tools if requested
    if [ "$1" = "--install" ]; then
        install_security_tools
        exit 0
    fi
    
    # Setup
    setup_reports
    
    # Run scans
    run_bandit
    run_safety
    run_pip_audit
    run_semgrep
    run_static_analysis
    
    # Generate summary
    generate_summary
    
    # Display results
    display_results
}

# Run main function
main "$@" 