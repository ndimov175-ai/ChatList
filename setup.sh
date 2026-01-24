#!/bin/bash
# Setup script for ChatList

echo "ChatList Setup Script"
echo "===================="
echo ""

# Check if python3-venv is needed
if ! python3 -m venv --help > /dev/null 2>&1; then
    echo "❌ python3-venv is not installed."
    echo ""
    echo "Please install it with:"
    echo "  sudo apt install python3.11-venv"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Remove old venv if it exists
if [ -d "venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf venv
fi

# Create new venv
echo "Creating virtual environment..."
python3 -m venv venv

# Activate and upgrade pip
echo "Upgrading pip..."
venv/bin/pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
venv/bin/pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "  source venv/bin/activate"
echo "  python run.py"
echo ""
echo "Or use the venv Python directly:"
echo "  venv/bin/python run.py"

