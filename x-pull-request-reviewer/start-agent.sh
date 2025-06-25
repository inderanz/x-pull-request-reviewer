#!/bin/bash
set -e

# --- CONFIG ---
OLLAMA_DIR="$(dirname "$0")/ollama"
OLLAMA_MODELS_DIR="$(dirname "$0")/ollama_models"
LOGS_DIR="$(dirname "$0")/logs"
VENV_DIR="$(dirname "$0")/venv"
PYTHON="python3"
AGENT_MODULE="xprr_agent"
OLLAMA_PORT=11434
OLLAMA_PID_FILE="$LOGS_DIR/ollama.pid"

mkdir -p "$LOGS_DIR"

# --- Detect platform ---
OS="$(uname -s)"
if [[ "$OS" == "Darwin" ]]; then
  OLLAMA_BIN="$OLLAMA_DIR/ollama-macos"
elif [[ "$OS" == "Linux" ]]; then
  OLLAMA_BIN="$OLLAMA_DIR/ollama-linux"
else
  echo "[ERROR] Unsupported OS: $OS" | tee -a "$LOGS_DIR/startup.log"
  exit 1
fi

# --- Start Ollama if not running ---
if ! pgrep -f "$OLLAMA_BIN serve" > /dev/null; then
  echo "[INFO] Starting Ollama server..." | tee -a "$LOGS_DIR/startup.log"
  nohup "$OLLAMA_BIN" serve --model-path "$OLLAMA_MODELS_DIR" --port $OLLAMA_PORT > "$LOGS_DIR/ollama.log" 2>&1 &
  echo $! > "$OLLAMA_PID_FILE"
  sleep 5
else
  echo "[INFO] Ollama already running." | tee -a "$LOGS_DIR/startup.log"
fi

# --- Check Ollama health ---
if ! curl -s "http://localhost:$OLLAMA_PORT/api/tags" > /dev/null; then
  echo "[ERROR] Ollama did not start correctly. Check $LOGS_DIR/ollama.log" | tee -a "$LOGS_DIR/startup.log"
  exit 1
fi

# --- Setup Python venv ---
if [ ! -d "$VENV_DIR" ]; then
  echo "[INFO] Creating Python virtual environment..." | tee -a "$LOGS_DIR/startup.log"
  "$PYTHON" -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# --- Install requirements ---
if [ -f "requirements.txt" ]; then
  echo "[INFO] Installing Python dependencies..." | tee -a "$LOGS_DIR/startup.log"
  pip install --upgrade pip > "$LOGS_DIR/pip.log" 2>&1
  pip install -r requirements.txt >> "$LOGS_DIR/pip.log" 2>&1
fi

# --- Run the agent ---
echo "[INFO] Starting x-pull-request-reviewer agent..." | tee -a "$LOGS_DIR/startup.log"
python -m "$AGENT_MODULE" "$@"

# --- Cleanup (optional) ---
# (Add any cleanup logic here) 