import configparser
import os
import sys
from pathlib import Path
from typing import Optional

from mutagen import File
from PyQt6.QtCore import Qt, QTime, QTimer, QUrl
from PyQt6.QtGui import QFontMetrics, QIcon, QPixmap
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QProgressBar,
    QProgressDialog,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class AudioApp(QWidget):
    """Audio Adjuster GUI application."""

    CONFIG_FILE = "mini_player.ini"
    CONFIG_SECTION = "Settings"
    SUPPORTED_EXTENSIONS = (".mp3", ".flac", ".wav", ".ogg")

    def __init__(self) -> None:
        super().__init__()
        self.config = configparser.ConfigParser()
        self.current_folder = None
        self.current_track = None
        self.user_stopped = False
        self.ignore_auto_advance = False
        self.settings()
        self.initUI()
        self.load_settings()
        self.file_list.setFocus()
        self.fade_timer = QTimer(self)
        self.fade_duration = 500  # milliseconds for fade out
        self.fade_steps = 10  # number of steps for fade
        self.fade_interval = self.fade_duration // self.fade_steps
        self.original_volume = 1.0
        self.event_handler()
        self.setWindowIcon(QIcon(self.get_icon_path("mini-player.svg")))

    def settings(self):
        """Set up the main window settings."""
        self.setWindowTitle("Mini Player")
        self.setGeometry(800, 500, 800, 400)

    def initUI(self):
        """Initialize the redesigned UI components."""
        # File list and search bar
        file_list_container = QVBoxLayout()

        # Add search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search tracks...")
        self.search_bar.setClearButtonEnabled(True)
        file_list_container.addWidget(self.search_bar)
        file_list_container.setSpacing(6)

        # File list
        self.file_list = QListWidget()
        file_list_container.addWidget(self.file_list)

        # Add metadata display label
        self.metadata_label = QLabel()
        self.metadata_label.setWordWrap(True)
        self.metadata_label.setStyleSheet(
            "font-size: 12px; color: #B0B0B0; margin-top: 2px;"
        )
        self.metadata_label.setTextFormat(Qt.TextFormat.RichText)

        # Now Playing section
        self.album_art = QLabel()
        self.album_art.setObjectName("album_art")
        self.album_art.setFixedSize(80, 80)
        self.album_art.setStyleSheet(
            "background-color: #444; border-radius: 8px;"
        )
        self.album_art.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.album_art.setPixmap(
            QPixmap(self.get_icon_path("default_album.png")).scaled(
                80, 80, Qt.AspectRatioMode.KeepAspectRatio
            )
        )

        self.track_label = QLabel("Now Playing: ")
        self.track_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.track_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #5BB9C2;"
        )
        self.track_title = ""
        self.track_scroll_index = 0
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.scroll_track_title)
        self.scroll_timer.setInterval(150)
        self.track_label.setMinimumWidth(200)
        self.track_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.track_label.setMaximumHeight(40)

        now_playing_layout = QVBoxLayout()
        top_row = QHBoxLayout()
        top_row.addWidget(self.album_art)
        top_row.addWidget(self.track_label)
        top_row.setSpacing(10)
        now_playing_layout.addLayout(top_row)
        now_playing_layout.addWidget(self.metadata_label)
        now_playing_layout.setSpacing(4)

        # Playback buttons with icons
        self.btn_play_pause = QPushButton()
        self.btn_play_pause.setIcon(QIcon(self.get_icon_path("play.png")))
        self.btn_play_pause.setToolTip("Play / Pause")

        self.btn_prev = QPushButton()
        self.btn_prev.setIcon(QIcon(self.get_icon_path("prev.png")))
        self.btn_prev.setToolTip("Previous Track")

        self.btn_next = QPushButton()
        self.btn_next.setIcon(QIcon(self.get_icon_path("next.png")))
        self.btn_next.setToolTip("Next Track")

        self.btn_reset = QPushButton()
        self.btn_reset.setIcon(QIcon(self.get_icon_path("reset.png")))
        self.btn_reset.setToolTip("Stop")

        self.btn_opener = QPushButton()
        self.btn_opener.setIcon(QIcon(self.get_icon_path("folder.png")))
        self.btn_opener.setToolTip("Open Folder")

        self.btn_repeat = QCheckBox()
        self.btn_repeat.setIcon(QIcon(self.get_icon_path("repeat.svg")))
        self.btn_repeat.setToolTip("Repeat Track")

        self.btn_mute = QCheckBox()
        self.btn_mute.setIcon(QIcon(self.get_icon_path("mute.svg")))
        self.btn_mute.setToolTip("Mute Audio")

        self.btn_play_all = QCheckBox()
        self.btn_play_all.setIcon(QIcon(self.get_icon_path("play-all.png")))
        self.btn_play_all.setToolTip("Play All Tracks")

        self.btn_play_pause.setEnabled(True)
        self.btn_reset.setDisabled(True)
        self.btn_prev.setDisabled(True)
        self.btn_next.setDisabled(True)
        self.btn_repeat.setCheckState(Qt.CheckState.Unchecked)

        # Speed + Volume
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(50)
        self.slider.setMaximum(150)
        self.slider.setValue(100)

        self.slider_text = QLabel("Speed: 1.00x")
        self.slider_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)

        self.volume_label = QLabel("Volume: 50%")
        self.volume_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Progress + time
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setMouseTracking(True)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layouts
        playback_buttons = QHBoxLayout()
        playback_buttons.setSpacing(10)
        for btn in [
            self.btn_opener,
            self.btn_prev,
            self.btn_play_pause,
            self.btn_next,
            self.btn_reset,
        ]:
            playback_buttons.addWidget(btn)

        status_controls = QHBoxLayout()
        status_controls.addWidget(self.btn_repeat)
        status_controls.addWidget(self.btn_mute)
        status_controls.addWidget(self.btn_play_all)
        status_controls.addStretch()
        status_controls.addWidget(self.time_label)

        speed_layout = QHBoxLayout()
        speed_layout.addWidget(self.slider_text)
        speed_layout.addWidget(self.slider)

        volume_layout = QHBoxLayout()
        volume_layout.addWidget(self.volume_label)
        volume_layout.addWidget(self.volume_slider)

        sliders = QVBoxLayout()
        sliders.addLayout(speed_layout)
        sliders.addLayout(volume_layout)

        track_area = QVBoxLayout()
        track_area.addLayout(now_playing_layout)
        track_area.addWidget(self.progress_bar)
        track_area.addLayout(status_controls)
        track_area.addLayout(playback_buttons)
        track_area.addLayout(sliders)
        track_area.setSpacing(8)

        # Master layout
        main_layout = QHBoxLayout()
        main_layout.addLayout(file_list_container, 3)
        main_layout.addLayout(track_area, 5)

        self.setLayout(main_layout)
        self.master = main_layout

        self.style()

        # Media
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.5)
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)

        self.timer = QTimer(self)
        self.timer.setInterval(10)

    def style(self):
        """Apply stylish modern look."""
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
        self.time_label.setObjectName("timeLabel")
        self.slider_text.setObjectName("speedLabel")
        self.volume_label.setObjectName("volumeLabel")

        self.progress_bar.setFixedHeight(8)
        self.master.setContentsMargins(20, 15, 20, 15)

    def event_handler(self):
        """Connect UI components to their respective functions."""
        self.slider.valueChanged.connect(self.update_slider)
        self.btn_opener.clicked.connect(self.open_file)
        self.btn_play_pause.clicked.connect(self.toggle_play_pause)
        self.btn_reset.clicked.connect(self.reset_audio)
        self.btn_prev.clicked.connect(self.skip_to_previous)
        self.btn_next.clicked.connect(self.skip_to_next)
        self.timer.timeout.connect(self.update_progress)
        self.progress_bar.mousePressEvent = self.progress_bar_clicked
        self.file_list.itemSelectionChanged.connect(self.track_changed)
        self.media_player.playbackStateChanged.connect(
            self.handle_playback_state
        )
        self.volume_slider.valueChanged.connect(self.update_volume)
        self.btn_mute.toggled.connect(self.toggle_mute)
        self.fade_timer.timeout.connect(self.fade_step)
        self.search_bar.textChanged.connect(self.filter_tracks)
        self.file_list.itemDoubleClicked.connect(
            self.play_double_clicked_track
        )
        self.media_player.mediaStatusChanged.connect(self.handle_media_status)
        self.btn_repeat.toggled.connect(self.on_repeat_toggled)
        self.btn_play_all.toggled.connect(self.on_play_all_toggled)

    def filter_tracks(self, text):
        """Filter the file list based on search text."""
        if not self.current_folder:
            return

        search_text = text.lower()

        # Show all items if search is empty
        if not search_text:
            for i in range(self.file_list.count()):
                self.file_list.item(i).setHidden(False)
            return

        # Filter items
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            item_text = item.text().lower()
            item.setHidden(search_text not in item_text)

    def toggle_play_pause(self):
        """Toggle play/pause state."""
        state = self.media_player.playbackState()
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.btn_play_pause.setIcon(QIcon(self.get_icon_path("play.png")))
            self.timer.stop()
        else:
            if not self.current_track:
                self.play_audio()  # fallback if nothing playing yet
            else:
                self.media_player.play()
                self.btn_play_pause.setIcon(
                    QIcon(self.get_icon_path("pause.png"))
                )
                self.btn_reset.setEnabled(True)
                self.timer.start()

    def play_double_clicked_track(self, item):
        """Play the track that was double-clicked in the file list."""
        if not self.current_folder:
            return

        # Get the file path from the clicked item
        rel_path = item.text()
        file_path = Path(self.current_folder) / rel_path

        if not file_path.exists():
            QMessageBox.warning(
                self, "File Missing", f"Cannot find {file_path}"
            )
            return

        # Stop current playback if any
        if (
            self.media_player.playbackState()
            != QMediaPlayer.PlaybackState.StoppedState
        ):
            self.media_player.stop()

        # Set up and play the new track
        self.ignore_auto_advance = True
        file_url = QUrl.fromLocalFile(str(file_path))
        self.current_track = file_url
        self.media_player.setSource(file_url)
        self.media_player.setPlaybackRate(self.slider.value() / 100.0)

        # Set track info and metadata
        metadata = self.get_audio_metadata(file_path)
        title = metadata.get("title", file_path.name)
        self.set_track_title(title)
        self.metadata_label.setText(self.format_metadata_display(metadata))
        self.extract_album_art(file_path)

        # Start playback and update UI
        self.media_player.play()
        self.btn_play_pause.setIcon(QIcon(self.get_icon_path("pause.png")))
        self.btn_reset.setEnabled(True)
        self.timer.start()
        self.save_settings()
        self.update_skip_buttons()

    def skip_to_next(self):
        """Skip to the next track without triggering unintended resets."""
        current_row = self.file_list.currentRow()
        if current_row < self.file_list.count() - 1:
            self.file_list.blockSignals(True)
            self.ignore_auto_advance = True
            self.file_list.setCurrentRow(current_row + 1)
            self.file_list.blockSignals(False)
            if (
                self.media_player.playbackState()
                != QMediaPlayer.PlaybackState.StoppedState
            ):
                self.play_audio()
            self.update_skip_buttons()

    def skip_to_previous(self):
        """Skip to the previous track without triggering unintended resets."""
        current_row = self.file_list.currentRow()
        if current_row > 0:
            self.file_list.blockSignals(True)
            self.ignore_auto_advance = True
            self.file_list.setCurrentRow(current_row - 1)
            self.file_list.blockSignals(False)
            if (
                self.media_player.playbackState()
                != QMediaPlayer.PlaybackState.StoppedState
            ):
                self.play_audio()
            self.update_skip_buttons()

    def on_repeat_toggled(self, checked):
        """Ensure Repeat and Play All are mutually exclusive."""
        if checked and self.btn_play_all.isChecked():
            self.btn_play_all.blockSignals(True)
            self.btn_play_all.setChecked(False)
            self.btn_play_all.blockSignals(False)

    def on_play_all_toggled(self, checked):
        """Ensure Play All and Repeat are mutually exclusive."""
        if checked and self.btn_repeat.isChecked():
            self.btn_repeat.blockSignals(True)
            self.btn_repeat.setChecked(False)
            self.btn_repeat.blockSignals(False)

    def toggle_mute(self, checked):
        """Toggle mute state."""
        if checked:
            self.audio_output.setVolume(0)
            self.btn_mute.setIcon(QIcon(self.get_icon_path("unmute.svg")))
            self.btn_mute.setToolTip("Unmute Audio")
        else:
            self.audio_output.setVolume(self.volume_slider.value() / 100.0)
            self.btn_mute.setIcon(QIcon(self.get_icon_path("mute.svg")))
            self.btn_mute.setToolTip("Mute Audio")
        self.save_settings()

    def update_volume(self):
        """Update the volume based on slider value."""
        volume = self.volume_slider.value()
        self.volume_label.setText(f"Volume: {volume}%")
        if not self.btn_mute.isChecked():  # Only update volume if not muted
            self.audio_output.setVolume(volume / 100.0)
        self.save_settings()

    def progress_bar_clicked(self, event):
        """Handle mouse click events on the progress bar."""
        if self.media_player.duration() > 0:
            # Calculate the position based on click location
            pos = event.pos().x()
            percent = pos / self.progress_bar.width()
            duration = self.media_player.duration()
            seek_position = int(percent * duration)
            self.media_player.setPosition(seek_position)

    def update_slider(self):
        """Update the speed label based on the slider value."""
        speed = self.slider.value() / 100
        self.slider_text.setText(f"Speed: {speed:.2f}x")
        if (
            self.media_player.playbackState()
            == QMediaPlayer.PlaybackState.PlayingState
        ):
            self.media_player.setPlaybackRate(speed)
        self.save_settings()

    def handle_media_status(self, status):
        """Handle status change to detect end-of-track and act on Play All / Repeat."""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            # Repeat mode
            if self.btn_repeat.isChecked() and self.current_track:
                self.media_player.setPosition(0)
                self.media_player.play()
                return

            # Play All mode
            if self.btn_play_all.isChecked():
                current_row = self.file_list.currentRow()
                if current_row < self.file_list.count() - 1:
                    self.file_list.blockSignals(True)
                    try:
                        self.file_list.setCurrentRow(current_row + 1)
                    finally:
                        self.file_list.blockSignals(False)
                    self.play_audio()
                    return

            # Fallback: reset player UI
            self.btn_play_pause.setIcon(QIcon(self.get_icon_path("play.png")))
            self.btn_reset.setDisabled(True)
            self.timer.stop()
            self.update_skip_buttons()

    def open_file(self):
        """Open a file dialog to select an audio file or folder."""
        initial_dir = str(self.current_folder) if self.current_folder else ""
        path = QFileDialog.getExistingDirectory(
            self, "Select Folder", initial_dir
        )

        if path:
            self.current_folder = path
            self.populate_file_list(path)
            self.save_settings()
        else:
            file_filter = (
                "Audio Files (*.mp3 *.flac *.wav *.ogg);;All Files (*)"
            )
            file, _ = QFileDialog.getOpenFileName(
                self, "Select File", initial_dir, filter=file_filter
            )
            if file:
                self.current_folder = str(Path(file).parent)
                self.file_list.clear()
                self.file_list.addItem(os.path.basename(file))
                self.save_settings()

    def populate_file_list(self, folder_path):
        """Optimized recursive file search with progress feedback."""
        self.file_list.clear()
        if not folder_path or not os.path.exists(folder_path):
            return

        # Show progress
        progress = QProgressDialog(
            "Scanning folder...", "Cancel", 0, 100, self
        )
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()

        file_count = 0
        for root, _, files in os.walk(folder_path):
            for file_name in files:
                if file_name.lower().endswith(self.SUPPORTED_EXTENSIONS):
                    rel_path = os.path.relpath(
                        os.path.join(root, file_name), folder_path
                    )
                    self.file_list.addItem(rel_path)
                    file_count += 1

                # Update progress every 100 files
                if file_count % 100 == 0:
                    progress.setValue(file_count % 100)
                    if progress.wasCanceled():
                        break

            if progress.wasCanceled():
                break

        self.file_list.setCurrentRow(0)
        self.update_skip_buttons()
        progress.close()

    def play_audio(self):
        """Play the selected audio file with metadata support."""
        if not self.file_list.selectedItems() or not self.current_folder:
            return

        rel_path = self.file_list.selectedItems()[0].text()
        file_path = Path(self.current_folder) / rel_path

        if not file_path.exists():
            QMessageBox.warning(
                self, "File Missing", f"Cannot find {file_path}"
            )
            return

        # Stop current playback if it's a different track
        current_file = (
            Path(QUrl(self.current_track).path())
            if self.current_track
            else None
        )
        if (
            self.media_player.playbackState()
            != QMediaPlayer.PlaybackState.StoppedState
            and current_file != file_path
        ):
            self.media_player.stop()

        # Set up new track
        file_url = QUrl.fromLocalFile(str(file_path))
        self.current_track = file_url
        self.media_player.setSource(file_url)
        self.media_player.setPlaybackRate(self.slider.value() / 100.0)

        # Set track title
        metadata = self.get_audio_metadata(file_path)
        title = metadata.get("title", file_path.name)
        self.set_track_title(title)

        # Display metadata
        self.metadata_label.setText(self.format_metadata_display(metadata))

        # Extract and display album art
        self.extract_album_art(file_path)

        # Start playback
        self.media_player.play()
        self.btn_play_pause.setIcon(QIcon(self.get_icon_path("pause.png")))
        self.btn_reset.setEnabled(True)
        self.timer.start()
        self.save_settings()
        self.update_skip_buttons()

    def set_track_title(self, title: str):
        """Set the track title and start scrolling if necessary."""
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

    def scroll_track_title(self):
        """Scroll the track title if it exceeds the label width."""
        spacer = "   —   "
        full_text = self.track_title + spacer
        metrics = QFontMetrics(self.track_label.font())

        # Extract the visible part based on pixel width
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

    def track_changed(self):
        """Handle changes in the selected track."""
        # Only proceed if we have a valid selection and folder
        if not self.file_list.selectedItems() or not self.current_folder:
            return

        # Get the new selection
        new_selection = self.file_list.selectedItems()[0].text()
        try:
            file_path = Path(self.current_folder) / new_selection
        except TypeError:
            # Handle case where current_folder is None (shouldn't happen due to above check)
            return

        # Don't reset if selecting the currently playing track
        if (
            self.current_track
            and Path(QUrl(self.current_track).path()) == str(file_path)
            and self.media_player.playbackState()
            == QMediaPlayer.PlaybackState.PlayingState
        ):
            return

        # Reset player state
        # if self.media_player.playbackState() != QMediaPlayer.PlaybackState.StoppedState:
        #     self.fade_out()
        #
        # # Reset UI elements
        # self.progress_bar.setValue(0)
        # self.time_label.setText("00:00 / 00:00")
        # self.btn_play_pause.setIcon(QIcon(self.get_icon_path("play.png")))
        # self.btn_reset.setDisabled(True)
        # self.update_skip_buttons()

    def pause_audio(self):
        """Pause the currently playing audio."""
        self.media_player.pause()
        self.btn_play_pause.setIcon(QIcon(self.get_icon_path("play.png")))
        self.timer.stop()

    def resume_audio(self):
        """Resume the currently paused audio."""
        self.media_player.play()
        self.btn_play_pause.setIcon(QIcon(self.get_icon_path("pause.png")))
        self.timer.start()

    def handle_playback_state(self, state):
        """Handle when playback state changes."""
        if state == QMediaPlayer.PlaybackState.StoppedState:
            # Skip autoplay logic if user just skipped or double-clicked
            if self.ignore_auto_advance:
                self.ignore_auto_advance = False
                return

            # Auto-repeat if applicable
            if (
                self.btn_repeat.isChecked()
                and self.current_track
                and self.media_player.position()
                == self.media_player.duration()
            ):
                self.media_player.setPosition(0)
                self.media_player.play()
                return

            # Auto Play All
            if self.btn_play_all.isChecked():
                current_row = self.file_list.currentRow()
                if current_row < self.file_list.count() - 1:
                    self.file_list.setCurrentRow(current_row + 1)
                    self.play_audio()
                    return

            # End of playlist or playback — update UI
            self.btn_play_pause.setIcon(QIcon(self.get_icon_path("play.png")))
            self.btn_reset.setDisabled(True)
            self.timer.stop()
            self.update_skip_buttons()

    def reset_audio(self):
        """Reset the audio playback to the beginning."""
        if (
            self.media_player.playbackState()
            != QMediaPlayer.PlaybackState.StoppedState
        ):
            self.user_stopped = True  # Prevent Play All logic
            self.fade_out()

        self.media_player.setPosition(0)
        self.progress_bar.setValue(0)
        self.time_label.setText("00:00 / 00:00")

        # Update button states
        self.btn_play_pause.setIcon(QIcon(self.get_icon_path("play.png")))
        self.btn_reset.setDisabled(True)

        # Stop progress timer
        self.timer.stop()

    def fade_out(self):
        """Start the fade out process."""
        if (
            self.media_player.playbackState()
            == QMediaPlayer.PlaybackState.StoppedState
        ):
            return

        # Store current volume
        self.original_volume = self.audio_output.volume()

        # Start fade timer
        self.fade_timer.start(self.fade_interval)

    def fade_step(self):
        """Reduce volume by one step."""
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

            # Reset UI as before
            self.progress_bar.setValue(0)
            self.time_label.setText("00:00 / 00:00")
            self.btn_play_pause.setIcon(QIcon(self.get_icon_path("play.png")))
            self.btn_reset.setDisabled(True)

    def get_icon_path(self, icon_name: str) -> Optional[str]:
        """Check multiple possible icon locations"""
        paths = [
            # System install locations
            f"/usr/share/icons/hicolor/scalable/apps/{icon_name}",
            f"/usr/share/icons/hicolor/48x48/apps/{icon_name}",
            # Local development
            os.path.join(os.path.dirname(__file__), "icons", f"{icon_name}"),
            os.path.join(os.path.dirname(__file__), f"{icon_name}"),
            # Flatpak/Snap locations
            f"/usr/share/{icon_name}",
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        return None

    def update_progress(self):
        """Update the progress bar and time label based on the current playback position."""
        if (
            self.media_player.playbackState()
            != QMediaPlayer.PlaybackState.StoppedState
        ):
            duration = self.media_player.duration()
            position = self.media_player.position()

            if duration > 0:
                progress = int((position / duration) * 100)
                self.progress_bar.setValue(progress)

                # Update time labels
                current_time = QTime(0, 0).addMSecs(position)
                total_time = QTime(0, 0).addMSecs(duration)

                self.time_label.setText(
                    f"{current_time.toString('mm:ss')} / {total_time.toString('mm:ss')}"
                )

    def load_settings(self):
        """Load settings from config file."""
        # Set default values first
        self.last_volume = 50
        self.last_speed = 100
        self.last_repeat = False
        self.last_mute = False
        self.last_play_all = False
        self.current_folder = None
        self.last_track = None

        if Path(self.CONFIG_FILE).exists():
            self.config.read(self.CONFIG_FILE)
            if self.CONFIG_SECTION in self.config:
                # Override defaults with saved values
                self.current_folder = self.config.get(
                    self.CONFIG_SECTION, "last_folder", fallback=None
                )
                self.last_track = self.config.get(
                    self.CONFIG_SECTION, "last_track", fallback=None
                )
                self.last_volume = int(
                    self.config.get(self.CONFIG_SECTION, "volume", fallback=50)
                )
                self.last_speed = int(
                    self.config.get(self.CONFIG_SECTION, "speed", fallback=100)
                )
                self.last_repeat = self.config.getboolean(
                    self.CONFIG_SECTION, "repeat", fallback=False
                )
                self.last_mute = self.config.getboolean(
                    self.CONFIG_SECTION, "mute", fallback=False
                )
                self.last_play_all = self.config.getboolean(
                    self.CONFIG_SECTION, "play_all", fallback=False
                )

        # Apply settings to UI components
        self.volume_slider.setValue(self.last_volume)
        self.slider.setValue(self.last_speed)
        self.btn_repeat.setChecked(self.last_repeat)
        self.btn_mute.setChecked(self.last_mute)
        self.btn_play_all.setChecked(self.last_play_all)
        self.update_volume()
        self.update_slider()

        # Populate file list if folder exists
        if self.current_folder and Path(self.current_folder).exists():
            self.populate_file_list(self.current_folder)
            if self.last_track:
                try:
                    # Convert the saved URL back to a local path
                    last_track_url = QUrl(self.last_track)
                    if (
                        last_track_url.isValid()
                        and last_track_url.isLocalFile()
                    ):
                        last_track_path = Path(last_track_url.toLocalFile())
                        if last_track_path.exists():
                            # Find the track by comparing the full path
                            for i in range(self.file_list.count()):
                                item = self.file_list.item(i)
                                item_path = (
                                    Path(self.current_folder) / item.text()
                                )
                                if item_path == last_track_path:
                                    self.file_list.setCurrentItem(item)
                                    break
                except Exception as e:
                    print(f"Error selecting last track: {e}")

    def get_audio_metadata(self, file_path):
        """Extract metadata using mutagen."""
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
                if tag in audio.tags:
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

    def format_metadata_display(self, metadata):
        """Format metadata for display in the UI."""
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
                f"<b>Duration:</b> {self.format_duration(metadata['duration'])}"
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

    def format_duration(self, seconds):
        """Convert duration in seconds to MM:SS format."""
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def extract_album_art(self, file_path):
        """Extract album art using mutagen."""
        try:
            audio = File(file_path)

            # Check for embedded art
            if hasattr(audio, "pictures") and audio.pictures:
                picture = audio.pictures[0]
                pixmap = QPixmap()
                pixmap.loadFromData(picture.data)
                if not pixmap.isNull():
                    self.album_art.setPixmap(
                        pixmap.scaled(
                            80,
                            80,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                    )
                    return

            # For MP3 files with ID3 tags
            if file_path.suffix.lower() == ".mp3" and "APIC:" in audio.tags:
                picture = audio.tags["APIC:"].data
                pixmap = QPixmap()
                pixmap.loadFromData(picture)
                if not pixmap.isNull():
                    self.album_art.setPixmap(
                        pixmap.scaled(
                            80,
                            80,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                    )
                    return

            # For FLAC files with cover art
            if file_path.suffix.lower() == ".flac":
                for block in audio.metadata_blocks:
                    if (
                        hasattr(block, "type") and block.type == 6
                    ):  # Picture block
                        pixmap = QPixmap()
                        pixmap.loadFromData(block.data)
                        if not pixmap.isNull():
                            self.album_art.setPixmap(
                                pixmap.scaled(
                                    80,
                                    80,
                                    Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation,
                                )
                            )
                            return

            # Fallback to default image
            self.album_art.setPixmap(
                QPixmap(self.get_icon_path("default_album.png")).scaled(
                    80, 80, Qt.AspectRatioMode.KeepAspectRatio
                )
            )

        except Exception as e:
            print(f"Error extracting album art: {e}")
            self.album_art.setPixmap(
                QPixmap(self.get_icon_path("default_album.png")).scaled(
                    80, 80, Qt.AspectRatioMode.KeepAspectRatio
                )
            )

    def save_settings(self):
        """Save current settings to config file."""
        if not self.config.has_section(self.CONFIG_SECTION):
            self.config.add_section(self.CONFIG_SECTION)

        # Save paths as strings, not QUrl.toString() which can have issues with spaces
        self.config.set(
            self.CONFIG_SECTION, "last_folder", str(self.current_folder or "")
        )

        # Store the local file path directly instead of QUrl.toString()
        if self.current_track and self.current_track.isLocalFile():
            track_path = self.current_track.toLocalFile()
            self.config.set(self.CONFIG_SECTION, "last_track", track_path)
        else:
            self.config.set(self.CONFIG_SECTION, "last_track", "")

        self.config.set(
            self.CONFIG_SECTION, "volume", str(self.volume_slider.value())
        )
        self.config.set(self.CONFIG_SECTION, "speed", str(self.slider.value()))
        self.config.set(
            self.CONFIG_SECTION, "repeat", str(self.btn_repeat.isChecked())
        )
        self.config.set(
            self.CONFIG_SECTION, "mute", str(self.btn_mute.isChecked())
        )
        self.config.set(
            self.CONFIG_SECTION, "play_all", str(self.btn_play_all.isChecked())
        )

        with open(self.CONFIG_FILE, "w", encoding="utf-8") as configfile:
            self.config.write(configfile)

    def update_skip_buttons(self):
        """Enable/disable skip buttons based on current selection."""
        row = self.file_list.currentRow()
        count = self.file_list.count()

        self.btn_prev.setEnabled(row > 0)
        self.btn_next.setEnabled(row < count - 1)

    def closeEvent(self, event):
        """Override close event to save settings."""
        self.save_settings()
        event.accept()

    def keyPressEvent(self, event):
        """Handle global keypress shortcuts."""
        key = event.key()
        modifiers = event.modifiers()

        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            current_row = self.file_list.currentRow()
            if key == Qt.Key.Key_Up:
                self.file_list.setCurrentRow(max(0, current_row - 1))
            else:
                self.file_list.setCurrentRow(
                    min(self.file_list.count() - 1, current_row + 1)
                )

        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.play_audio()

        elif key == Qt.Key.Key_Space:
            if (
                self.media_player.playbackState()
                == QMediaPlayer.PlaybackState.PlayingState
            ):
                self.pause_audio()
            elif (
                self.media_player.playbackState()
                == QMediaPlayer.PlaybackState.PausedState
            ):
                self.resume_audio()

        elif key == Qt.Key.Key_Escape:
            self.reset_audio()

        elif (
            key == Qt.Key.Key_O
            and modifiers == Qt.KeyboardModifier.ControlModifier
        ):
            self.open_file()

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
            self.slider.setValue(min(150, self.slider.value() + 10))

        elif (
            key == Qt.Key.Key_Minus
            and modifiers == Qt.KeyboardModifier.ControlModifier
        ):
            self.slider.setValue(max(50, self.slider.value() - 10))

        else:
            super().keyPressEvent(event)


# Run the app
def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    player = AudioApp()
    player.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
