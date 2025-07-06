#!/bin/bash

# XPRR Offline Installation Script
# This script installs XPRR completely offline using a local virtual environment

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

# Create and activate virtual environment
print_status "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists, removing..."
    rm -rf venv
fi

python3 -m venv venv
print_success "Virtual environment created"

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip in the virtual environment
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies from local wheels
print_status "Installing Python dependencies from local wheels..."
pip install --no-index --find-links=packages -r requirements.txt
print_success "Dependencies installed"

# Install the package itself
print_status "Installing XPRR package..."
pip install --no-index --find-links=packages -e .
print_success "XPRR package installed"

# Install Gemini CLI if available
if [ -d "gemini-cli" ] && command -v npm &> /dev/null; then
    print_status "Installing Gemini CLI..."
    npm install -g gemini-cli/*.tgz
    print_success "Gemini CLI installed"
else
    print_warning "Gemini CLI not available or npm not found"
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

# Create activation script
print_status "Creating activation script..."
cat > activate-xprr.sh << 'EOF'
#!/bin/bash
# XPRR Activation Script
# Run this script to activate the XPRR environment

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    export PYTHONPATH=$PWD/src:$PYTHONPATH
    echo "XPRR environment activated!"
    echo "You can now run: python -m src.xprr_agent --help"
else
    echo "Error: Virtual environment not found. Please run ./install-offline.sh first."
    exit 1
fi
EOF

chmod +x activate-xprr.sh
print_success "Activation script created"

# Create wrapper script for easy access
print_status "Creating XPRR wrapper script..."
cat > xprr << 'EOF'
#!/bin/bash
# XPRR Wrapper Script
# This script runs XPRR with the correct environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    export PYTHONPATH=$PWD/src:$PYTHONPATH
    python -m src.xprr_agent "$@"
else
    echo "Error: Virtual environment not found. Please run ./install-offline.sh first."
    exit 1
fi
EOF

chmod +x xprr
print_success "XPRR wrapper script created"

print_success "Offline installation completed!"
echo
echo -e "${GREEN}🎉 XPRR is now ready to use!${NC}"
echo
echo -e "${BLUE}Next steps:${NC}"
echo "1. Run: ./activate-xprr.sh (to activate the environment)"
echo "2. Run: ./xprr --help (to see available commands)"
echo "3. Run: ./xprr review <PR_URL> (to review a pull request)"
echo
echo -e "${BLUE}Available commands:${NC}"
echo "  ./xprr --help              - Show help"
echo "  ./xprr review <URL>        - Review a pull request"
echo "  ./xprr llm list-providers  - List available LLM providers"
echo "  ./xprr config              - Show or edit configuration"
echo
echo -e "${BLUE}Offline Mode:${NC}"
echo "  - All binary tools are included (Java, Go, Python, Terraform, YAML, Shell)"
echo "  - Ollama model included: deepseek-coder-6.7b.bin (3.6GB)"
echo "  - All review engines are integrated (Security, Compliance, Best Practices, etc.)"
echo "  - Interactive change management is available"
echo
echo -e "${GREEN}Happy reviewing! 🚀${NC}"
