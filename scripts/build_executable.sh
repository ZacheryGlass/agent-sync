#!/bin/bash
set -e

# Ensure we are in the root directory
cd "$(dirname "$0")/.."

# Check for venv capability
if ! python3 -c "import venv" 2>/dev/null; then
    echo "Error: python3-venv is not installed. Please install it (e.g., sudo apt install python3-venv)."
    exit 1
fi

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt
pip install pyinstaller

echo "Building executable..."
pyinstaller --clean agent-sync.spec

echo "Build complete. Executable is in dist/agent-sync"
