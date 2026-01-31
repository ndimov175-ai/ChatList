#!/bin/bash
# ChatList launcher script
# Activates virtual environment and runs the application
# Automatically detects and handles display availability

cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Configure Qt platform based on environment
if [ -z "$DISPLAY" ]; then
    # No display - use offscreen rendering
    export QT_QPA_PLATFORM=offscreen
else
    # Display is available, but xcb might not have all dependencies
    # Use minimal platform as a fallback for missing xcb libraries
    if ! pkg-config --exists xcb-cursor 2>/dev/null; then
        export QT_QPA_PLATFORM=minimal
    fi
fi

# Run the application
python3 run.py
