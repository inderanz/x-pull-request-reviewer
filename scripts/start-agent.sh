#!/bin/bash
set -e

# --- CONFIG ---
OLLAMA_DIR="$(dirname "$0")/../ollama"
OLLAMA_MODELS_DIR="$(dirname "$0")/../ollama_models"
LOGS_DIR="$(dirname "$0")/logs"
VENV_DIR="$(dirname "$0")/../venv"
PYTHON="python3"
AGENT_MODULE="xprr_agent"
OLLAMA_PORT=11434
OLLAMA_PID_FILE="$LOGS_DIR/ollama.pid"
PACKAGES_DIR="$(dirname "$0")/../packages"
BIN_DIR="$(dirname "$0")/../bin"
GEMINI_CLI_DIR="$(dirname "$0")/../gemini-cli"
NODE_MODULES_DIR="$(dirname "$0")/../node_modules"

# Required wheels for offline installation
REQUIRED_WHEELS=(
  requests-*.whl
  beautifulsoup4-*.whl
  toml-*.whl
  click-*.whl
  PyYAML-*.whl
  GitPython-*.whl
  rich-*.whl
  tqdm-*.whl
  markdown_it_py-*.whl
  pygments-*.whl
  black-*.whl
  flake8-*.whl
  yamllint-*.whl
)

# Required binaries for static analysis
REQUIRED_BINARIES=(terraform tflint shellcheck shfmt black flake8 yamllint)
REQUIRED_MODEL_DIR="$OLLAMA_MODELS_DIR"

mkdir -p "$LOGS_DIR"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOGS_DIR/startup.log"
}

fail() {
  log "[FATAL] $1"
  exit 1
}

# --- Check if this is an offline package ---
if [ -d "$PACKAGES_DIR" ] && [ -d "$BIN_DIR" ]; then
  log "Detected offline package structure"
  OFFLINE_MODE=true
else
  log "Using online mode (some dependencies may need internet)"
  OFFLINE_MODE=false
fi

# --- Check wheels (offline mode only) ---
if [ "$OFFLINE_MODE" = true ]; then
  log "Checking required Python wheels in $PACKAGES_DIR..."
  WHEELS_AVAILABLE=true
  for pattern in "${REQUIRED_WHEELS[@]}"; do
    if ! ls "$PACKAGES_DIR"/$pattern >/dev/null 2>&1; then
      log "[WARNING] Missing wheel pattern: $pattern"
      WHEELS_AVAILABLE=false
    else
      log "Found wheels matching: $pattern"
    fi
  done

  if [ "$WHEELS_AVAILABLE" = false ]; then
    log "[WARNING] Some wheels are missing. Will use regular pip installation."
  fi
fi

# --- Check binaries ---
log "Checking required binaries in $BIN_DIR..."
BINARIES_AVAILABLE=true
for bin in "${REQUIRED_BINARIES[@]}"; do
  if [ ! -f "$BIN_DIR/$bin" ] || [ ! -x "$BIN_DIR/$bin" ]; then
    log "[WARNING] Missing or not executable: $BIN_DIR/$bin"
    BINARIES_AVAILABLE=false
  else
    log "Found executable: $BIN_DIR/$bin"
  fi
done

if [ "$BINARIES_AVAILABLE" = false ]; then
  log "[WARNING] Some binaries are missing. Some features may not work."
fi

# --- Check Gemini CLI ---
log "Checking Gemini CLI..."
GEMINI_AVAILABLE=false
if command -v gemini &> /dev/null; then
  log "Gemini CLI found in PATH"
  GEMINI_AVAILABLE=true
elif [ -d "$GEMINI_CLI_DIR" ]; then
  log "Gemini CLI package found in $GEMINI_CLI_DIR"
  GEMINI_AVAILABLE=true
else
  log "[WARNING] Gemini CLI not found. Some LLM features may be limited."
fi

# --- Check Ollama model(s) ---
log "Checking Ollama model(s) in $REQUIRED_MODEL_DIR..."
OLLAMA_AVAILABLE=true
if [ ! -d "$REQUIRED_MODEL_DIR" ] || [ -z "$(ls -A "$REQUIRED_MODEL_DIR" 2>/dev/null)" ]; then
  log "[WARNING] No Ollama model found in $REQUIRED_MODEL_DIR. Ollama features will be disabled."
  OLLAMA_AVAILABLE=false
else
  log "Ollama model(s) found."
fi

# --- Warn if GITHUB_TOKEN is not set ---
if [ -z "$GITHUB_TOKEN" ]; then
  log "[WARN] GITHUB_TOKEN is not set. You will be prompted for it if needed."
fi

# --- Detect platform and find Ollama binary ---
OS="$(uname -s)"
OLLAMA_BIN=""
if [[ "$OS" == "Darwin" ]]; then
  # First check for bundled binary in bin directory
  if [ -x "$BIN_DIR/ollama" ]; then
    OLLAMA_BIN="$BIN_DIR/ollama"
    log "Using bundled Ollama binary: $OLLAMA_BIN"
  # Then check for system-wide installation
  elif command -v ollama &> /dev/null; then
    OLLAMA_BIN="$(command -v ollama)"
    log "Using system Ollama: $OLLAMA_BIN"
  fi
elif [[ "$OS" == "Linux" ]]; then
  if [ -x "$BIN_DIR/ollama" ]; then
    OLLAMA_BIN="$BIN_DIR/ollama"
    log "Using bundled Ollama binary: $OLLAMA_BIN"
  elif command -v ollama &> /dev/null; then
    OLLAMA_BIN="$(command -v ollama)"
    log "Using system Ollama: $OLLAMA_BIN"
  fi
else
  fail "Unsupported OS: $OS"
fi

if [ -z "$OLLAMA_BIN" ]; then
  echo -e "\033[1;31m[ERROR] Ollama binary not found!\033[0m"
  echo -e "\033[1;33mTo use Ollama features, please install Ollama:\033[0m"
  echo -e "\033[1;34m  • Official download: https://ollama.ai/download\033[0m"
  echo -e "\033[1;34m  • Homebrew: brew install ollama\033[0m"
  echo -e "\033[1;34m  • Install script: curl -fsSL https://ollama.ai/install.sh | sh\033[0m"
  echo -e "\033[1;34m  • GitHub releases: https://github.com/ollama/ollama/releases\033[0m"
  echo -e "\033[1;34mAfter installing, rerun this script.\033[0m"
  OLLAMA_AVAILABLE=false
fi

# --- Start Ollama if not running ---
if [ "$OLLAMA_AVAILABLE" = true ] && [ -n "$OLLAMA_BIN" ]; then
  if ! pgrep -f "$OLLAMA_BIN serve" > /dev/null; then
    log "Starting Ollama server using $OLLAMA_BIN ..."
    nohup "$OLLAMA_BIN" serve --model-path "$OLLAMA_MODELS_DIR" --port $OLLAMA_PORT > "$LOGS_DIR/ollama.log" 2>&1 &
    echo $! > "$OLLAMA_PID_FILE"
    sleep 5
  else
    log "Ollama already running."
  fi

  # --- Check Ollama health ---
  if ! curl -s "http://localhost:$OLLAMA_PORT/api/tags" > /dev/null; then
    echo -e "\033[1;31m[ERROR] Ollama did not start correctly. Check $LOGS_DIR/ollama.log\033[0m"
    log "[WARNING] Ollama did not start correctly. Check $LOGS_DIR/ollama.log"
  else
    log "Ollama server is healthy."
  fi
elif [ "$OLLAMA_AVAILABLE" = false ]; then
  echo -e "\033[1;33m[WARNING] Skipping Ollama startup (models not available or binary missing).\033[0m"
  log "Skipping Ollama startup (models not available or binary missing)."
fi

# --- Setup Python venv ---
if [ ! -d "$VENV_DIR" ]; then
  log "Creating Python virtual environment..."
  "$PYTHON" -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# --- Install requirements ---
log "Installing Python dependencies..."
pip install --upgrade pip > "$LOGS_DIR/pip.log" 2>&1

if [ "$OFFLINE_MODE" = true ] && [ "$WHEELS_AVAILABLE" = true ]; then
  log "Installing from local wheels (offline mode)..."
  pip install --no-index --find-links="$PACKAGES_DIR" -r ../requirements.txt >> "$LOGS_DIR/pip.log" 2>&1 || fail "Failed to install requirements. See $LOGS_DIR/pip.log."
  log "All Python dependencies installed from local wheels."
else
  log "Installing from PyPI (online mode)..."
  pip install -r ../requirements.txt >> "$LOGS_DIR/pip.log" 2>&1 || fail "Failed to install requirements. See $LOGS_DIR/pip.log."
  log "All Python dependencies installed from PyPI."
fi

# --- Install Gemini CLI if available ---
if [ "$GEMINI_AVAILABLE" = true ] && [ -d "$GEMINI_CLI_DIR" ] && command -v npm &> /dev/null; then
  log "Installing Gemini CLI from local package..."
  npm install -g "$GEMINI_CLI_DIR"/*.tgz >> "$LOGS_DIR/npm.log" 2>&1 || log "[WARNING] Failed to install Gemini CLI locally"
  log "Gemini CLI installed from local package."
fi

# --- Print readiness summary ---
echo "============================================================"
echo "  X-PULL-REQUEST-REVIEWER AGENT READY TO USE!"
if [ "$OFFLINE_MODE" = true ]; then
  echo "  ✅ OFFLINE MODE: All dependencies from local packages"
else
  echo "  🌐 ONLINE MODE: Some dependencies from internet"
fi
echo "  To use: xprr review <PR_URL> (from any directory)"
echo "============================================================"

echo
# --- Print usage examples ---
echo "\033[1;34mEXAMPLES: How to use the XPRR Agent\033[0m"
echo "------------------------------------------------------------"
echo "1. Setup agent and dependencies:"
echo "   xprr setup"
echo

echo "2. Check agent status:"
echo "   xprr status"
echo

echo "3. Review a pull request (default provider):"
echo "   xprr review --pr https://github.com/org/repo/pull/123"
echo

echo "4. Review a pull request with Gemini CLI:"
echo "   xprr review --pr https://github.com/org/repo/pull/123 --provider gemini_cli"
echo

echo "5. Check air-gap readiness:"
echo "   xprr check-airgap"
echo

echo "6. Stop the agent:"
echo "   xprr stop"
echo

echo "For more, run: xprr --help"
echo "------------------------------------------------------------"
echo

# --- Run the agent (optional, comment out if not needed) ---
# log "Starting x-pull-request-reviewer agent..."
# python -m "$AGENT_MODULE" "$@"

# --- Cleanup (optional) ---
# (Add any cleanup logic here) 