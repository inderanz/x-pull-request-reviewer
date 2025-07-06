#!/bin/bash

# XPRR Offline Package Test Script
# This script tests the offline package installation and basic functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
cat << 'EOF'
============================================================
   🚀 X-PULL-REQUEST-REVIEWER (Enterprise Edition)
============================================================
  Testing Offline Package for MacOS
  Air-Gapped | Self-Contained | Production-Ready
============================================================
✨ Offered by https://anzx.ai/ — Personal project of Inder Chauhan
🤖 Part of the X-agents Team — Always learning, always evolving!
🙏 Thanks to its Developer Inder Chauhan for this amazing tool!
EOF
echo -e "${NC}"

echo -e "${GREEN}🧪 Testing XPRR Offline Package...${NC}"
echo

# Function to print status
print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_WARNED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_exit="$3"
    
    print_status "Running: $test_name"
    
    if eval "$test_command" > /dev/null 2>&1; then
        if [ "$expected_exit" = "0" ] || [ -z "$expected_exit" ]; then
            print_success "$test_name"
            ((TESTS_PASSED++))
        else
            print_error "$test_name (unexpected success)"
            ((TESTS_FAILED++))
        fi
    else
        if [ "$expected_exit" != "0" ]; then
            print_success "$test_name (expected failure)"
            ((TESTS_PASSED++))
        else
            print_error "$test_name"
            ((TESTS_FAILED++))
        fi
    fi
}

# Function to run a test that might warn
run_test_warn() {
    local test_name="$1"
    local test_command="$2"
    
    print_status "Running: $test_name"
    
    if eval "$test_command" > /dev/null 2>&1; then
        print_success "$test_name"
        ((TESTS_PASSED++))
    else
        print_warning "$test_name (optional)"
        ((TESTS_WARNED++))
    fi
}

echo -e "${BLUE}=== Package Structure Tests ===${NC}"

# Test 1: Check if we're in the right directory
run_test "Package directory structure" "[ -d src ] && [ -d config ] && [ -d scripts ]"

# Test 2: Check if offline installation script exists
run_test "Offline installation script exists" "[ -f install-offline.sh ] && [ -x install-offline.sh ]"

# Test 3: Check if packages directory exists (if offline mode)
if [ -d "packages" ]; then
    run_test "Python packages directory exists" "[ -d packages ] && [ -n \"\$(ls packages/*.whl 2>/dev/null)\" ]"
else
    print_warning "Python packages directory not found (online mode)"
    ((TESTS_WARNED++))
fi

# Test 4: Check if binaries directory exists (if offline mode)
if [ -d "bin" ]; then
    run_test "Binaries directory exists" "[ -d bin ]"
    
    # Test individual binaries
    for binary in terraform tflint shellcheck shfmt; do
        if [ -f "bin/$binary" ]; then
            run_test "Binary $binary exists and is executable" "[ -x bin/$binary ]"
        else
            print_warning "Binary $binary not found (optional)"
            ((TESTS_WARNED++))
        fi
    done
else
    print_warning "Binaries directory not found (online mode)"
    ((TESTS_WARNED++))
fi

# Test 5: Check if Gemini CLI package exists (if offline mode)
if [ -d "gemini-cli" ]; then
    run_test "Gemini CLI package exists" "[ -d gemini-cli ] && [ -n \"\$(ls gemini-cli/*.tgz 2>/dev/null)\" ]"
else
    print_warning "Gemini CLI package not found (optional)"
    ((TESTS_WARNED++))
fi

echo
echo -e "${BLUE}=== Python Environment Tests ===${NC}"

# Test 6: Check Python version
run_test "Python 3 is available" "python3 --version"

# Test 7: Check if virtual environment can be created
run_test "Virtual environment creation" "python3 -m venv test_venv"
run_test "Virtual environment cleanup" "rm -rf test_venv"

# Test 8: Check if requirements.txt exists
run_test "Requirements file exists" "[ -f requirements.txt ]"

echo
echo -e "${BLUE}=== Installation Tests ===${NC}"

# Test 9: Test offline installation (if packages available)
if [ -d "packages" ] && [ -n "$(ls packages/*.whl 2>/dev/null)" ]; then
    print_status "Testing offline installation..."
    
    # Create test virtual environment
    python3 -m venv test_install_venv
    source test_install_venv/bin/activate
    
    # Test pip installation from local wheels
    if pip install --no-index --find-links=packages -r requirements.txt > /dev/null 2>&1; then
        print_success "Offline pip installation works"
        ((TESTS_PASSED++))
    else
        print_error "Offline pip installation failed"
        ((TESTS_FAILED++))
    fi
    
    # Cleanup
    deactivate
    rm -rf test_install_venv
else
    print_warning "Skipping offline installation test (no packages available)"
    ((TESTS_WARNED++))
fi

echo
echo -e "${BLUE}=== Binary Tests ===${NC}"

# Test 10: Test binary execution (if available)
if [ -d "bin" ]; then
    for binary in terraform tflint shellcheck shfmt; do
        if [ -x "bin/$binary" ]; then
            run_test_warn "Binary $binary is executable" "bin/$binary --version || bin/$binary --help"
        fi
    done
fi

echo
echo -e "${BLUE}=== Configuration Tests ===${NC}"

# Test 11: Check configuration files
run_test "Default configuration exists" "[ -f config/default.yaml ]"

# Test 12: Check if configuration is valid YAML
run_test "Configuration is valid YAML" "python3 -c \"import yaml; yaml.safe_load(open('config/default.yaml'))\""

echo
echo -e "${BLUE}=== Documentation Tests ===${NC}"

# Test 13: Check documentation files
run_test "README exists" "[ -f README.md ]"
run_test "Offline package README exists" "[ -f OFFLINE_PACKAGE_README.md ]"
run_test "Documentation directory exists" "[ -d docs ]"

echo
echo -e "${BLUE}=== Script Tests ===${NC}"

# Test 14: Check if scripts are executable
run_test "Start agent script is executable" "[ -x scripts/start-agent.sh ]"
run_test "Build script is executable" "[ -x scripts/build-offline-package.sh ]"

echo
echo -e "${BLUE}=== Summary ===${NC}"

echo
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${YELLOW}Tests Warned: $TESTS_WARNED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_WARNED + TESTS_FAILED))

if [ $TESTS_FAILED -eq 0 ]; then
    echo
    echo -e "${GREEN}🎉 All critical tests passed!${NC}"
    if [ $TESTS_WARNED -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Some optional components are missing (warnings above)${NC}"
    fi
    echo
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Run: ./install-offline.sh"
    echo "2. Run: ./scripts/start-agent.sh"
    echo "3. Test: xprr --help"
    echo
    echo -e "${GREEN}The offline package is ready for deployment! 🚀${NC}"
else
    echo
    echo -e "${RED}❌ Some tests failed. Please check the errors above.${NC}"
    exit 1
fi 