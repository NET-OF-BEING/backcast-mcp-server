#!/bin/bash
# Launcher script for Outcome Backcasting Engine

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  Outcome Backcasting Engine"
echo "  Reverse-engineer your path to success"
echo "=========================================="
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Using Python $PYTHON_VERSION"

# Ensure data directory exists
mkdir -p "$SCRIPT_DIR/data"

# Run the CLI
echo ""
python3 "$SCRIPT_DIR/backcast_cli.py"

exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo ""
    echo "ERROR: Application exited with code $exit_code"
    echo "Check the error messages above for details."
    exit $exit_code
fi

exit 0
