# Troubleshooting MiniPlayer Installation

If you encounter issues running the MiniPlayer application, here are some common problems and their solutions:

## ModuleNotFoundError: No module named 'miniplayer'

This error occurs when Python cannot find the miniplayer package. There are several ways to fix this:

### Solution 1: Install in Development Mode

Run the development installation script:

```bash
./dev_install.sh
```

Or manually install in development mode:

```bash
pip install -e .
```

### Solution 2: Update PYTHONPATH

If you prefer not to install the package, you can temporarily modify your PYTHONPATH:

```bash
# Bash/Zsh
export PYTHONPATH=$PYTHONPATH:$(pwd)
# or
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Then run the app
./main.py
```

### Solution 3: Run from the src directory

```bash
cd src
python -m miniplayer.app
```

## ImportError: Cannot import name 'X' from 'miniplayer.Y'

This usually means there's a circular import or a missing dependency. Check that:

1. You're not creating circular imports between modules
2. All required packages are installed with `pip install -r requirements.txt`

## PyQt6-related errors

Ensure you have the PyQt6 package and all its dependencies installed:

```bash
pip install PyQt6 PyQt6-Qt6 PyQt6-sip
```

On some Linux systems, you might also need to install additional packages:

```bash
sudo apt-get install python3-pyqt6 python3-pyqt6.qtmultimedia
```

## QMediaPlayer-related errors

If you encounter issues with the audio playback:

```bash
sudo apt-get install gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly
```

## Other Issues

If none of the above solutions work, please create an issue on the GitHub repository with details about your system and the exact error message.
