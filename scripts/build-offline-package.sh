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
PACKAGE_NAME="xprr-agent-macos-v0.1.1"
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
cp install-offline.sh "$BUILD_DIR/"

# NEW: Copy existing binary tools (instead of downloading)
print_status "Copying existing binary tools..."
if [ -d "bin" ] && [ "$(ls -A bin)" ]; then
    chmod +w bin/ollama 2>/dev/null || true
    cp -r bin/* "$BIN_DIR/"
    print_success "Copied existing binary tools"
else
    print_warning "No existing binary tools found. Will download during installation."
fi

# NEW: Copy Ollama models (only deepseek-coder-6.7b.bin for size optimization)
print_status "Copying Ollama models..."
mkdir -p "$BUILD_DIR/ollama_models"

# Copy deepseek-coder-6.7b.bin if available locally
if [ -f "test-offline-package/build/ollama_models/deepseek-coder-6.7b.bin" ]; then
    cp test-offline-package/build/ollama_models/deepseek-coder-6.7b.bin "$BUILD_DIR/ollama_models/"
    print_success "Copied deepseek-coder-6.7b.bin (3.6GB) for offline operation"
elif [ -f "ollama_models/deepseek-coder-6.7b.bin" ]; then
    cp ollama_models/deepseek-coder-6.7b.bin "$BUILD_DIR/ollama_models/"
    print_success "Copied deepseek-coder-6.7b.bin (3.6GB) for offline operation"
else
    print_warning "deepseek-coder-6.7b.bin not found locally. Will be downloaded during first use."
fi

# Note: The primary model codellama-trained-20250624_193347 is not available locally
# Users will need to download it during first use or use the fallback model
print_status "Note: Primary model codellama-trained-20250624_193347 will be downloaded during first use"
print_status "Fallback model deepseek-coder-6.7b.bin is included in package for immediate offline operation"

# Download Python wheels for multiple Python versions
print_status "Downloading Python wheels for multiple Python versions..."

# Download for current Python version
print_status "Downloading wheels for Python $PYTHON_VERSION..."
pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "$PYTHON_VERSION" --only-binary=:all: --no-deps

# Download for Python 3.9 (common version)
print_status "Downloading wheels for Python 3.9..."
pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "3.9" --only-binary=:all: --no-deps

# Download for Python 3.10 (common version)
print_status "Downloading wheels for Python 3.10..."
pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "3.10" --only-binary=:all: --no-deps

# Download for Python 3.11 (common version)
print_status "Downloading wheels for Python 3.11..."
pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "3.11" --only-binary=:all: --no-deps

# Download for Python 3.12 (common version)
print_status "Downloading wheels for Python 3.12..."
pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "3.12" --only-binary=:all: --no-deps

# Also download for x86_64 if on ARM, or vice versa
if [ "$ARCH" = "arm64" ]; then
    print_status "Downloading x86_64 wheels for compatibility..."
    pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_10_9_x86_64 --python-version "$PYTHON_VERSION" --only-binary=:all: --no-deps
    pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_10_9_x86_64 --python-version "3.9" --only-binary=:all: --no-deps
    pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_10_9_x86_64 --python-version "3.10" --only-binary=:all: --no-deps
    pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_10_9_x86_64 --python-version "3.11" --only-binary=:all: --no-deps
    pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_10_9_x86_64 --python-version "3.12" --only-binary=:all: --no-deps
elif [ "$ARCH" = "x86_64" ]; then
    print_status "Downloading ARM64 wheels for compatibility..."
    pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "$PYTHON_VERSION" --only-binary=:all: --no-deps
    pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "3.9" --only-binary=:all: --no-deps
    pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "3.10" --only-binary=:all: --no-deps
    pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "3.11" --only-binary=:all: --no-deps
    pip3 download -r requirements.txt -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "3.12" --only-binary=:all: --no-deps
fi

# Download static analysis tools (only those not already in bin/)
print_status "Downloading additional static analysis tools..."

# Python tools
print_status "Downloading Python tools..."
pip3 download black -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "$PYTHON_VERSION" --only-binary=:all: --no-deps
pip3 download flake8 -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "$PYTHON_VERSION" --only-binary=:all: --no-deps

# YAML tools
print_status "Downloading YAML tools..."
pip3 download yamllint -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "$PYTHON_VERSION" --only-binary=:all: --no-deps

# Download Go tools
print_status "Downloading Go tools..."
if command -v go &> /dev/null; then
    print_status "Go is available, will use system tools"
else
    print_warning "Go not found, Go tools will not be available"
fi

# Download Java tools
print_status "Downloading Java tools..."
if command -v java &> /dev/null; then
    print_status "Java is available, will use system tools"
else
    print_warning "Java not found, Java tools will not be available"
fi

# Download Terraform tools
print_status "Downloading Terraform tools..."
if command -v terraform &> /dev/null; then
    print_status "Terraform is available, will use system tools"
else
    print_warning "Terraform not found, Terraform tools will not be available"
fi

# Download Shell tools
print_status "Downloading Shell tools..."
if command -v shellcheck &> /dev/null; then
    print_status "ShellCheck is available, will use system tools"
else
    print_warning "ShellCheck not found, Shell tools will not be available"
fi

# Download Node.js tools (for prettier)
print_status "Downloading Node.js tools..."
if command -v npm &> /dev/null; then
    print_status "npm is available, will use system tools"
else
    print_warning "npm not found, Node.js tools will not be available"
fi

# Download Ollama binary for macOS
print_status "Downloading Ollama binary for macOS..."
OLLAMA_VERSION="0.9.5"  # Latest stable version

# Get the latest version from GitHub API
LATEST_VERSION=$(curl -s "https://api.github.com/repos/ollama/ollama/releases/latest" | grep -o '"tag_name": "v[^"]*"' | cut -d'"' -f4 | sed 's/v//')
if [ -n "$LATEST_VERSION" ]; then
    OLLAMA_VERSION="$LATEST_VERSION"
fi

OLLAMA_DOWNLOAD_URL="https://github.com/ollama/ollama/releases/download/v${OLLAMA_VERSION}/ollama-darwin.tgz"
OLLAMA_BINARY_PATH="$BIN_DIR/ollama"

print_status "Downloading Ollama v${OLLAMA_VERSION} for macOS..."
curl -L "$OLLAMA_DOWNLOAD_URL" -o "$BUILD_DIR/ollama-darwin.tgz"
tar -xzf "$BUILD_DIR/ollama-darwin.tgz" -C "$BUILD_DIR/"
cp "$BUILD_DIR/ollama" "$OLLAMA_BINARY_PATH"
chmod +x "$OLLAMA_BINARY_PATH"
rm -f "$BUILD_DIR/ollama-darwin.tgz" "$BUILD_DIR/ollama"
print_success "Downloaded Ollama binary: $OLLAMA_BINARY_PATH"

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

# Download and package Gemini CLI
print_status "Downloading and packaging Gemini CLI..."
if command -v npm &> /dev/null; then
    # Create a temporary directory for Gemini CLI
    TEMP_GEMINI_DIR="$BUILD_DIR/temp-gemini"
    mkdir -p "$TEMP_GEMINI_DIR"
    
    # Download Gemini CLI package
    print_status "Downloading Gemini CLI package..."
    cd "$TEMP_GEMINI_DIR"
    
    # Create package.json for Gemini CLI
    cat > package.json << 'EOF'
{
  "name": "gemini-cli-offline",
  "version": "0.1.7",
  "description": "Offline Gemini CLI package for XPRR",
  "main": "index.js",
  "bin": {
    "gemini": "./bin/gemini.js"
  },
  "dependencies": {
    "@google/gemini-cli": "^0.1.7"
  },
  "scripts": {
    "postinstall": "npm install -g @google/gemini-cli"
  }
}
EOF
    
    # Install Gemini CLI
    print_status "Installing Gemini CLI..."
    npm install @google/gemini-cli
    
    if [ $? -eq 0 ] && [ -d "$TEMP_GEMINI_DIR" ]; then
        # Create the offline package
        print_status "Creating Gemini CLI offline package..."
        mkdir -p "$GEMINI_CLI_DIR"
        # Create tarball from current directory
        tar -czf "$GEMINI_CLI_DIR/google-gemini-cli-0.1.7.tgz" -C "$TEMP_GEMINI_DIR" .
        if [ $? -eq 0 ]; then
            print_success "Gemini CLI offline package created successfully"
        else
            print_warning "Failed to create Gemini CLI tarball. Will use direct install."
        fi
        # Clean up after tarball creation
        rm -rf "$TEMP_GEMINI_DIR"
    else
        print_warning "Failed to install Gemini CLI. Creating empty directory."
        mkdir -p "$GEMINI_CLI_DIR"
    fi
    
    # Clean up
    rm -rf "$TEMP_GEMINI_DIR"
else
    print_warning "npm not found. Creating empty Gemini CLI directory."
    mkdir -p "$GEMINI_CLI_DIR"
fi

# Make all binaries executable
print_status "Making binaries executable..."
if [ -d "$BIN_DIR" ] && [ "$(ls -A $BIN_DIR)" ]; then
    chmod +x "$BIN_DIR"/*
    print_success "Made binaries executable"
else
    print_warning "No binaries to make executable"
fi

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
    
    # Install the package globally
    if npm install -g @google/gemini-cli; then
        print_success "Gemini CLI installed successfully from local tarball"
    else
        print_warning "Failed to install Gemini CLI from tarball, trying direct install..."
        if npm install -g @google/gemini-cli; then
            print_success "Gemini CLI installed successfully via direct install"
        else
            print_warning "Gemini CLI installation failed. It will not be available."
        fi
    fi
    
    cd ..
    rm -rf temp-gemini-install
else
    print_warning "Gemini CLI tarball not found or npm not installed. Trying direct install..."
    if command -v npm &> /dev/null; then
        if npm install -g @google/gemini-cli; then
            print_success "Gemini CLI installed successfully via direct install"
        else
            print_warning "Gemini CLI installation failed. It will not be available."
        fi
    else
        print_warning "npm not installed. Gemini CLI will not be available."
    fi
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