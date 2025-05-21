"""
Core audio playback functionality for MiniPlayer.

This module contains the main audio playback logic, independent of UI components.
"""

from pathlib import Path
from typing import Any, Callable, Dict, Optional

from mutagen import File
from PyQt6.QtCore import QObject, Qt, QTimer, QUrl, pyqtSignal
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer


class AudioPlayer(QObject):
    """Core audio player class that handles media playback functionality."""

    # Define signals for communication with UI
    positionChanged = pyqtSignal(int)
    durationChanged = pyqtSignal(int)
    playbackStateChanged = pyqtSignal(QMediaPlayer.PlaybackState)
    mediaStatusChanged = pyqtSignal(QMediaPlayer.MediaStatus)
    metadataChanged = pyqtSignal(dict)

    def __init__(self) -> None:
        """Initialize the audio player with default settings."""
        super().__init__()

        # Set up audio components
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.5)  # Default volume: 50%

        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)

        # Set up timer for progress updates
        self.timer = QTimer()
        self.timer.setInterval(10)  # 10ms update interval
        self.timer.timeout.connect(self._update_position)

        # Connect signals
        self.media_player.playbackStateChanged.connect(
            self._handle_playback_state_changed
        )
        self.media_player.mediaStatusChanged.connect(
            self._handle_media_status_changed
        )

        # Track info
        self.current_track_url = None
        self.current_track_path = None
        self.current_metadata = {}

        # Fade out settings
        self.fade_timer = QTimer()
        self.fade_duration = 500  # milliseconds for fade out
        self.fade_steps = 10  # number of steps for fade
        self.fade_interval = self.fade_duration // self.fade_steps
        self.original_volume = 1.0
        self.fade_timer.timeout.connect(self._fade_step)

    def load_track(self, file_path: Path) -> None:
        """
        Load a track from a file path.

        Args:
            file_path: Path to the audio file
        """
        if not file_path.exists():
            return

        # Set up new track
        file_url = QUrl.fromLocalFile(str(file_path))
        self.current_track_url = file_url
        self.current_track_path = file_path
        self.media_player.setSource(file_url)

        # Get metadata
        self.current_metadata = self.get_audio_metadata(file_path)
        self.metadataChanged.emit(self.current_metadata)

    def play(self) -> None:
        """Start or resume audio playback."""
        self.media_player.play()
        self.timer.start()

    def pause(self) -> None:
        """Pause audio playback."""
        self.media_player.pause()
        self.timer.stop()

    def stop(self) -> None:
        """Stop audio playback."""
        self.media_player.stop()
        self.timer.stop()

    def seek(self, position: int) -> None:
        """
        Seek to a position in the current track.

        Args:
            position: Position in milliseconds
        """
        self.media_player.setPosition(position)

    def set_volume(self, volume: float) -> None:
        """
        Set the volume level.

        Args:
            volume: Volume level from 0.0 to 1.0
        """
        self.audio_output.setVolume(volume)

    def set_playback_rate(self, rate: float) -> None:
        """
        Set the playback speed.

        Args:
            rate: Playback rate (1.0 is normal speed)
        """
        self.media_player.setPlaybackRate(rate)

    def get_position(self) -> int:
        """Get the current playback position in milliseconds."""
        return self.media_player.position()

    def get_duration(self) -> int:
        """Get the total duration of the current track in milliseconds."""
        return self.media_player.duration()

    def get_playback_state(self) -> QMediaPlayer.PlaybackState:
        """Get the current playback state."""
        return self.media_player.playbackState()

    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return (
            self.media_player.playbackState()
            == QMediaPlayer.PlaybackState.PlayingState
        )

    def is_paused(self) -> bool:
        """Check if audio is currently paused."""
        return (
            self.media_player.playbackState()
            == QMediaPlayer.PlaybackState.PausedState
        )

    def is_stopped(self) -> bool:
        """Check if audio is currently stopped."""
        return (
            self.media_player.playbackState()
            == QMediaPlayer.PlaybackState.StoppedState
        )

    def fade_out(self) -> None:
        """Start the fade out process."""
        if self.is_stopped():
            return

        # Store current volume
        self.original_volume = self.audio_output.volume()

        # Start fade timer
        self.fade_timer.start(self.fade_interval)

    def get_audio_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata using mutagen.

        Args:
            file_path: Path to the audio file

        Returns:
            Dictionary containing audio metadata
        """
        try:
            audio = File(file_path)
            if audio is None:
                return {}

            metadata = {}
            common_tags = [
                "title",
                "artist",
                "album",
                "date",
                "tracknumber",
                "genre",
                "composer",
                "copyright",
                "isrc",
            ]

            # Get standard tags
            for tag in common_tags:
                if hasattr(audio, "tags") and audio.tags and tag in audio.tags:
                    metadata[tag] = str(audio.tags[tag][0])

            # Get duration
            metadata["duration"] = audio.info.length

            # Get technical info
            if hasattr(audio.info, "bitrate"):
                metadata["bitrate"] = audio.info.bitrate // 1000
            if hasattr(audio.info, "sample_rate"):
                metadata["sample_rate"] = audio.info.sample_rate
            if hasattr(audio.info, "channels"):
                metadata["channels"] = audio.info.channels

            # Handle specific file types
            if file_path.suffix.lower() == ".flac":
                if "tracknumber" not in metadata and "track" in audio.tags:
                    metadata["tracknumber"] = str(audio.tags["track"][0])

            return metadata

        except Exception as e:
            print(f"Error reading metadata: {e}")
            return {}

    def _update_position(self) -> None:
        """Update position and emit signal."""
        if not self.is_stopped():
            self.positionChanged.emit(self.media_player.position())

    def _handle_playback_state_changed(self, state) -> None:
        """Forward playback state changes."""
        self.playbackStateChanged.emit(state)

    def _handle_media_status_changed(self, status) -> None:
        """Forward media status changes."""
        self.mediaStatusChanged.emit(status)

    def _fade_step(self) -> None:
        """Reduce volume by one step during fade out."""
        current_volume = self.audio_output.volume()
        step_size = self.original_volume / self.fade_steps

        if current_volume > step_size:
            # Reduce volume
            new_volume = max(0, current_volume - step_size)
            self.audio_output.setVolume(new_volume)
        else:
            # Fade complete - stop everything
            self.fade_timer.stop()
            self.audio_output.setVolume(0)
            self.media_player.stop()
            self.audio_output.setVolume(
                self.original_volume
            )  # Restore original volume
