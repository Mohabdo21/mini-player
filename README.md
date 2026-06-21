# 🎵 Mini Player - PyQt6 Music Player

**Mini Player** is a sleek and modern desktop music player built with PyQt6. It provides a lightweight, intuitive interface for playing audio files with smart features like playback speed control, volume adjustment, and smooth track title scrolling - all wrapped in a stylish UI.

## [![Build and Release Mini Player](https://github.com/Mohabdo21/mini-player/actions/workflows/release.yml/badge.svg)](https://github.com/Mohabdo21/mini-player/actions/workflows/release.yml)

## ✨ Features

- 🎧 **Play MP3, FLAC, WAV, OGG files** from folders or single files
- 📂 File browser with list display of tracks
- ▶️ Pause, resume, stop with responsive controls
- 🎚 Adjustable **playback speed** (0.5x-1.5x)
- 📈 Smooth **progress bar seeking**
- ⏳ Real-time time labels (`00:00 / 03:45`)
- 🔁 Repeat track toggle
- 🔇 Mute/unmute with volume memory
- 📀 "Now Playing" banner with **scrolling marquee** for long titles
- 💾 Automatic save/load of last session (volume, speed, track, etc.)
- 🎨 Stylish modern UI with custom icons and dark theme

![MiniPlayer Screenshot](https://github.com/user-attachments/assets/2b1ffb56-276a-4a36-a822-57582ab9989a)

---

## 🛠️ Requirements

- Python 3.8+
- PyQt6
- Mutagen (for metadata handling)

---

## 🚀 Getting Started

### Installation

```bash
git clone https://github.com/Mohabdo21/mini-player.git
cd mini-player
pip install -r requirements.txt
```

### Run the Application

```bash
python main.py
```

Alternatively, after installation:

```bash
mini-player
```

### Building Executable

To create a standalone executable:

```bash
pyinstaller app.spec
```

This will generate a `dist` folder containing the executable. You can run it directly:

```bash
./dist/MiniPlayer
```

> Your settings (volume, speed, last folder, etc.) are saved automatically to `mini_player.ini`.

---

## 📁 Project Structure

The project follows a modular design pattern for better maintainability:

```
mini-player/
├── main.py                # Entry point script
├── app.spec               # PyInstaller specification
├── LICENSE                # License file
├── pyproject.toml         # Project configuration
├── README.md              # Project documentation
├── requirements.txt       # Dependencies
├── setup.py               # Setup script
└── src/                   # Source code
    ├── __init__.py        # Package initialization
    ├── icons/             # Icon assets
    ├── default_album.png  # Default album art
    └── miniplayer/        # Main package
        ├── __init__.py    # Version info
        ├── app.py         # Application entry point
        ├── core/          # Core functionality
        │   ├── __init__.py
        │   ├── audio_player.py      # Audio playback engine
        │   ├── config_manager.py    # Settings management
        │   └── track_manager.py     # Track list management
        ├── ui/            # User interface components
        │   ├── __init__.py
        │   ├── main_window.py       # Main application window
        │   └── playlist_widget.py   # Custom playlist widget
        └── utils/         # Utilities and helpers
            ├── __init__.py
            └── helpers.py           # Helper functions
```

### Module Overview

- **core**: Contains the business logic and data handling

  - `audio_player.py`: Core audio playback functionality
  - `config_manager.py`: Settings management
  - `track_manager.py`: Track list and file system operations

- **ui**: User interface components

  - `main_window.py`: Main application window
  - `playlist_widget.py`: Custom playlist widget

- **utils**: Utility functions
  - `helpers.py`: Common helper functions

---

## ⚙️ Configuration

Settings are stored in `mini_player.ini` and include:

- Last opened folder and track
- Volume level
- Playback speed
- Repeat/mute toggle states

---

## 💡 Future Enhancements

- Playlist management (save/load playlists)
- Drag-and-drop track queue
- Advanced album art fetching from metadata or online sources
- Audio visualizer or waveform view
- Mobile version using QtQuick/QML

---

## 🪪 License

MIT License - free to use, modify, and distribute.
