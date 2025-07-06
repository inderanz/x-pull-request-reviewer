#!/bin/bash

# Gemini CLI Auth & Project Setup Helper

# Check if gemini CLI is installed
if ! command -v gemini &> /dev/null; then
  echo "[ERROR] Gemini CLI not found. Please install it first."
  exit 1
fi

# Check authentication status
gemini auth status
if [ $? -ne 0 ]; then
  echo "[INFO] You are not authenticated. Running 'gemini auth login'..."
  gemini auth login
fi

# Prompt for GOOGLE_CLOUD_PROJECT
read -p "Enter your Google Cloud Project ID: " PROJECT_ID
export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
echo "[INFO] Exported GOOGLE_CLOUD_PROJECT for this session."

# Offer to persist in shell config
read -p "Persist this variable in your shell config for future sessions? (y/n): " persist
if [[ "$persist" =~ ^[Yy]$ ]]; then
  SHELL_RC="$HOME/.bashrc"
  if [[ "$SHELL" =~ "zsh" ]]; then
    SHELL_RC="$HOME/.zshrc"
  elif [[ "$SHELL" =~ "bash" ]]; then
    SHELL_RC="$HOME/.bashrc"
  elif [[ "$SHELL" =~ "profile" ]]; then
    SHELL_RC="$HOME/.profile"
  fi
  echo "export GOOGLE_CLOUD_PROJECT=\"$PROJECT_ID\"" >> "$SHELL_RC"
  echo "[INFO] Added to $SHELL_RC. Run 'source $SHELL_RC' to activate."
fi 