"""
Core functionality for MiniPlayer.

This package contains the core business logic for the MiniPlayer application.
"""

from .audio_player import AudioPlayer
from .config_manager import ConfigManager
from .track_manager import TrackManager

__all__ = ["AudioPlayer", "TrackManager", "ConfigManager"]
