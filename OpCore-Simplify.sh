#!/usr/bin/env bash

# ###################################################################
# # OpCore-Simplify Linux Launcher
# ###################################################################
# # This script handles the necessary environment setup to run the
# # OpCore-Simplify.py application on a Linux system.
# #
# # It performs the following checks:
# # 1. Root Privileges: Verifies if the script is run with sudo,
# #    which is required for dumping ACPI tables from /sys.
# # 2. Python 3: Ensures that the python3 interpreter is installed
# #    and available in the system's PATH.
# # 3. Script Location: Finds its own directory to correctly locate
# #    and execute the main Python script.
# ###################################################################

# --- Get the script's absolute directory ---
# This ensures that it runs correctly regardless of where it's called from.
dir="$(cd -- "$(dirname "$0")" >/dev/null 2>&1; pwd -P)"
target="OpCore-Simplify.py"

# --- Verify that the main Python script exists ---
if [ ! -f "$dir/$target" ]; then
    echo "Error: The main script '$target' was not found in the directory '$dir'." >&2
    echo "Please ensure you are running this launcher from the correct project folder." >&2
    exit 1
fi

# --- Check for Python 3 Interpreter ---
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not found in your system's PATH." >&2
    echo "Please install it using your distribution's package manager." >&2
    echo "  For Debian/Ubuntu: sudo apt update && sudo apt install python3" >&2
    echo "  For Fedora:        sudo dnf install python3" >&2
    echo "  For Arch Linux:    sudo pacman -S python" >&2
    exit 1
fi

# --- All checks passed, launch the application ---
echo "Launching OpCore-Simplify..."
echo "-----------------------------------"

# Execute the Python script, passing along any arguments
python3 "$dir/$target" "$@"

# Exit with the status code of the Python script
exit $?