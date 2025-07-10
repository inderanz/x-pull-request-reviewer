#!/bin/bash

# Gemini CLI Auth & Project Setup Helper

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
cat << 'BANNER'
============================================================
   🔐 Gemini CLI Authentication Setup
============================================================
  Choose your authentication method:
  1. Google Cloud Project ID (Recommended for enterprise)
  2. Gemini API Key (Alternative method)
============================================================
BANNER
echo -e "${NC}"

# Check if gemini CLI is installed
if ! command -v gemini &> /dev/null; then
    echo -e "${RED}[ERROR] Gemini CLI not found. Please install it first.${NC}"
    echo -e "${YELLOW}Run: npm install -g @google/gemini-cli${NC}"
    exit 1
fi

echo -e "${GREEN}[INFO] Gemini CLI found.${NC}"

# Check authentication status
echo -e "${BLUE}[INFO] Checking current authentication status...${NC}"
gemini auth status
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[INFO] You are not authenticated. Running 'gemini auth login'...${NC}"
    gemini auth login
fi

echo -e "${BLUE}[INFO] Choose your authentication method:${NC}"
echo "1. Google Cloud Project ID (Recommended for enterprise use)"
echo "2. Gemini API Key (Alternative method)"
echo "3. Both (for maximum compatibility)"

read -p "Enter your choice [1-3]: " choice

case $choice in
    1)
        echo -e "${BLUE}[INFO] Setting up Google Cloud Project ID authentication...${NC}"
        read -p "Enter your Google Cloud Project ID: " PROJECT_ID
        export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
        echo -e "${GREEN}[INFO] Exported GOOGLE_CLOUD_PROJECT for this session.${NC}"
        
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
            echo -e "${GREEN}[INFO] Added to $SHELL_RC. Run 'source $SHELL_RC' to activate.${NC}"
        fi
        ;;
    2)
        echo -e "${BLUE}[INFO] Setting up Gemini API Key authentication...${NC}"
        echo -e "${YELLOW}[INFO] Get your API key from: https://aistudio.google.com/app/apikey${NC}"
        read -p "Enter your Gemini API Key: " API_KEY
        export GEMINI_API_KEY="$API_KEY"
        echo -e "${GREEN}[INFO] Exported GEMINI_API_KEY for this session.${NC}"
        
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
            echo "export GEMINI_API_KEY=\"$API_KEY\"" >> "$SHELL_RC"
            echo -e "${GREEN}[INFO] Added to $SHELL_RC. Run 'source $SHELL_RC' to activate.${NC}"
        fi
        ;;
    3)
        echo -e "${BLUE}[INFO] Setting up both authentication methods...${NC}"
        
        # Google Cloud Project ID
        read -p "Enter your Google Cloud Project ID: " PROJECT_ID
        export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
        echo -e "${GREEN}[INFO] Exported GOOGLE_CLOUD_PROJECT for this session.${NC}"
        
        # Gemini API Key
        echo -e "${YELLOW}[INFO] Get your API key from: https://aistudio.google.com/app/apikey${NC}"
        read -p "Enter your Gemini API Key: " API_KEY
        export GEMINI_API_KEY="$API_KEY"
        echo -e "${GREEN}[INFO] Exported GEMINI_API_KEY for this session.${NC}"
        
        # Offer to persist both in shell config
        read -p "Persist both variables in your shell config for future sessions? (y/n): " persist
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
            echo "export GEMINI_API_KEY=\"$API_KEY\"" >> "$SHELL_RC"
            echo -e "${GREEN}[INFO] Added both to $SHELL_RC. Run 'source $SHELL_RC' to activate.${NC}"
        fi
        ;;
    *)
        echo -e "${RED}[ERROR] Invalid choice. Please run the script again.${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}[SUCCESS] Gemini CLI authentication setup completed!${NC}"
echo
echo -e "${BLUE}Next steps:${NC}"
echo "1. Test authentication: gemini auth status"
echo "2. Test with XPRR: xprr review <PR_URL>"
echo "3. If you chose to persist variables, restart your terminal or run: source $SHELL_RC"
echo
echo -e "${BLUE}Reference:${NC}"
echo "- Google Cloud Project ID: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/authentication.md"
echo "- Gemini API Key: https://aistudio.google.com/app/apikey" 