#!/bin/bash

# X-Pull-Request-Reviewer Setup Script
# This script sets up the XPRR agent with all dependencies

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

echo -e "${GREEN}🚀 Starting XPRR Setup...${NC}"
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

# Install Python dependencies
print_status "Installing Python dependencies..."
$PIP_CMD install -r requirements.txt
print_success "Python dependencies installed"

# Install the package globally
print_status "Installing XPRR package globally..."
$PIP_CMD install -e .
print_success "XPRR package installed globally"

# Check if xprr command is now available
print_status "Verifying xprr command availability..."
if command_exists xprr; then
    print_success "xprr command is now available globally"
    XPRR_CMD="xprr"
else
    print_warning "xprr command not available globally, using local script"
    XPRR_CMD="./xprr"
fi

# Check Node.js and npm
print_status "Checking Node.js and npm..."
if command_exists node && command_exists npm; then
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    print_success "Node.js $NODE_VERSION and npm $NPM_VERSION found"
else
    print_warning "Node.js or npm not found"
    echo "Node.js and npm are required for Gemini CLI installation"
    echo "Please install Node.js from https://nodejs.org/ and try again"
    echo "You can continue without Gemini CLI, but some features will be limited"
    read -p "Continue without Node.js? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Git
print_status "Checking Git..."
if command_exists git; then
    GIT_VERSION=$(git --version)
    print_success "$GIT_VERSION found"
else
    print_warning "Git not found"
    echo "Git is recommended for repository operations"
    echo "You can install it later if needed"
fi

# Check if we're in the right directory
if [ ! -f "xprr" ]; then
    print_error "xprr script not found in current directory"
    echo "Please run this script from the xprr-production directory"
    exit 1
fi

# Make xprr executable
print_status "Making xprr executable..."
chmod +x xprr
print_success "xprr script is now executable"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p bin
mkdir -p packages
mkdir -p ollama_models
mkdir -p config
print_success "Directories created"

# Copy config if it doesn't exist
if [ ! -f "config/default.yaml" ]; then
    print_status "Creating default configuration..."
    cat > config/default.yaml << 'EOF'
# XPRR Default Configuration

# LLM Provider Configuration
llm:
  default_provider: "ollama"  # Options: ollama, gemini_cli, google_code_assist
  timeout: 300  # Timeout in seconds for LLM requests

# Review Configuration
review:
  max_chunk_size: 4000  # Maximum characters per chunk
  enable_static_analysis: true
  enable_security_scanning: true
  enable_compliance_checking: true
  enable_best_practices: true
  enable_dependency_analysis: true
  enable_test_coverage: true
  enable_documentation_checking: true

# GitHub Configuration
github:
  api_timeout: 30
  max_retries: 3
  enable_line_comments: true
  enable_summary_comments: true

# Logging Configuration
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "logs/xprr.log"
  max_size: "10MB"
  backup_count: 5

# Security Configuration
security:
  enable_secret_scanning: true
  enable_hardcoded_credential_detection: true
  enable_sql_injection_detection: true
  enable_xss_detection: true

# Compliance Configuration
compliance:
  enable_license_checking: true
  enable_copyright_checking: true
  enable_export_control_checking: true
EOF
    print_success "Default configuration created"
fi

# Run the Python setup
print_status "Running Python setup..."
python3 $XPRR_CMD setup

print_success "Setup completed successfully!"
echo
echo -e "${GREEN}🎉 XPRR is now ready to use!${NC}"
echo
echo -e "${BLUE}Next steps:${NC}"
echo "1. Run: $XPRR_CMD status (to check everything is working)"
echo "2. Run: $XPRR_CMD review <PR_URL> (to review a pull request)"
echo "3. Run: $XPRR_CMD review <PR_URL> --provider gemini_cli (to use Gemini CLI)"
echo
echo -e "${BLUE}Available commands:${NC}"
echo "  $XPRR_CMD setup          - Setup dependencies and credentials"
echo "  $XPRR_CMD status         - Check agent status"
echo "  $XPRR_CMD review <URL>   - Review a pull request"
echo "  $XPRR_CMD stop           - Stop the agent"
echo "  $XPRR_CMD check-airgap   - Check air-gap readiness"
echo
if [ "$XPRR_CMD" = "xprr" ]; then
    echo -e "${GREEN}✅ xprr command is available globally!${NC}"
    echo "You can now run 'xprr' from any directory."
else
    echo -e "${YELLOW}⚠️  Using local xprr script${NC}"
    echo "Run './xprr' from the xprr-production directory."
fi
echo
echo -e "${BLUE}Documentation:${NC}"
echo "  README.md             - Main documentation"
echo "  docs/                 - Detailed documentation"
echo
echo -e "${GREEN}Happy reviewing! 🚀${NC}" 