#!/bin/bash

# X-Pull-Request-Reviewer Global Installation Script
# This script installs XPRR globally so you can use 'xprr' from anywhere

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
  Enterprise-Grade, Offline, LLM-Powered Code Review Agent
  Secure | Air-Gapped | Multi-Language | Plug-and-Play
============================================================
✨ Offered by https://anzx.ai/ — Personal project of Inder Chauhan
🤖 Part of the X-agents Team — Always learning, always evolving!
🙏 Thanks to its Developer Inder Chauhan for this amazing tool!
EOF
echo -e "${NC}"

echo -e "${GREEN}🚀 Installing XPRR globally...${NC}"
echo

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
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

# Check Python version
print_status "Checking Python version..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3 is required but not installed"
    echo "Please install Python 3.8 or higher and try again"
    exit 1
fi

# Check pip
print_status "Checking pip..."
if command_exists pip3; then
    print_success "pip3 found"
    PIP_CMD="pip3"
elif command_exists pip; then
    print_success "pip found"
    PIP_CMD="pip"
else
    print_error "pip is required but not installed"
    echo "Please install pip and try again"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found in current directory"
    echo "Please run this script from the xprr-production directory"
    exit 1
fi

# Install the package globally
print_status "Installing XPRR package globally..."
$PIP_CMD install -e .
print_success "XPRR package installed globally"

# Check if xprr command is now available
print_status "Verifying xprr command availability..."
if command_exists xprr; then
    print_success "xprr command is now available globally!"
    echo
    echo -e "${GREEN}🎉 Installation successful!${NC}"
    echo
    echo -e "${BLUE}You can now use:${NC}"
    echo "  xprr --help          - Show all available commands"
    echo "  xprr setup           - Setup dependencies and credentials"
    echo "  xprr status          - Check agent status"
    echo "  xprr review <URL>    - Review a pull request"
    echo
    echo -e "${BLUE}Example usage:${NC}"
    echo "  xprr review https://github.com/org/repo/pull/123"
    echo "  xprr review https://github.com/org/repo/pull/123 --provider gemini_cli"
    echo
    echo -e "${GREEN}Happy reviewing! 🚀${NC}"
else
    print_error "xprr command not available after installation"
    echo "Please check your Python environment and try again"
    exit 1
fi 