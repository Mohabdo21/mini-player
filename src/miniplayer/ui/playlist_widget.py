"""
Playlist widget for MiniPlayer.

This module contains the playlist view component.
"""

from PyQt6.QtWidgets import QListWidget


class PlaylistWidget(QListWidget):
    """Custom list widget for audio track playlist."""

    def __init__(self, parent=None):
        """Initialize the playlist widget."""
        super().__init__(parent)
        self.setAlternatingRowColors(True)
