#!/bin/bash
# Quick launcher for the Model Training TUI

# Check if dependencies are installed
if ! python -c "import textual" 2>/dev/null; then
    echo "Installing TUI dependencies..."
    pip install textual rich click
fi

# Launch the TUI
echo "Launching Model Training TUI..."
python -m cli.main tui "$@"
