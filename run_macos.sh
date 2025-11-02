#!/bin/bash

# Virtual Keyboard Launcher for macOS
# This script launches the virtual keyboard application on macOS

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

# Check if pynput is installed
if ! python3 -c "import pynput" &> /dev/null; then
    echo "Installing required dependency: pynput"
    python3 -m pip install pynput
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install pynput"
        echo "Please run: pip3 install pynput"
        exit 1
    fi
fi

# Run the application
echo "Starting Virtual Keyboard..."
python3 main.py

# Keep terminal open if there's an error
if [ $? -ne 0 ]; then
    echo ""
    echo "Press any key to exit..."
    read -n 1
fi
