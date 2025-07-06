#!/bin/bash

# XPRR Offline Installation Script
# This script installs XPRR completely offline with comprehensive setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

# Function to print status messages
print_status() {
    echo -e "${CYAN}[INFO]${NC} $1"
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

print_step() {
    echo -e "${PURPLE}➤${NC} $1"
}

# Function to check system requirements
check_system_requirements() {
    print_step "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This package is designed for macOS. Detected: $OSTYPE"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_success "Python $PYTHON_VERSION detected"
    
    # Check Node.js for Gemini CLI
    if ! command -v node &> /dev/null; then
        print_warning "Node.js not found. Gemini CLI installation will be skipped"
        NODE_AVAILABLE=false
    else
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION detected"
        NODE_AVAILABLE=true
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_warning "npm not found. Gemini CLI installation will be skipped"
        NPM_AVAILABLE=false
    else
        NPM_VERSION=$(npm --version)
        print_success "npm $NPM_VERSION detected"
        NPM_AVAILABLE=true
    fi
    
    # Check available disk space (need at least 5GB)
    DISK_SPACE=$(df . | awk 'NR==2 {print $4}')
    DISK_SPACE_GB=$((DISK_SPACE / 1024 / 1024))
    if [ $DISK_SPACE_GB -lt 5 ]; then
        print_warning "Low disk space: ${DISK_SPACE_GB}GB available. Recommended: 5GB+"
    else
        print_success "Disk space: ${DISK_SPACE_GB}GB available"
    fi
}

# Function to validate package contents
validate_package() {
    print_step "Validating package contents..."
    
    REQUIRED_FILES=(
        "requirements.txt"
        "pyproject.toml"
        "src/"
        "packages/"
        "ollama_models/"
        "bin/"
        "config/"
        "scripts/"
    )
    
    MISSING_FILES=()
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -e "$file" ]; then
            MISSING_FILES+=("$file")
        fi
    done
    
    if [ ${#MISSING_FILES[@]} -gt 0 ]; then
        print_error "Missing required files: ${MISSING_FILES[*]}"
        exit 1
    fi
    
    # Check Ollama model
    if [ -f "ollama_models/deepseek-coder-6.7b.bin" ]; then
        MODEL_SIZE=$(du -h ollama_models/deepseek-coder-6.7b.bin | cut -f1)
        print_success "Ollama model found: deepseek-coder-6.7b.bin ($MODEL_SIZE)"
    else
        print_warning "Ollama model not found. Will download during first use"
    fi
    
    # Check Python packages
    PACKAGE_COUNT=$(ls packages/*.whl 2>/dev/null | wc -l)
    print_success "Python packages: $PACKAGE_COUNT wheels available"
    
    # Check Gemini CLI package
    if [ -f "gemini-cli/google-gemini-cli-0.1.7.tgz" ]; then
        CLI_SIZE=$(du -h gemini-cli/google-gemini-cli-0.1.7.tgz | cut -f1)
        print_success "Gemini CLI package found: $CLI_SIZE"
    else
        print_warning "Gemini CLI package not found"
    fi
}

# Function to setup Python environment
setup_python_env() {
    print_step "Setting up Python environment..."
    
    # Create venv if not exists
    if [ ! -d venv ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Using existing virtual environment"
    fi
    
    # Activate venv
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip --no-index --find-links=packages
    
    # Install Python wheels
    print_status "Installing Python dependencies..."
    pip install --no-index --find-links=packages -r requirements.txt
    
    print_success "Python environment setup complete"
}

# Function to setup Gemini CLI
setup_gemini_cli() {
    if [ "$NODE_AVAILABLE" = false ] || [ "$NPM_AVAILABLE" = false ]; then
        print_warning "Skipping Gemini CLI setup (Node.js/npm not available)"
        return
    fi
    
    print_step "Setting up Gemini CLI..."
    
    # Check if Gemini CLI is already installed
    if command -v gemini &> /dev/null; then
        GEMINI_VERSION=$(gemini --version 2>/dev/null || echo "unknown")
        print_status "Gemini CLI already installed: $GEMINI_VERSION"
        
        # Check authentication status
        if [ -n "$GEMINI_API_KEY" ] || [ -n "$GOOGLE_CLOUD_PROJECT" ]; then
            print_success "Gemini CLI authentication verified"
            return
        else
            print_warning "Gemini CLI not authenticated"
        fi
    fi
    
    # Install Gemini CLI
    if [ -f "gemini-cli/google-gemini-cli-0.1.7.tgz" ]; then
        print_status "Installing Gemini CLI from offline package..."
        mkdir -p temp-gemini-cli
        tar -xzf gemini-cli/google-gemini-cli-0.1.7.tgz -C temp-gemini-cli
        
        cd temp-gemini-cli
        if npm install -g . --force 2>/dev/null; then
            print_success "Gemini CLI installed from offline package"
        else
            print_warning "Failed to install from offline package, trying direct install..."
            npm install -g @google/genai --force
        fi
        cd ..
        rm -rf temp-gemini-cli
    else
        print_status "Installing Gemini CLI from npm registry..."
        npm install -g @google/genai --force
    fi
    
    # Verify installation
    if command -v gemini &> /dev/null; then
        GEMINI_VERSION=$(gemini --version 2>/dev/null || echo "unknown")
        print_success "Gemini CLI installed: $GEMINI_VERSION"
    else
        print_error "Failed to install Gemini CLI"
        return
    fi
    
    # Setup authentication
    print_status "Setting up Gemini CLI authentication..."
    echo -e "${YELLOW}Choose authentication method:${NC}"
    echo "1. Google Cloud Project ID (recommended for enterprise)"
    echo "2. Gemini API Key (simpler for personal use)"
    echo "3. Skip authentication (setup later)"
    
    read -p "Enter choice (1-3): " auth_choice
    
    case $auth_choice in
        1)
            read -p "Enter Google Cloud Project ID: " project_id
            # Create config directory
            mkdir -p ~/.config/gemini
            # Set project ID in environment or config
            echo "export GOOGLE_CLOUD_PROJECT=$project_id" >> ~/.bashrc
            echo "export GOOGLE_CLOUD_PROJECT=$project_id" >> ~/.zshrc
            export GOOGLE_CLOUD_PROJECT="$project_id"
            print_success "Google Cloud Project ID configured"
            print_status "You may need to restart your terminal or run: source ~/.bashrc"
            ;;
        2)
            read -s -p "Enter Gemini API Key: " api_key
            echo
            # Create config directory
            mkdir -p ~/.config/gemini
            # Set API key in environment
            echo "export GEMINI_API_KEY=$api_key" >> ~/.bashrc
            echo "export GEMINI_API_KEY=$api_key" >> ~/.zshrc
            export GEMINI_API_KEY="$api_key"
            print_success "Gemini API Key configured"
            print_status "You may need to restart your terminal or run: source ~/.bashrc"
            ;;
        3)
            print_status "Authentication skipped. Run 'xprr setup-gemini' later to configure"
            ;;
        *)
            print_warning "Invalid choice. Authentication skipped"
            ;;
    esac
}

# Function to setup Ollama
setup_ollama() {
    print_step "Setting up Ollama..."
    
    # Check if Ollama binary exists
    if [ -f "bin/ollama" ]; then
        print_status "Found Ollama binary in package"
        chmod +x bin/ollama
        
        # Add to PATH for this session
        export PATH="$(pwd)/bin:$PATH"
        
        # Check if Ollama is running
        if ollama list &>/dev/null; then
            print_success "Ollama is running and accessible"
        else
            print_status "Starting Ollama service..."
            if ollama serve &>/dev/null & then
                sleep 3
                if ollama list &>/dev/null; then
                    print_success "Ollama service started"
                else
                    print_warning "Failed to start Ollama service"
                fi
            else
                print_warning "Failed to start Ollama service"
            fi
        fi
        
        # Check for models
        if ollama list | grep -q "deepseek-coder"; then
            print_success "DeepSeek Coder model found"
        else
            print_status "Loading DeepSeek Coder model..."
            if [ -f "ollama_models/deepseek-coder-6.7b.bin" ]; then
                ollama create deepseek-coder -f ollama_models/deepseek-coder-6.7b.bin
                print_success "DeepSeek Coder model loaded from offline package"
            else
                print_warning "Model file not found. Will download during first use"
            fi
        fi
    else
        print_warning "Ollama binary not found in package"
    fi
}

# Function to create shortcuts and scripts
create_shortcuts() {
    print_step "Creating shortcuts and scripts..."
    
    # Create xprr command
    cat > xprr << 'EOF'
#!/bin/bash
# XPRR Command Wrapper
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
export PATH="$SCRIPT_DIR/bin:$PATH"
python -m src.xprr_agent "$@"
EOF
    
    chmod +x xprr
    print_success "Created 'xprr' command"
    
    # Create setup script
    cat > setup-gemini.sh << 'EOF'
#!/bin/bash
# Gemini CLI Setup Script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"
export PATH="$SCRIPT_DIR/bin:$PATH"
python -m src.xprr_agent setup-gemini
EOF
    
    chmod +x setup-gemini.sh
    print_success "Created 'setup-gemini.sh' script"
}

# Function to run post-installation tests
run_tests() {
    print_step "Running post-installation tests..."
    
    # Test Python environment
    if python -c "import click, git, requests, yaml" 2>/dev/null; then
        print_success "Python dependencies verified"
    else
        print_warning "Some Python dependencies may be missing"
    fi
    
    # Test XPRR command
    if python -m src.xprr_agent --help &>/dev/null; then
        print_success "XPRR command verified"
    else
        print_error "XPRR command failed"
        return 1
    fi
    
    # Test Gemini CLI
    if command -v gemini &> /dev/null; then
        if gemini --help &>/dev/null; then
            print_success "Gemini CLI verified"
        else
            print_warning "Gemini CLI may not be working properly"
        fi
    fi
    
    # Test Ollama
    if command -v ollama &> /dev/null; then
        if ollama list &>/dev/null; then
            print_success "Ollama verified"
        else
            print_warning "Ollama may not be working properly"
        fi
    fi
}

# Function to display post-installation information
show_post_install_info() {
    echo
    echo -e "${GREEN}🎉 XPRR Installation Complete!${NC}"
    echo
    echo -e "${CYAN}Next Steps:${NC}"
    echo "1. Activate the environment: source venv/bin/activate"
    echo "2. Run XPRR: ./xprr --help"
    echo "3. Setup Gemini CLI: ./setup-gemini.sh"
    echo "4. Test with a PR: ./xprr review <PR_URL>"
    echo
    echo -e "${CYAN}Available Commands:${NC}"
    echo "  ./xprr review <PR_URL>     - Review a pull request"
    echo "  ./xprr review --repo .     - Review local repository"
    echo "  ./xprr setup-gemini        - Setup Gemini CLI authentication"
    echo "  ./xprr config              - Show configuration"
    echo
    echo -e "${CYAN}Documentation:${NC}"
    echo "  README.md                  - Main documentation"
    echo "  docs/                      - Detailed guides"
    echo "  examples/                  - Usage examples"
    echo
    echo -e "${YELLOW}Note:${NC} This is a beta release (v0.0.2). For production use,"
    echo "      ensure all authentication is properly configured."
    echo
    echo -e "${BLUE}✨ Happy Code Reviewing! ✨${NC}"
}

# Main installation flow
main() {
    echo -e "${GREEN}🚀 Starting XPRR offline installation...${NC}"
    echo
    
    check_system_requirements
    echo
    
    validate_package
    echo
    
    setup_python_env
    echo
    
    setup_gemini_cli
    echo
    
    setup_ollama
    echo
    
    create_shortcuts
    echo
    
    run_tests
    echo
    
    show_post_install_info
}

# Run main function
main "$@" 