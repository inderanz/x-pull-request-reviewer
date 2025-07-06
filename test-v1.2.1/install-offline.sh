#!/bin/bash

# XPRR Offline Installation Script
# This script installs XPRR completely offline

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
cat << 'BANNER'
============================================================
   🚀 X-PULL-REQUEST-REVIEWER (Enterprise Edition)
============================================================
  Offline Installation for MacOS
  Air-Gapped | Self-Contained | Production-Ready
============================================================
✨ Offered by https://anzx.ai/ — Personal project of Inder Chauhan
🤖 Part of the X-agents Team — Always learning, always evolving!
🙏 Thanks to its Developer Inder Chauhan for this amazing tool!
BANNER
echo -e "${NC}"

echo -e "${GREEN}🚀 Installing XPRR Offline...${NC}"
echo

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
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Create virtual environment for local installation
print_status "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies from local wheels
print_status "Installing Python dependencies from local wheels..."
pip install --no-index --find-links=packages -r requirements.txt

# Install the package itself
print_status "Installing XPRR package..."
pip install --no-index --find-links=packages -e .

# Install Gemini CLI from local tarball if available
if [ -f "gemini-cli/google-gemini-cli-0.1.7.tgz" ] && command -v npm &> /dev/null; then
    print_status "Installing Gemini CLI from local tarball..."
    # Extract and install the complete offline package
    mkdir -p temp-gemini-install
    tar -xzf gemini-cli/google-gemini-cli-0.1.7.tgz -C temp-gemini-install
    cd temp-gemini-install
    npm install -g .
    cd ..
    rm -rf temp-gemini-install
    print_success "Gemini CLI installed from local tarball"
else
    print_warning "Gemini CLI tarball not found or npm not installed. Gemini CLI will not be available."
fi

# Make binaries executable
print_status "Setting up binaries..."
chmod +x bin/*

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p ollama_models

# Setup Ollama models
print_status "Setting up Ollama models..."
if [ -f "ollama_models/deepseek-coder-6.7b.bin" ]; then
    print_success "Ollama model found: deepseek-coder-6.7b.bin"
    print_status "To use offline mode, ensure Ollama is running and the model is loaded:"
    echo "  ollama run deepseek-coder-6.7b"
else
    print_warning "Ollama model not found. Offline mode will not work."
fi

print_success "Offline installation completed!"
echo
echo -e "${GREEN}🎉 XPRR is now ready to use!${NC}"
echo
echo -e "${BLUE}Next steps:${NC}"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run: ./scripts/start-agent.sh (to start the agent)"
echo "3. Run: xprr --help (to see available commands)"
echo "4. Run: xprr review <PR_URL> (to review a pull request)"
echo
echo -e "${BLUE}Available commands:${NC}"
echo "  xprr setup          - Setup dependencies and credentials"
echo "  xprr status         - Check agent status"
echo "  xprr review <URL>   - Review a pull request"
echo "  xprr llm list-providers - List available LLM providers"
echo
echo -e "${BLUE}Offline Mode:${NC}"
echo "  - All binary tools are included (Java, Go, Python, Terraform, YAML, Shell)"
echo "  - Ollama model included: deepseek-coder-6.7b.bin (3.6GB)"
echo "  - All review engines are integrated (Security, Compliance, Best Practices, etc.)"
echo "  - Interactive change management is available"
echo
echo -e "${GREEN}Happy reviewing! 🚀${NC}"
