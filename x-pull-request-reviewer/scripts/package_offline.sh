#!/bin/bash
# Package the agent and all dependencies for offline installation

set -e

AGENT_DIR="$(dirname "$0")/.."
OUTPUT="x-pull-request-reviewer-offline.tar.gz"
OLLAMA_MODELS_DIR="$HOME/.ollama/models"

cd "$AGENT_DIR"

# Copy Ollama model files (assumes 'codellama' is downloaded)
mkdir -p ollama_models
cp -r "$OLLAMA_MODELS_DIR"/* ollama_models/ || echo "Ollama models not found, skipping."

# Create the archive
cd "$AGENT_DIR"
tar --exclude-vcs -czf "$OUTPUT" .gitignore README.md LICENSE pyproject.toml requirements.txt xprr_agent.py agent/ adapters/ llm/ review/ github/ config/ scripts/ tests/ examples/ docs/ docker/ workspace/ ollama_models/

# Cleanup
rm -rf ollama_models

echo "Offline package created: $OUTPUT" 