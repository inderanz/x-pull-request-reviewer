#!/bin/bash

echo "--- Checking GitHub Remote URL ---"
git remote -v | grep github.com

REMOTE_URL=$(git remote get-url origin 2>/dev/null)
if [[ $REMOTE_URL == git@github.com:* ]]; then
    echo "\nYou are using SSH for GitHub access."
    echo "Testing SSH connection..."
    ssh -T git@github.com || true
    echo "\nIf you see a welcome message, your SSH key is set up."
elif [[ $REMOTE_URL == https://github.com/* ]]; then
    echo "\nYou are using HTTPS for GitHub access."
    echo "Credential helper in use:"
    git config --global credential.helper
    echo "\nIf you can clone/push, your credentials are cached."
else
    echo "\nCould not determine remote URL or not a GitHub repo."
fi

echo "\n--- Checking GITHUB_TOKEN environment variable ---"
if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "GITHUB_TOKEN is NOT set."
    echo "To post PR comments, set it with:"
    echo "  export GITHUB_TOKEN=ghp_xxx..."
else
    echo "GITHUB_TOKEN is set."
    echo "First 8 chars: ${GITHUB_TOKEN:0:8}..."
fi 