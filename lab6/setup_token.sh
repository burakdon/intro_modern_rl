#!/bin/bash

# Setup script for OpenAI API key
# This will add the key to your shell profile for persistent use
# Replace YOUR_OPENAI_API_KEY with your actual OpenAI API key

TOKEN="YOUR_OPENAI_API_KEY"
SHELL_PROFILE=""

# Detect shell and set profile file
if [ -n "$ZSH_VERSION" ]; then
    SHELL_PROFILE="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_PROFILE="$HOME/.bashrc"
else
    SHELL_PROFILE="$HOME/.profile"
fi

# Check if token is already set
if grep -q "OPENAI_API_KEY" "$SHELL_PROFILE" 2>/dev/null; then
    echo "⚠️  OPENAI_API_KEY already exists in $SHELL_PROFILE"
    echo "   Please update it manually or remove the old entry first."
else
    # Add token to shell profile
    echo "" >> "$SHELL_PROFILE"
    echo "# OpenAI API Key for Lab 6" >> "$SHELL_PROFILE"
    echo "export OPENAI_API_KEY=\"$TOKEN\"" >> "$SHELL_PROFILE"
    echo "✅ API key added to $SHELL_PROFILE"
    echo ""
    echo "⚠️  Don't forget to replace YOUR_OPENAI_API_KEY with your actual key!"
    echo ""
    echo "To use it in this session, run:"
    echo "  source $SHELL_PROFILE"
    echo ""
    echo "Or restart your terminal."
fi

# Also set for current session
export OPENAI_API_KEY="$TOKEN"
echo "✅ API key set for current session (remember to replace YOUR_OPENAI_API_KEY)"
