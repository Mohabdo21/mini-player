#!/bin/bash
# Transition script from the old flat structure to the new modular structure

echo "🎵 MiniPlayer Migration Helper 🎵"
echo "=================================="
echo "This script will help you transition from the old structure to the new modular structure."
echo ""

# Check if the src/app.py file exists (old structure)
if [ ! -f src/app.py ]; then
    echo "❌ The old structure (src/app.py) was not found."
    echo "You may already be using the new structure or have a different setup."
    exit 1
fi

echo "✅ Found old structure. Beginning migration..."

# Create a backup of the entire project
echo "📁 Creating backup..."
timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="../mini_player_backup_${timestamp}"
cp -r . "${backup_dir}"
echo "✅ Backup created at: ${backup_dir}"

# Migrate settings if needed
echo "⚙️ Migrating settings..."
python3 migrate_settings.py

# Run the app from the new structure
echo ""
echo "🚀 Ready to run the new modular version!"
echo ""
echo "To run the app, use one of these commands:"
echo "  python3 main.py"
echo "  or"
echo "  ./main.py"
echo ""
echo "If you run into any issues, you can restore your backup from: ${backup_dir}"
echo ""
echo "Enjoy your new modular MiniPlayer! 🎵"
