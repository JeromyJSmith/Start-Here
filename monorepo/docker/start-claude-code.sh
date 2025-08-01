#!/bin/bash
set -e

echo "Starting Claude Code with SuperClaude integration..."

# Change to SuperClaude directory
cd /app/superclaude-framework

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install SuperClaude if not already installed
echo "Installing SuperClaude..."
uv pip install -e .

# Install Claude Code requirements if they exist
if [ -f "/app/claude-code/requirements.txt" ]; then
    echo "Installing Claude Code requirements..."
    uv pip install -r /app/claude-code/requirements.txt
fi

echo "SuperClaude setup complete. Starting SuperClaude..."

# Start a simple HTTP server to keep container running
echo "Starting HTTP server on port 8002..."
cd /app/claude-code
python -m http.server 8002