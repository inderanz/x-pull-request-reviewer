#!/bin/bash
# X-Pull-Request-Reviewer Production Installation Script

set -e

echo "============================================================"
echo "   🚀 X-PULL-REQUEST-REVIEWER Production Installation"
echo "============================================================"

# Detect OS
OS="$(uname -s)"
ARCH="$(uname -m)"

echo "[INFO] Detected OS: $OS $ARCH"

# Create installation directory
INSTALL_DIR="/usr/local/bin"
sudo mkdir -p "$INSTALL_DIR"

# Copy executable
echo "[INFO] Installing xprr to $INSTALL_DIR"
sudo cp xprr "$INSTALL_DIR/"
sudo chmod +x "$INSTALL_DIR/xprr"

# Create symlink
if [ ! -L "$INSTALL_DIR/xprr_agent" ]; then
    sudo ln -sf "$INSTALL_DIR/xprr" "$INSTALL_DIR/xprr_agent"
fi

# Install Python dependencies
echo "[INFO] Installing Python dependencies..."
python3 -m pip install --user -r requirements.txt

# Download Ollama if not present
if [ ! -f "bin/ollama" ]; then
    echo "[INFO] Downloading Ollama..."
    mkdir -p bin
    if [[ "$OS" == "Darwin" ]]; then
        curl -L https://ollama.ai/download/ollama-darwin -o bin/ollama
    elif [[ "$OS" == "Linux" ]]; then
        curl -L https://ollama.ai/download/ollama-linux -o bin/ollama
    fi
    chmod +x bin/ollama
fi

# Pull CodeLlama model
echo "[INFO] Pulling CodeLlama model..."
./bin/ollama pull codellama:7b

echo "============================================================"
echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  xprr setup                    # Setup dependencies"
echo "  xprr review <PR_NUMBER>       # Review a pull request"
echo ""
echo "Environment:"
echo "  export GITHUB_TOKEN=your_token  # Set GitHub token"
echo "============================================================"

AGENT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULT_BIN="$HOME/bin"

# Prompt for install location
read -p "Where do you want to install the xprr CLI? [default: $DEFAULT_BIN] " USER_BIN
USER_BIN="${USER_BIN:-$DEFAULT_BIN}"

# Loop until we have a writable directory
while true; do
  if [ ! -d "$USER_BIN" ]; then
    read -p "Directory $USER_BIN does not exist. Create it? [Y/n] " CREATE_DIR
    CREATE_DIR=${CREATE_DIR:-Y}
    if [[ "$CREATE_DIR" =~ ^[Yy]$ ]]; then
      mkdir -p "$USER_BIN" || { echo "[ERROR] Could not create $USER_BIN"; exit 1; }
      echo "[INFO] Created $USER_BIN"
    else
      read -p "Please enter a different directory: " USER_BIN
      continue
    fi
  fi
  if [ ! -w "$USER_BIN" ]; then
    echo "[ERROR] Directory $USER_BIN is not writable."
    read -p "Please enter a different directory: " USER_BIN
    continue
  fi
  break
done

# Symlink or copy xprr to chosen bin dir
if [ -f "$AGENT_DIR/xprr" ]; then
  ln -sf "$AGENT_DIR/xprr" "$USER_BIN/xprr"
  chmod +x "$USER_BIN/xprr"
  echo "[INFO] xprr CLI installed to $USER_BIN/xprr"
else
  echo "[ERROR] xprr script not found in $AGENT_DIR"
  exit 1
fi

# Add chosen bin dir to PATH in shell profile if not present
if ! echo "$PATH" | grep -q "$USER_BIN"; then
  SHELL_PROFILE="$HOME/.bashrc"
  [ -n "$ZSH_VERSION" ] && SHELL_PROFILE="$HOME/.zshrc"
  if ! grep -q "export PATH=\"$USER_BIN:\$PATH\"" "$SHELL_PROFILE" 2>/dev/null; then
    echo "export PATH=\"$USER_BIN:\$PATH\"" >> "$SHELL_PROFILE"
    echo "[INFO] Added $USER_BIN to PATH in $SHELL_PROFILE"
  fi
  export PATH="$USER_BIN:$PATH"
fi

echo "[INFO] Installation complete. You can now run: xprr review <PR_URL> from any directory."
