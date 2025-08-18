#!/bin/bash

# OpCore Simplify for Linux
# This script runs the OpCore Simplify tool on Linux systems

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 to run OpCore Simplify."
    exit 1
fi

# Check if running with sudo for full hardware detection
if [ "$EUID" -ne 0 ]; then 
    echo "Note: Running without sudo. Some hardware information may be limited."
    echo "For complete hardware detection (ACPI tables, memory details), run with: sudo $0"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit..."
fi

# Run the main Python script
python3 OpCore-Simplify.py

# Exit with the same code as the Python script
exit $?