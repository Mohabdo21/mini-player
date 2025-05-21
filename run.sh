#!/bin/bash
# Quick run script for MiniPlayer that sets PYTHONPATH

# Add the current directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the app
python main.py
