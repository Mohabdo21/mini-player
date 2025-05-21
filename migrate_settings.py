#!/usr/bin/env python3
"""
Migration script for MiniPlayer settings.

This script helps migrate settings from the old flat structure to the new modular structure.
"""

import configparser
import os
import shutil
import sys
from pathlib import Path


def migrate_settings():
    """Migrate settings from old format to new format."""
    old_config = "mini_player.ini"

    # Check if old config exists
    if not os.path.exists(old_config):
        print(
            f"No existing config file found at {old_config}. No migration needed."
        )
        return

    print("Found existing settings. Migrating to new format...")

    # Create backup
    backup_path = f"{old_config}.bak"
    shutil.copy2(old_config, backup_path)
    print(f"Created backup at {backup_path}")

    # The config format is the same, so we don't need to change anything
    # Just inform the user
    print("Migration complete! Your existing settings have been preserved.")
    print(
        f"If you encounter any issues, you can restore the backup from {backup_path}"
    )


if __name__ == "__main__":
    migrate_settings()
