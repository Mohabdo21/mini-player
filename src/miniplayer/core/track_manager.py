"""
File management and track list functionality for MiniPlayer.

This module handles file system operations, track lists, and file filtering.
"""

import os
from pathlib import Path
from typing import Callable, List, Optional, Set, Tuple

from PyQt6.QtCore import QObject, pyqtSignal


class TrackManager(QObject):
    """Manages track lists and file operations."""

    # Define signals
    trackListUpdated = pyqtSignal(list)  # Emitted when track list changes
    trackDiscoveryProgress = pyqtSignal(int, int)  # (current, total) progress

    def __init__(self, supported_extensions: Tuple[str, ...] = None):
        """
        Initialize the track manager.

        Args:
            supported_extensions: Tuple of supported file extensions
        """
        super().__init__()
        self.supported_extensions = supported_extensions or (
            ".mp3",
            ".flac",
            ".wav",
            ".ogg",
        )
        self.current_folder = None
        self.track_list = []

    def set_folder(self, folder_path: str) -> bool:
        """
        Set the current folder and scan for tracks.

        Args:
            folder_path: Path to the music folder

        Returns:
            True if folder was set successfully, False otherwise
        """
        path = Path(folder_path)
        if not path.exists() or not path.is_dir():
            return False

        self.current_folder = str(path)
        self.scan_folder()
        return True

    def scan_folder(
        self, callback: Optional[Callable[[int, int], None]] = None
    ) -> List[str]:
        """
        Scan the current folder for supported audio files.

        Args:
            callback: Optional progress callback function

        Returns:
            List of relative paths to audio files
        """
        if not self.current_folder:
            return []

        result = []
        folder_path = Path(self.current_folder)

        # First count files for progress reporting
        total_files = 0
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(self.supported_extensions):
                    total_files += 1

        # Then scan for matching files
        found_files = 0
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(self.supported_extensions):
                    rel_path = os.path.relpath(
                        os.path.join(root, file), folder_path
                    )
                    result.append(rel_path)
                    found_files += 1

                    # Update progress
                    if callback:
                        callback(found_files, total_files)
                    self.trackDiscoveryProgress.emit(found_files, total_files)

        self.track_list = result
        self.trackListUpdated.emit(self.track_list)
        return result

    def filter_tracks(self, search_text: str) -> List[Tuple[str, bool]]:
        """
        Filter tracks based on search text.

        Args:
            search_text: Text to search for in track names

        Returns:
            List of tuples containing (track_path, visible)
        """
        if not search_text:
            return [(track, True) for track in self.track_list]

        search_lower = search_text.lower()
        return [
            (track, search_lower in track.lower()) for track in self.track_list
        ]

    def get_absolute_path(self, relative_path: str) -> Path:
        """
        Convert a relative path to an absolute path.

        Args:
            relative_path: Relative path from the current folder

        Returns:
            Absolute path to the file
        """
        if not self.current_folder:
            return None

        return Path(self.current_folder) / relative_path

    def get_current_folder(self) -> Optional[str]:
        """Get the current folder path."""
        return self.current_folder

    def get_track_list(self) -> List[str]:
        """Get the current list of tracks."""
        return self.track_list
