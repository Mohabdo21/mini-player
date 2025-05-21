#!/usr/bin/env python3
"""
MiniPlayer - PyQt6 Music Player with Speed Control

Main entry point for running the MiniPlayer application.
"""

import os
import sys

# Add src directory to Python path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

from miniplayer.app import main

if __name__ == "__main__":
    main()
