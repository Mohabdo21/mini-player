#!/bin/bash
# Development install script for MiniPlayer

echo "🎵 MiniPlayer Development Setup 🎵"
echo "=================================="

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip could not be found. Please make sure Python and pip are installed."
    exit 1
fi

# Check for virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "ℹ️ No active virtual environment detected."
    echo "  It is recommended to use a virtual environment."
    echo "  You can create one with: python -m venv .venv"
    echo "  And activate it with: source .venv/bin/activate"

    read -p "Continue with installation outside of a virtual environment? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation canceled."
        exit 1
    fi
fi

echo "📦 Installing MiniPlayer in development mode..."
pip install -e .

if [ $? -eq 0 ]; then
    echo "✅ Installation successful!"
    echo
    echo "📝 You can now run MiniPlayer using either:"
    echo "  ./main.py"
    echo "  python main.py"
    echo "  mini-player (if installation added to PATH)"
    echo
    echo "🎉 Happy development!"
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi
