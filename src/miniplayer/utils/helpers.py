"""
Utility functions for MiniPlayer.

This module contains helper functions used throughout the application.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from PyQt6.QtCore import QTime
from PyQt6.QtGui import QPixmap


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to MM:SS format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted time string (MM:SS)
    """
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"


def format_position_duration(position_ms: int, duration_ms: int) -> str:
    """
    Format position and duration as MM:SS / MM:SS.

    Args:
        position_ms: Current position in milliseconds
        duration_ms: Total duration in milliseconds

    Returns:
        Formatted time string (MM:SS / MM:SS)
    """
    current_time = QTime(0, 0).addMSecs(position_ms)
    total_time = QTime(0, 0).addMSecs(duration_ms)

    return f"{current_time.toString('mm:ss')} / {total_time.toString('mm:ss')}"


def format_metadata_display(metadata: Dict[str, Any]) -> str:
    """
    Format metadata for display in the UI.

    Args:
        metadata: Dictionary containing track metadata

    Returns:
        HTML-formatted string for display
    """
    if not metadata:
        return "No metadata available"

    display = []

    # Basic info
    if "title" in metadata:
        display.append(f"<b>Title:</b> {metadata['title']}")
    if "artist" in metadata:
        display.append(f"<b>Artist:</b> {metadata['artist']}")
    if "album" in metadata:
        display.append(f"<b>Album:</b> {metadata['album']}")

    # Track info
    if "tracknumber" in metadata:
        track_num = metadata["tracknumber"].split("/")[
            0
        ]  # Handle "1/10" format
        display.append(f"<b>Track:</b> {track_num}")

    # Technical info
    if "duration" in metadata:
        display.append(
            f"<b>Duration:</b> {format_duration(metadata['duration'])}"
        )
    if "bitrate" in metadata:
        display.append(f"<b>Bitrate:</b> {metadata['bitrate']} kbps")
    if "sample_rate" in metadata:
        display.append(f"<b>Sample Rate:</b> {metadata['sample_rate']} Hz")

    # Additional metadata
    if "date" in metadata:
        display.append(f"<b>Year:</b> {metadata['date']}")
    if "genre" in metadata:
        display.append(f"<b>Genre:</b> {metadata['genre']}")
    if "composer" in metadata:
        display.append(f"<b>Composer:</b> {metadata['composer']}")

    return "<br>".join(display)


def get_icon_path(icon_name: str) -> Optional[str]:
    """
    Find the path to an icon file.

    Args:
        icon_name: Name of the icon file

    Returns:
        Absolute path to the icon, or None if not found
    """
    paths = [
        # System install locations
        f"/usr/share/icons/hicolor/scalable/apps/{icon_name}",
        f"/usr/share/icons/hicolor/48x48/apps/{icon_name}",
        # Local development
        os.path.join(
            os.path.dirname(__file__), "..", "..", "icons", f"{icon_name}"
        ),
        os.path.join(os.path.dirname(__file__), "..", "..", f"{icon_name}"),
        # Flatpak/Snap locations
        f"/usr/share/{icon_name}",
    ]

    for path in paths:
        if os.path.exists(path):
            return path

    return None


def extract_album_art(file_path: Path) -> Optional[QPixmap]:
    """
    Extract album art from an audio file.

    Args:
        file_path: Path to the audio file

    Returns:
        QPixmap with album art, or None if extraction fails
    """
    try:
        from mutagen import File

        audio = File(file_path)

        # No audio file found
        if audio is None:
            return None

        # Check for embedded art
        if hasattr(audio, "pictures") and audio.pictures:
            picture = audio.pictures[0]
            pixmap = QPixmap()
            pixmap.loadFromData(picture.data)
            if not pixmap.isNull():
                return pixmap

        # For MP3 files with ID3 tags
        if (
            file_path.suffix.lower() == ".mp3"
            and hasattr(audio, "tags")
            and "APIC:" in audio.tags
        ):
            picture = audio.tags["APIC:"].data
            pixmap = QPixmap()
            pixmap.loadFromData(picture)
            if not pixmap.isNull():
                return pixmap

    except Exception as e:
        print(f"Error extracting album art: {e}")

    return None
