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

# Download static analysis tools
print_status "Downloading static analysis tools..."

# Black
print_status "Downloading Black..."
pip3 download black -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "$PYTHON_VERSION" --only-binary=:all: --no-deps

# Flake8
print_status "Downloading Flake8..."
pip3 download flake8 -d "$PACKAGES_DIR" --platform macosx_11_0_arm64 --python-version "$PYTHON_VERSION" --only-binary=:all: --no-deps

# Download Terraform
print_status "Downloading Terraform..."
TERRAFORM_VERSION="1.7.0"
if [ "$ARCH" = "arm64" ]; then
    TERRAFORM_ARCH="darwin_arm64"
else
    TERRAFORM_ARCH="darwin_amd64"
fi

curl -L "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_${TERRAFORM_ARCH}.zip" -o "$BUILD_DIR/terraform.zip"
unzip -q "$BUILD_DIR/terraform.zip" -d "$BIN_DIR/"
rm "$BUILD_DIR/terraform.zip"

# Download TFLint
print_status "Downloading TFLint..."
TFLINT_VERSION="v0.58.0"
if [ "$ARCH" = "arm64" ]; then
    TFLINT_ARCH="darwin_arm64"
else
    TFLINT_ARCH="darwin_amd64"
fi

curl -L "https://github.com/terraform-linters/tflint/releases/download/${TFLINT_VERSION}/tflint_${TFLINT_ARCH}.zip" -o "$BUILD_DIR/tflint.zip"
unzip -q "$BUILD_DIR/tflint.zip" -d "$BIN_DIR/"
rm "$BUILD_DIR/tflint.zip"

# Download other tools
print_status "Downloading additional tools..."

# ShellCheck
SHELLCHECK_VERSION="v0.9.0"
if [ "$ARCH" = "arm64" ]; then
    SHELLCHECK_ARCH="darwin.x86_64"
else
    SHELLCHECK_ARCH="darwin.x86_64"
fi

curl -L "https://github.com/koalaman/shellcheck/releases/download/${SHELLCHECK_VERSION}/shellcheck-${SHELLCHECK_VERSION}.${SHELLCHECK_ARCH}.tar.xz" -o "$BUILD_DIR/shellcheck.tar.xz"
tar -xf "$BUILD_DIR/shellcheck.tar.xz" -C "$BUILD_DIR/"
cp "$BUILD_DIR/shellcheck-${SHELLCHECK_VERSION}/shellcheck" "$BIN_DIR/"
rm -rf "$BUILD_DIR/shellcheck-${SHELLCHECK_VERSION}" "$BUILD_DIR/shellcheck.tar.xz"

# shfmt
SHFMT_VERSION="v3.8.0"
if [ "$ARCH" = "arm64" ]; then
    SHFMT_ARCH="darwin_arm64"
else
    SHFMT_ARCH="darwin_amd64"
fi

curl -L "https://github.com/mvdan/sh/releases/download/${SHFMT_VERSION}/shfmt_${SHFMT_VERSION}_${SHFMT_ARCH}" -o "$BIN_DIR/shfmt"

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

# Download Gemini CLI
print_status "Downloading Gemini CLI..."
if command -v npm &> /dev/null; then
    # Download Gemini CLI package
    npm pack @google/gemini-cli --pack-destination "$GEMINI_CLI_DIR"
    
    # Create a local npm registry
    mkdir -p "$NODE_MODULES_DIR/@google"
    cp -r "$GEMINI_CLI_DIR"/* "$NODE_MODULES_DIR/@google/"
    
    print_success "Gemini CLI package downloaded"
else
    print_warning "npm not available. Gemini CLI will need to be installed manually."
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

# Install Python dependencies from local wheels
print_status "Installing Python dependencies from local wheels..."
python3 -m pip install --no-index --find-links=packages -r requirements.txt

# Install the package itself
print_status "Installing XPRR package..."
python3 -m pip install --no-index --find-links=packages -e .

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

print_success "Offline installation completed!"
echo
echo -e "${GREEN}🎉 XPRR is now ready to use!${NC}"
echo
echo -e "${BLUE}Next steps:${NC}"
echo "1. Run: ./scripts/start-agent.sh (to start the agent)"
echo "2. Run: xprr --help (to see available commands)"
echo "3. Run: xprr review <PR_URL> (to review a pull request)"
echo
echo -e "${BLUE}Available commands:${NC}"
echo "  xprr setup          - Setup dependencies and credentials"
echo "  xprr status         - Check agent status"
echo "  xprr review <URL>   - Review a pull request"
echo "  xprr llm list-providers - List available LLM providers"
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
- Python wheels: $(ls "$PACKAGES_DIR"/*.whl | wc -l) files
- Binaries: $(ls "$BIN_DIR" | wc -l) files
- Source code: Complete XPRR agent
- Documentation: Complete docs
- Configuration: Default config files

Dependencies Included:
- Python packages: All required packages
- Static analysis tools: black, flake8, terraform, tflint, shellcheck, shfmt, yamllint
- LLM tools: Gemini CLI (if available)
- Documentation: Complete user guide

Installation:
1. Extract the package
2. Run: ./install-offline.sh
3. Run: ./scripts/start-agent.sh

Usage:
- xprr --help
- xprr review <PR_URL>
- xprr llm list-providers

This package is completely offline and requires no internet connection.
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
echo "3. Test: ./scripts/start-agent.sh"
echo
echo -e "${GREEN}The package is now ready for air-gapped deployment! 🚀${NC}" 