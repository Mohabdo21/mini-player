#!/bin/bash
# Quick fix script for MiniPlayer module error

echo "🎵 MiniPlayer Import Error Fix 🎵"
echo "================================"
echo "This script will fix the 'ModuleNotFoundError: No module named 'miniplayer'' error."
echo

# Check if the current directory is the audio_speed directory
if [ "$(basename $(pwd))" != "audio_speed" ]; then
    echo "❌ Please run this script from the audio_speed directory."
    exit 1
fi

echo "📋 The script will try the following solutions:"
echo "  1. Install the package in development mode"
echo "  2. Create a PYTHONPATH-enabled run script"
echo "  3. Update the main.py import path"
echo

echo "🔧 Installing in development mode..."
pip install -e .

echo
echo "🔧 Creating a PYTHONPATH-enabled run script..."
cat > run.sh << 'EOF'
#!/bin/bash
# Run MiniPlayer with the correct PYTHONPATH

# Add the current directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the app
python main.py
EOF
chmod +x run.sh

echo
echo "🔧 Ensuring main.py has the correct import path..."
if ! grep -q "sys.path.insert" main.py; then
    # Backup the original file
    cp main.py main.py.bak

    # Add the path fix to main.py
    sed -i '1,/^import/ {/^import/ i\
import os\
import sys\
\
# Add src directory to Python path\
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")\
sys.path.insert(0, src_dir)\
' main.py
fi

echo
echo "✅ All fixes applied!"
echo
echo "🚀 You can now run MiniPlayer using one of these commands:"
echo "  1. ./run.sh (recommended)"
echo "  2. ./main.py"
echo "  3. python -m miniplayer.app"
echo
echo "If you still encounter issues, please check TROUBLESHOOTING.md"
