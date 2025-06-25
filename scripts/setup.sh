#!/bin/bash
# Setup script for x-pull-request-reviewer

set -e

# Ensure VSCode is installed
if ! command -v code &> /dev/null; then
  echo "VSCode (code) not found in PATH. Please install Visual Studio Code and add 'code' to your PATH."
  exit 1
fi

echo "VSCode found: $(which code)"

# Install GitHub Pull Requests and Issues extension
if ! code --list-extensions | grep -q github.vscode-pull-request-github; then
  echo "Installing GitHub Pull Requests and Issues extension..."
  code --install-extension github.vscode-pull-request-github --force
else
  echo "GitHub Pull Requests and Issues extension already installed."
fi

# Launch VSCode in the workspace root
code .

echo "Environment setup complete. VSCode launched with GitHub PR extension."

echo "Setting up environment..."
# Add installation steps here 