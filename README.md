# 🎵 Mini Player — PyQt6 Music Player

**Mini Player** is a sleek and modern desktop music player built with PyQt6. It provides a lightweight, intuitive interface for playing MP3 files with smart features like playback speed control, volume adjustment, and smooth track title scrolling — all wrapped in a stylish UI.

---

## ✨ Features

- 🎧 **Play MP3 files** from folders or single files
- 📂 File browser with list display of tracks
- ▶️ Pause, resume, stop with responsive controls
- 🔁 Repeat track toggle
- 🔇 Mute/unmute with volume memory
- 🎚 Adjustable **playback speed** (0.5x–1.5x)
- 📈 Smooth **progress bar seeking**
- ⏳ Real-time time labels (`00:00 / 03:45`)
- 📀 "Now Playing" banner with **scrolling marquee** for long titles
- 💾 Automatic save/load of last session (volume, speed, track, etc.)
- 🎨 Stylish modern UI with custom icons and dark theme

---
![Screenshot from 2025-04-24 19-28-53](https://github.com/user-attachments/assets/2b1ffb56-276a-4a36-a822-57582ab9989a)
---

## 🛠️ Requirements

- Python 3.12+
- PyQt6
- MP3, FLAC, wav, ogg files

---

## 🚀 Getting Started

```bash
git clone https://github.com/Mohabdo21/mini-player.git
cd mini-player
pip install -r requirements.txt
python -m src.app
```

## Building Executable

To create an executable for the application, you can use `PyInstaller`. First, ensure you have it installed:

```bash
pyinstaller app.spec
```

This will generate a `dist` folder containing the executable. You can run the application directly from there.

```bash
./dist/MiniPlayer
```

> Your settings (volume, speed, last folder, etc.) are saved automatically to `mini_player.ini`.

---

## 📁 Project Structure

```
mini-player/src
├── app.py                # Main application
├── icons/                # Icon assets (SVG/PNG)
│   └── play.png ...
├── default_album.png     # Placeholder album art
└── mini_player.ini       # Auto-generated config file
```

---

## ⚙️ Configuration

Settings are stored in `mini_player.ini` and include:

- Last opened folder and track
- Volume level
- Playback speed
- Repeat/mute toggle states

---

## 💡 Future Enhancements

- Playlist support
- Drag-and-drop track queue
- Album art fetching from metadata or online
- Visualizer or waveform view

---

## 🪪 License

MIT License — free to use, modify, and distribute.
