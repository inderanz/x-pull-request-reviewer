#!/bin/bash

# XPRR Offline Package Builder for MacOS
# This script creates a complete offline package with all dependencies

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
  Building Offline Package for MacOS
  Air-Gapped | Self-Contained | Production-Ready
============================================================
✨ Offered by https://anzx.ai/ — Personal project of Inder Chauhan
🤖 Part of the X-agents Team — Always learning, always evolving!
🙏 Thanks to its Developer Inder Chauhan for this amazing tool!
EOF
echo -e "${NC}"

echo -e "${GREEN}🚀 Building XPRR Offline Package for MacOS...${NC}"
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

# Configuration
PACKAGE_NAME="xprr-agent-macos-v1.0.0"
BUILD_DIR="build"
PACKAGES_DIR="$BUILD_DIR/packages"
BIN_DIR="$BUILD_DIR/bin"
NODE_MODULES_DIR="$BUILD_DIR/node_modules"
GEMINI_CLI_DIR="$BUILD_DIR/gemini-cli"

# Detect system info
OS="$(uname -s)"
ARCH="$(uname -m)"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)

print_status "Detected system: $OS $ARCH, Python $PYTHON_VERSION"

# Create build directory structure
print_status "Creating build directory structure..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
mkdir -p "$PACKAGES_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$NODE_MODULES_DIR"
mkdir -p "$GEMINI_CLI_DIR"

# Copy source files
print_status "Copying source files..."
cp -r src "$BUILD_DIR/"
cp -r config "$BUILD_DIR/"
cp -r scripts "$BUILD_DIR/"
cp -r docs "$BUILD_DIR/"
cp -r examples "$BUILD_DIR/"
cp -r tests "$BUILD_DIR/"
cp requirements.txt "$BUILD_DIR/"
cp pyproject.toml "$BUILD_DIR/"
cp setup.py "$BUILD_DIR/"
cp README.md "$BUILD_DIR/"
cp LICENSE "$BUILD_DIR/"
cp .gitignore "$BUILD_DIR/"

# NEW: Copy existing binary tools (instead of downloading)
print_status "Copying existing binary tools..."
cp -r bin/* "$BIN_DIR/"

# NEW: Copy Ollama models (only deepseek-coder-6.7b.bin for size optimization)
print_status "Copying Ollama models..."
mkdir -p "$BUILD_DIR/ollama_models"
cp ollama_models/deepseek-coder-6.7b.bin "$BUILD_DIR/ollama_models/"
print_success "Copied deepseek-coder-6.7b.bin (3.6GB) for offline operation"

# Download Python wheels
print_status "Downloading Python wheels..."
pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "$PYTHON_VERSION" --only-binary=:all: --no-deps

# Also download for x86_64 if on ARM, or vice versa
if [ "$ARCH" = "arm64" ]; then
    print_status "Downloading x86_64 wheels for compatibility..."
    pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_10_9_x86_64 --python-version "$PYTHON_VERSION" --only-binary=:all: --no-deps
elif [ "$ARCH" = "x86_64" ]; then
    print_status "Downloading ARM64 wheels for compatibility..."
    pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "$PYTHON_VERSION" --only-binary=:all: --no-deps
fi

# Download static analysis tools (only those not already in bin/)
print_status "Downloading additional static analysis tools..."

# Black
print_status "Downloading Black..."
pip3 download black -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "$PYTHON_VERSION" --only-binary=:all: --no-deps

# Flake8
print_status "Downloading Flake8..."
pip3 download flake8 -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "$PYTHON_VERSION" --only-binary=:all: --no-deps

# YAML Lint
print_status "Installing YAML Lint..."
pip3 download yamllint -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "$PYTHON_VERSION" --only-binary=:all: --no-deps

# Download Node.js and npm (if not available)
print_status "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    print_warning "Node.js not found. Downloading Node.js..."
    NODE_VERSION="20.10.0"
    if [ "$ARCH" = "arm64" ]; then
        NODE_ARCH="darwin-arm64"
    else
        NODE_ARCH="darwin-x64"
    fi
    
    curl -L "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-${NODE_ARCH}.tar.gz" -o "$BUILD_DIR/nodejs.tar.gz"
    tar -xf "$BUILD_DIR/nodejs.tar.gz" -C "$BUILD_DIR/"
    cp -r "$BUILD_DIR/node-v${NODE_VERSION}-${NODE_ARCH}/bin/"* "$BIN_DIR/"
    rm -rf "$BUILD_DIR/node-v${NODE_VERSION}-${NODE_ARCH}" "$BUILD_DIR/nodejs.tar.gz"
fi

# Copy Gemini CLI offline package (optional - will be skipped during install)
print_status "Copying Gemini CLI offline package..."
if [ -f "test-offline-package/gemini-cli/google-gemini-cli-0.1.7.tgz" ]; then
    cp "test-offline-package/gemini-cli/google-gemini-cli-0.1.7.tgz" "$GEMINI_CLI_DIR/"
    print_success "Gemini CLI offline package copied (installation will be skipped due to dependency issues)"
else
    print_warning "Gemini CLI offline package not found. Creating empty directory."
    mkdir -p "$GEMINI_CLI_DIR"
fi

# Make all binaries executable
print_status "Making binaries executable..."
chmod +x "$BIN_DIR"/*

# Create offline installation script
print_status "Creating offline installation script..."
cat > "$BUILD_DIR/install-offline.sh" << 'EOF'
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
EOF

chmod +x "$BUILD_DIR/install-offline.sh"

# Create package manifest
print_status "Creating package manifest..."
cat > "$BUILD_DIR/MANIFEST.txt" << EOF
XPRR Agent Offline Package for MacOS
====================================

Package: $PACKAGE_NAME
Build Date: $(date)
System: $OS $ARCH
Python Version: $PYTHON_VERSION

Contents:
- Python wheels: $(ls "$PACKAGES_DIR"/*.whl 2>/dev/null | wc -l) files
- Binary tools: $(ls "$BIN_DIR" | wc -l) files
- Ollama models: 1 file (deepseek-coder-6.7b.bin - 3.6GB)
- Source code: Complete XPRR agent
- Documentation: Complete docs
- Configuration: Default config files

Binary Tools Included:
- Python: black, flake8
- Java: checkstyle, google-java-format
- Go: gofmt, golint
- Terraform: terraform, tflint
- YAML: yamllint, prettier
- Shell: shellcheck, shfmt

Ollama Models Included:
- deepseek-coder-6.7b.bin (3.6GB) - General code analysis model

Review Engines Supported:
- Security Analysis: Hardcoded credentials, SQL injection, XSS, command injection
- Compliance Checking: License, copyright, naming conventions, forbidden packages
- Best Practices: Documentation, formatting, magic numbers, architecture
- Dependency Analysis: Pre-1.0 version detection for all supported languages
- Test Coverage: Test file detection and coverage analysis
- Documentation: Comment coverage, README analysis

Interactive Features:
- Change Management: Apply and revert suggested changes
- Line-by-line Comments: Detailed feedback on specific code lines
- Review Summaries: Overall assessment and priority actions

Installation:
1. Extract the package
2. Run: ./install-offline.sh
3. Run: ./scripts/start-agent.sh

Usage:
- xprr --help
- xprr review <PR_URL>
- xprr llm list-providers

This package is completely offline and requires no internet connection.
All features mentioned in the README are fully supported.
EOF

# Create the final tar.gz package
print_status "Creating final package..."
cd "$BUILD_DIR"
tar -czf "../${PACKAGE_NAME}.tar.gz" .
cd ..

print_success "Package created: ${PACKAGE_NAME}.tar.gz"
print_success "Size: $(du -h "${PACKAGE_NAME}.tar.gz" | cut -f1)"

echo
echo -e "${GREEN}🎉 Offline package build completed!${NC}"
echo
echo -e "${BLUE}Package:${NC} ${PACKAGE_NAME}.tar.gz"
echo -e "${BLUE}Size:${NC} $(du -h "${PACKAGE_NAME}.tar.gz" | cut -f1)"
echo
echo -e "${BLUE}To test the package:${NC}"
echo "1. Extract: tar -xzf ${PACKAGE_NAME}.tar.gz"
echo "2. Install: ./install-offline.sh"
echo "3. Activate: source venv/bin/activate"
echo "4. Test: ./scripts/start-agent.sh"
echo
echo -e "${GREEN}The package is now ready for air-gapped deployment! 🚀${NC}" 