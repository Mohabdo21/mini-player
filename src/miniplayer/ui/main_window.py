"""
Main window for the MiniPlayer application.

This module contains the main application window and UI setup.
"""

import os
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QFontMetrics, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QProgressDialog,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from miniplayer.core import AudioPlayer, ConfigManager, TrackManager
from miniplayer.utils import (
    extract_album_art,
    format_metadata_display,
    format_position_duration,
    get_icon_path,
)

from .playlist_widget import PlaylistWidget


class MainWindow(QWidget):
    """Main application window for MiniPlayer."""

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()

        # Initialize core components
        self.audio_player = AudioPlayer()
        self.track_manager = TrackManager()
        self.config_manager = ConfigManager()

        # UI state
        self.user_stopped = False
        self.ignore_auto_advance = False

        # Set up window properties
        self.setWindowTitle("Mini Player")
        self.setGeometry(800, 500, 800, 400)
        self.setWindowIcon(QIcon(get_icon_path("mini-player.svg")))

        # Setup UI components
        self.setup_ui()

        # Connect signals
        self.connect_signals()

        # Apply styling
        self.apply_styling()

        # Load saved settings
        self.load_settings()

        # Initialize UI state
        self.playlist.setFocus()

        # Set up title scrolling
        self.track_title = ""
        self.track_scroll_index = 0
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.scroll_track_title)
        self.scroll_timer.setInterval(150)

    def setup_ui(self) -> None:
        """Set up UI components."""
        # Main layout
        main_layout = QHBoxLayout()

        # Left side: Playlist and search
        left_side = self.create_playlist_section()

        # Right side: Controls and now playing
        right_side = self.create_playback_section()

        # Add layouts to main layout
        main_layout.addLayout(left_side, 3)
        main_layout.addLayout(right_side, 5)
        main_layout.setContentsMargins(20, 15, 20, 15)

        self.setLayout(main_layout)
        self.main_layout = main_layout

    def create_playlist_section(self) -> QVBoxLayout:
        """Create the playlist section with search bar."""
        layout = QVBoxLayout()

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search tracks...")
        self.search_bar.setClearButtonEnabled(True)
        layout.addWidget(self.search_bar)

        # Playlist
        self.playlist = PlaylistWidget()
        layout.addWidget(self.playlist)

        layout.setSpacing(6)
        return layout

    def create_playback_section(self) -> QVBoxLayout:
        """Create the playback controls and now playing section."""
        layout = QVBoxLayout()

        # Now Playing section with album art
        now_playing = QHBoxLayout()

        # Album art
        self.album_art = QLabel()
        self.album_art.setObjectName("album_art")
        self.album_art.setFixedSize(80, 80)
        self.album_art.setStyleSheet(
            "background-color: #444; border-radius: 8px;"
        )
        self.album_art.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.album_art.setPixmap(
            QPixmap(get_icon_path("default_album.png")).scaled(
                80, 80, Qt.AspectRatioMode.KeepAspectRatio
            )
        )

        # Track info
        track_info = QVBoxLayout()
        self.track_label = QLabel("Now Playing: ")
        self.track_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.track_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #5BB9C2;"
        )
        self.track_label.setMinimumWidth(200)
        self.track_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.track_label.setMaximumHeight(40)

        track_info.addWidget(self.track_label)

        now_playing.addWidget(self.album_art)
        now_playing.addLayout(track_info)
        now_playing.setSpacing(10)

        # Metadata display
        self.metadata_label = QLabel()
        self.metadata_label.setWordWrap(True)
        self.metadata_label.setStyleSheet(
            "font-size: 12px; color: #B0B0B0; margin-top: 2px;"
        )
        self.metadata_label.setTextFormat(Qt.TextFormat.RichText)

        # Progress section
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setMouseTracking(True)
        self.progress_bar.setFixedHeight(8)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setObjectName("timeLabel")

        # Status controls (repeat, mute, play all)
        status_controls = QHBoxLayout()

        self.btn_repeat = QCheckBox()
        self.btn_repeat.setIcon(QIcon(get_icon_path("repeat.svg")))
        self.btn_repeat.setToolTip("Repeat Track")

        self.btn_mute = QCheckBox()
        self.btn_mute.setIcon(QIcon(get_icon_path("mute.svg")))
        self.btn_mute.setToolTip("Mute Audio")

        self.btn_play_all = QCheckBox()
        self.btn_play_all.setIcon(QIcon(get_icon_path("play-all.png")))
        self.btn_play_all.setToolTip("Play All Tracks")

        status_controls.addWidget(self.btn_repeat)
        status_controls.addWidget(self.btn_mute)
        status_controls.addWidget(self.btn_play_all)
        status_controls.addStretch()
        status_controls.addWidget(self.time_label)

        # Playback controls
        playback_controls = QHBoxLayout()

        self.btn_opener = QPushButton()
        self.btn_opener.setIcon(QIcon(get_icon_path("folder.png")))
        self.btn_opener.setToolTip("Open Folder")

        self.btn_prev = QPushButton()
        self.btn_prev.setIcon(QIcon(get_icon_path("prev.png")))
        self.btn_prev.setToolTip("Previous Track")
        self.btn_prev.setDisabled(True)

        self.btn_play_pause = QPushButton()
        self.btn_play_pause.setIcon(QIcon(get_icon_path("play.png")))
        self.btn_play_pause.setToolTip("Play / Pause")

        self.btn_next = QPushButton()
        self.btn_next.setIcon(QIcon(get_icon_path("next.png")))
        self.btn_next.setToolTip("Next Track")
        self.btn_next.setDisabled(True)

        self.btn_reset = QPushButton()
        self.btn_reset.setIcon(QIcon(get_icon_path("reset.png")))
        self.btn_reset.setToolTip("Stop")
        self.btn_reset.setDisabled(True)

        playback_controls.addWidget(self.btn_opener)
        playback_controls.addWidget(self.btn_prev)
        playback_controls.addWidget(self.btn_play_pause)
        playback_controls.addWidget(self.btn_next)
        playback_controls.addWidget(self.btn_reset)
        playback_controls.setSpacing(10)

        # Sliders (speed and volume)
        slider_section = QVBoxLayout()

        # Speed slider
        speed_layout = QHBoxLayout()
        self.slider_text = QLabel("Speed: 1.00x")
        self.slider_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_text.setObjectName("speedLabel")

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(50)
        self.speed_slider.setMaximum(150)
        self.speed_slider.setValue(100)

        speed_layout.addWidget(self.slider_text)
        speed_layout.addWidget(self.speed_slider)

        # Volume slider
        volume_layout = QHBoxLayout()
        self.volume_label = QLabel("Volume: 50%")
        self.volume_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.volume_label.setObjectName("volumeLabel")

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)

        volume_layout.addWidget(self.volume_label)
        volume_layout.addWidget(self.volume_slider)

        slider_section.addLayout(speed_layout)
        slider_section.addLayout(volume_layout)

        # Add all sections to main layout
        now_playing_container = QVBoxLayout()
        now_playing_container.addLayout(now_playing)
        now_playing_container.addWidget(self.metadata_label)
        now_playing_container.setSpacing(4)

        layout.addLayout(now_playing_container)
        layout.addWidget(self.progress_bar)
        layout.addLayout(status_controls)
        layout.addLayout(playback_controls)
        layout.addLayout(slider_section)
        layout.setSpacing(8)

        return layout

    def connect_signals(self) -> None:
        """Connect UI signals and slots."""
        # Search and playlist
        self.search_bar.textChanged.connect(self.filter_tracks)
        self.playlist.itemSelectionChanged.connect(
            self.handle_track_selection_changed
        )
        self.playlist.itemDoubleClicked.connect(self.play_selected_track)

        # Player controls
        self.btn_play_pause.clicked.connect(self.toggle_play_pause)
        self.btn_reset.clicked.connect(self.reset_playback)
        self.btn_prev.clicked.connect(self.skip_to_previous)
        self.btn_next.clicked.connect(self.skip_to_next)
        self.btn_opener.clicked.connect(self.open_file_dialog)

        # Sliders
        self.speed_slider.valueChanged.connect(self.update_speed)
        self.volume_slider.valueChanged.connect(self.update_volume)

        # Checkboxes
        self.btn_mute.toggled.connect(self.toggle_mute)
        self.btn_repeat.toggled.connect(self.on_repeat_toggled)
        self.btn_play_all.toggled.connect(self.on_play_all_toggled)

        # Progress bar
        self.progress_bar.mousePressEvent = self.progress_bar_clicked

        # Audio player signals
        self.audio_player.positionChanged.connect(
            self.update_playback_position
        )
        self.audio_player.playbackStateChanged.connect(
            self.handle_playback_state_changed
        )
        self.audio_player.mediaStatusChanged.connect(
            self.handle_media_status_changed
        )
        self.audio_player.metadataChanged.connect(self.update_track_metadata)

    def apply_styling(self) -> None:
        """Apply styling to UI components."""
        self.setStyleSheet(
            """
            QWidget {
                background-color: #1E1E1E;
                color: #EAEAEA;
                font-family: 'Segoe UI', sans-serif;
            }

            QLabel {
                color: #EAEAEA;
                font-size: 14px;
            }

            QLabel#timeLabel {
                color: #999;
                font-size: 12px;
            }

            QLabel#album_art{
                background-color: #444;
                border-radius: 8px;
                border: 1px solid #5BB9C2;
            }

            QListWidget {
                background-color: #2B2B2B;
                border: none;
                border-radius: 8px;
                padding: 5px;
            }

            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #3A3A3A;
            }

            QListWidget::item:selected {
                background-color: #5BB9C2;
                color: #000;
                border-radius: 5px;
            }

            QListWidget::item:hover {
                background-color: #3A3A3A;
            }

            QPushButton {
                background-color: #2B2B2B;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: #5BB9C2;
                border: 1px solid #5BB9C2;
            }

            QPushButton:disabled {
                background-color: #1E1E1E;
                color: #777;
            }

            QCheckBox {
                padding: 8px;
            }

            QSlider::groove:horizontal {
                height: 6px;
                background: #444;
                border-radius: 3px;
            }

            QSlider::handle:horizontal {
                background: #5BB9C2;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }

            QSlider::sub-page:horizontal {
                background: #5BB9C2;
                border-radius: 3px;
            }

            QProgressBar {
                height: 8px;
                background-color: #333;
                border-radius: 4px;
            }

            QProgressBar::chunk {
                background-color: #5BB9C2;
                border-radius: 4px;
            }

            QLineEdit {
                padding: 6px 10px;
                font-size: 14px;
                border: 1px solid #555;
                border-radius: 6px;
                background-color: #2B2B2B;
                color: #EAEAEA;
            }
        """
        )

    def load_settings(self) -> None:
        """Load settings from config file and apply them."""
        # Get settings
        volume = self.config_manager.get_int("volume", 50)
        speed = self.config_manager.get_int("speed", 100)
        repeat = self.config_manager.get_bool("repeat", False)
        mute = self.config_manager.get_bool("mute", False)
        play_all = self.config_manager.get_bool("play_all", False)
        last_folder = self.config_manager.get("last_folder", "")
        last_track = self.config_manager.get("last_track", "")

        # Apply settings to UI
        self.volume_slider.setValue(volume)
        self.speed_slider.setValue(speed)
        self.btn_repeat.setChecked(repeat)
        self.btn_mute.setChecked(mute)
        self.btn_play_all.setChecked(play_all)

        # Set folder and select last track
        if last_folder and Path(last_folder).exists():
            self.track_manager.set_folder(last_folder)
            self.populate_playlist()

            # Try to find and select the last played track
            if last_track:
                try:
                    last_track_url = QUrl(last_track)
                    if (
                        last_track_url.isValid()
                        and last_track_url.isLocalFile()
                    ):
                        track_path = Path(last_track_url.toLocalFile())
                        rel_path = track_path.relative_to(Path(last_folder))
                        for i in range(self.playlist.count()):
                            if self.playlist.item(i).text() == str(rel_path):
                                self.playlist.setCurrentRow(i)
                                break
                except Exception as e:
                    print(f"Error selecting last track: {e}")

        # Update controls based on settings
        self.update_volume()
        self.update_speed()
        self.update_skip_buttons()

    def save_settings(self) -> None:
        """Save current settings to config file."""
        # Save settings
        self.config_manager.set("volume", self.volume_slider.value())
        self.config_manager.set("speed", self.speed_slider.value())
        self.config_manager.set("repeat", self.btn_repeat.isChecked())
        self.config_manager.set("mute", self.btn_mute.isChecked())
        self.config_manager.set("play_all", self.btn_play_all.isChecked())

        # Save folder
        folder = self.track_manager.get_current_folder()
        if folder:
            self.config_manager.set("last_folder", folder)

        # Save track
        if self.audio_player.current_track_url:
            self.config_manager.set(
                "last_track", self.audio_player.current_track_url.toString()
            )

        # Write to file
        self.config_manager.save_settings()

    def filter_tracks(self, text: str) -> None:
        """
        Filter tracks in the playlist based on search text.

        Args:
            text: Search text
        """
        filtered_tracks = self.track_manager.filter_tracks(text)

        for i in range(self.playlist.count()):
            item = self.playlist.item(i)
            item_text = item.text()
            item_visible = any(
                track[0] == item_text and track[1] for track in filtered_tracks
            )
            item.setHidden(not item_visible)

    def toggle_play_pause(self) -> None:
        """Toggle between play and pause states."""
        if self.audio_player.is_playing():
            self.audio_player.pause()
            self.btn_play_pause.setIcon(QIcon(get_icon_path("play.png")))
        else:
            # If no track is selected, play the selected one
            if not self.audio_player.current_track_url:
                self.play_selected_track()
            else:
                self.audio_player.play()
                self.btn_play_pause.setIcon(QIcon(get_icon_path("pause.png")))
                self.btn_reset.setEnabled(True)

    def play_selected_track(self) -> None:
        """Play the currently selected track in the playlist."""
        if (
            not self.playlist.currentItem()
            or not self.track_manager.get_current_folder()
        ):
            return

        rel_path = self.playlist.currentItem().text()
        file_path = self.track_manager.get_absolute_path(rel_path)

        if not file_path.exists():
            QMessageBox.warning(
                self, "File Missing", f"Cannot find {file_path}"
            )
            return

        # Stop current playback if any
        if self.audio_player.is_playing():
            self.audio_player.stop()

        # Set up and play the new track
        self.ignore_auto_advance = True
        self.audio_player.load_track(file_path)
        self.audio_player.set_playback_rate(self.speed_slider.value() / 100.0)
        self.audio_player.play()

        self.btn_play_pause.setIcon(QIcon(get_icon_path("pause.png")))
        self.btn_reset.setEnabled(True)

        # Update UI
        metadata = self.audio_player.current_metadata
        title = metadata.get("title", file_path.name)
        self.set_track_title(title)

        # Save settings
        self.save_settings()
        self.update_skip_buttons()

    def reset_playback(self) -> None:
        """Reset the playback to the beginning."""
        if not self.audio_player.is_stopped():
            self.user_stopped = True  # Prevent Play All logic
            self.audio_player.fade_out()

        self.audio_player.seek(0)
        self.progress_bar.setValue(0)
        self.time_label.setText("00:00 / 00:00")

        # Update button states
        self.btn_play_pause.setIcon(QIcon(get_icon_path("play.png")))
        self.btn_reset.setDisabled(True)

    def skip_to_next(self) -> None:
        """Skip to the next track in the playlist."""
        current_row = self.playlist.currentRow()
        if current_row < self.playlist.count() - 1:
            self.playlist.blockSignals(True)
            self.ignore_auto_advance = True
            self.playlist.setCurrentRow(current_row + 1)
            self.playlist.blockSignals(False)

            if not self.audio_player.is_stopped():
                self.play_selected_track()

            self.update_skip_buttons()

    def skip_to_previous(self) -> None:
        """Skip to the previous track in the playlist."""
        current_row = self.playlist.currentRow()
        if current_row > 0:
            self.playlist.blockSignals(True)
            self.ignore_auto_advance = True
            self.playlist.setCurrentRow(current_row - 1)
            self.playlist.blockSignals(False)

            if not self.audio_player.is_stopped():
                self.play_selected_track()

            self.update_skip_buttons()

    def open_file_dialog(self) -> None:
        """Open a file dialog to select a folder or audio file."""
        initial_dir = self.track_manager.get_current_folder() or ""
        path = QFileDialog.getExistingDirectory(
            self, "Select Folder", initial_dir
        )

        if path:
            # Set folder and scan for tracks
            self.track_manager.set_folder(path)
            self.populate_playlist()
        else:
            # If folder selection was canceled, try file selection
            file_filter = (
                "Audio Files (*.mp3 *.flac *.wav *.ogg);;All Files (*)"
            )
            file, _ = QFileDialog.getOpenFileName(
                self, "Select File", initial_dir, filter=file_filter
            )

            if file:
                # Set the folder to the parent directory of the selected file
                folder = str(Path(file).parent)
                self.track_manager.set_folder(folder)

                # Add only the selected file to the playlist
                self.playlist.clear()
                self.playlist.addItem(os.path.basename(file))
                self.playlist.setCurrentRow(0)

                self.save_settings()

    def populate_playlist(self) -> None:
        """Populate the playlist with tracks from the current folder."""
        # Clear playlist
        self.playlist.clear()

        # Show progress dialog
        progress = QProgressDialog(
            "Scanning folder...", "Cancel", 0, 100, self
        )
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()

        # Define progress callback
        def update_progress(current, total):
            progress_value = int(min((current / max(total, 1)) * 100, 100))
            progress.setValue(progress_value)
            if progress.wasCanceled():
                return False
            return True

        # Scan folder with progress updates
        tracks = self.track_manager.scan_folder(update_progress)

        # Add tracks to playlist
        for track in tracks:
            self.playlist.addItem(track)

        # Select first track
        if self.playlist.count() > 0:
            self.playlist.setCurrentRow(0)

        # Update UI
        self.update_skip_buttons()

        # Close progress dialog
        progress.close()

    def update_speed(self) -> None:
        """Update the playback speed based on slider value."""
        speed = self.speed_slider.value() / 100
        self.slider_text.setText(f"Speed: {speed:.2f}x")

        # Update player speed if playing
        if self.audio_player.is_playing():
            self.audio_player.set_playback_rate(speed)

        self.save_settings()

    def update_volume(self) -> None:
        """Update volume based on slider value."""
        volume = self.volume_slider.value()
        self.volume_label.setText(f"Volume: {volume}%")

        # Update player volume if not muted
        if not self.btn_mute.isChecked():
            self.audio_player.set_volume(volume / 100.0)

        self.save_settings()

    def toggle_mute(self, checked: bool) -> None:
        """
        Toggle mute state.

        Args:
            checked: Whether mute is checked
        """
        if checked:
            self.audio_player.set_volume(0)
            self.btn_mute.setIcon(QIcon(get_icon_path("unmute.svg")))
            self.btn_mute.setToolTip("Unmute Audio")
        else:
            self.audio_player.set_volume(self.volume_slider.value() / 100.0)
            self.btn_mute.setIcon(QIcon(get_icon_path("mute.svg")))
            self.btn_mute.setToolTip("Mute Audio")

        self.save_settings()

    def on_repeat_toggled(self, checked: bool) -> None:
        """
        Ensure Repeat and Play All are mutually exclusive.

        Args:
            checked: Whether repeat is checked
        """
        if checked and self.btn_play_all.isChecked():
            self.btn_play_all.blockSignals(True)
            self.btn_play_all.setChecked(False)
            self.btn_play_all.blockSignals(False)

    def on_play_all_toggled(self, checked: bool) -> None:
        """
        Ensure Play All and Repeat are mutually exclusive.

        Args:
            checked: Whether play all is checked
        """
        if checked and self.btn_repeat.isChecked():
            self.btn_repeat.blockSignals(True)
            self.btn_repeat.setChecked(False)
            self.btn_repeat.blockSignals(False)

    def progress_bar_clicked(self, event) -> None:
        """
        Handle clicks on the progress bar to seek.

        Args:
            event: Mouse event
        """
        if not self.audio_player.current_track_url:
            return

        # Calculate position from click
        width = self.progress_bar.width()
        x_pos = event.pos().x()
        percentage = max(0, min(1, x_pos / width))

        # Calculate position in milliseconds
        duration = self.audio_player.get_duration()
        position = int(percentage * duration)

        # Seek to position
        self.audio_player.seek(position)

    def update_playback_position(self, position: int) -> None:
        """
        Update progress bar and time label based on playback position.

        Args:
            position: Current position in milliseconds
        """
        duration = self.audio_player.get_duration()
        if duration > 0:
            # Update progress bar
            progress = int((position / duration) * 100)
            self.progress_bar.setValue(progress)

            # Update time label
            self.time_label.setText(
                format_position_duration(position, duration)
            )

    def handle_track_selection_changed(self) -> None:
        """Handle changes in the selected track."""
        self.update_skip_buttons()

    def handle_playback_state_changed(self, state) -> None:
        """
        Update UI based on playback state changes.

        Args:
            state: New playback state
        """
        if state == self.audio_player.media_player.PlaybackState.StoppedState:
            # Skip autoplay logic if user manually changed tracks
            if self.ignore_auto_advance:
                self.ignore_auto_advance = False
                return

            # Auto-repeat if enabled
            if (
                self.btn_repeat.isChecked()
                and self.audio_player.current_track_url
                and self.audio_player.get_position()
                == self.audio_player.get_duration()
            ):
                self.audio_player.seek(0)
                self.audio_player.play()
                return

            # Auto play all if enabled
            if self.btn_play_all.isChecked():
                current_row = self.playlist.currentRow()
                if current_row < self.playlist.count() - 1:
                    self.playlist.setCurrentRow(current_row + 1)
                    self.play_selected_track()
                    return

            # End of playback or user stopped
            self.btn_play_pause.setIcon(QIcon(get_icon_path("play.png")))
            self.btn_reset.setDisabled(True)
            self.update_skip_buttons()

    def handle_media_status_changed(self, status) -> None:
        """
        Handle media status changes (e.g. end of track).

        Args:
            status: New media status
        """
        if status == self.audio_player.media_player.MediaStatus.EndOfMedia:
            # Repeat mode
            if (
                self.btn_repeat.isChecked()
                and self.audio_player.current_track_url
            ):
                self.audio_player.seek(0)
                self.audio_player.play()
                return

            # Play All mode
            if self.btn_play_all.isChecked():
                current_row = self.playlist.currentRow()
                if current_row < self.playlist.count() - 1:
                    self.playlist.blockSignals(True)
                    self.playlist.setCurrentRow(current_row + 1)
                    self.playlist.blockSignals(False)
                    self.play_selected_track()
                    return

            # Reset UI
            self.btn_play_pause.setIcon(QIcon(get_icon_path("play.png")))
            self.btn_reset.setDisabled(True)
            self.update_skip_buttons()

    def update_track_metadata(self, metadata: dict) -> None:
        """
        Update UI with track metadata.

        Args:
            metadata: Track metadata dictionary
        """
        # Update metadata display
        self.metadata_label.setText(format_metadata_display(metadata))

        # Update album art
        file_path = self.audio_player.current_track_path
        if file_path:
            album_art = extract_album_art(file_path)
            if album_art:
                self.album_art.setPixmap(
                    album_art.scaled(
                        80, 80, Qt.AspectRatioMode.KeepAspectRatio
                    )
                )
            else:
                # Reset to default album art
                self.album_art.setPixmap(
                    QPixmap(get_icon_path("default_album.png")).scaled(
                        80, 80, Qt.AspectRatioMode.KeepAspectRatio
                    )
                )

    def set_track_title(self, title: str) -> None:
        """
        Set the track title and start scrolling if necessary.

        Args:
            title: Track title
        """
        self.track_title = title
        self.track_scroll_index = 0

        metrics = QFontMetrics(self.track_label.font())
        text_width = metrics.horizontalAdvance(title)
        label_width = self.track_label.width()

        if text_width > label_width:
            self.scroll_timer.start()
        else:
            self.scroll_timer.stop()
            self.track_label.setText(f"Now Playing: {title}")

    def scroll_track_title(self) -> None:
        """Scroll the track title if it exceeds the label width."""
        spacer = "   —   "
        full_text = self.track_title + spacer
        metrics = QFontMetrics(self.track_label.font())

        # Extract visible part based on pixel width
        visible_width = self.track_label.width()
        start = self.track_scroll_index

        for i in range(1, len(full_text)):
            if (
                metrics.horizontalAdvance(full_text[start : start + i])
                > visible_width
            ):
                break

        visible_text = full_text[start : start + i]
        self.track_label.setText(f"Now Playing: {visible_text}")
        self.track_scroll_index = (self.track_scroll_index + 1) % len(
            full_text
        )

    def update_skip_buttons(self) -> None:
        """Enable or disable skip buttons based on playlist selection."""
        current_row = self.playlist.currentRow()
        count = self.playlist.count()

        self.btn_prev.setEnabled(current_row > 0)
        self.btn_next.setEnabled(current_row < count - 1 and count > 0)

    def closeEvent(self, event) -> None:
        """
        Save settings when the window is closed.

        Args:
            event: Close event
        """
        self.save_settings()
        event.accept()

    def keyPressEvent(self, event) -> None:
        """
        Handle keyboard shortcuts.

        Args:
            event: Key press event
        """
        key = event.key()
        modifiers = event.modifiers()

        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            current_row = self.playlist.currentRow()
            if key == Qt.Key.Key_Up:
                self.playlist.setCurrentRow(max(0, current_row - 1))
            else:
                self.playlist.setCurrentRow(
                    min(self.playlist.count() - 1, current_row + 1)
                )
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.play_selected_track()
        elif key == Qt.Key.Key_Space:
            self.toggle_play_pause()
        elif key == Qt.Key.Key_Escape:
            self.reset_playback()
        elif (
            key == Qt.Key.Key_O
            and modifiers == Qt.KeyboardModifier.ControlModifier
        ):
            self.open_file_dialog()
        elif (
            key == Qt.Key.Key_M
            and modifiers == Qt.KeyboardModifier.ControlModifier
        ):
            self.btn_mute.toggle()
        elif (
            key == Qt.Key.Key_R
            and modifiers == Qt.KeyboardModifier.ControlModifier
        ):
            self.btn_repeat.toggle()
        elif (
            key == Qt.Key.Key_Plus
            and modifiers == Qt.KeyboardModifier.ControlModifier
        ):
            self.speed_slider.setValue(
                min(150, self.speed_slider.value() + 10)
            )
        elif (
            key == Qt.Key.Key_Minus
            and modifiers == Qt.KeyboardModifier.ControlModifier
        ):
            self.speed_slider.setValue(max(50, self.speed_slider.value() - 10))
        else:
            super().keyPressEvent(event)
