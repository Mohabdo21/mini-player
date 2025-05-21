"""
Configuration management for MiniPlayer.

This module handles loading, saving, and accessing application settings.
"""

import configparser
from pathlib import Path
from typing import Any, Dict, Optional, Union


class ConfigManager:
    """Manages application configuration settings."""

    def __init__(
        self, config_file: str = "mini_player.ini", section: str = "Settings"
    ):
        """
        Initialize the configuration manager.

        Args:
            config_file: Path to the config file
            section: Main section name in the config file
        """
        self.config_file = config_file
        self.config_section = section
        self.config = configparser.ConfigParser()

        # Default settings
        self.defaults = {
            "volume": "50",
            "speed": "100",
            "repeat": "False",
            "mute": "False",
            "play_all": "False",
            "last_folder": "",
            "last_track": "",
        }

        # Load existing settings or create defaults
        self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from config file.

        Returns:
            Dictionary of settings
        """
        # Set defaults first
        settings = self.defaults.copy()

        # Try to load from file
        if Path(self.config_file).exists():
            self.config.read(self.config_file)

            if self.config_section in self.config:
                # Override defaults with saved values
                for key in self.defaults:
                    if key in self.config[self.config_section]:
                        settings[key] = self.config[self.config_section][key]

        # Ensure the section exists
        if not self.config.has_section(self.config_section):
            self.config.add_section(self.config_section)

        # Set initial values
        for key, value in settings.items():
            self.config.set(self.config_section, key, value)

        return settings

    def save_settings(self) -> None:
        """Save settings to config file."""
        with open(self.config_file, "w", encoding="utf-8") as configfile:
            self.config.write(configfile)

    def get(self, key: str, fallback: Any = None) -> Any:
        """
        Get a setting value.

        Args:
            key: Setting name
            fallback: Default value if setting doesn't exist

        Returns:
            Setting value
        """
        if not self.config.has_section(self.config_section):
            return fallback

        return self.config.get(self.config_section, key, fallback=fallback)

    def get_int(self, key: str, fallback: int = 0) -> int:
        """Get an integer setting value."""
        try:
            return int(self.get(key, fallback))
        except (ValueError, TypeError):
            return fallback

    def get_float(self, key: str, fallback: float = 0.0) -> float:
        """Get a float setting value."""
        try:
            return float(self.get(key, fallback))
        except (ValueError, TypeError):
            return fallback

    def get_bool(self, key: str, fallback: bool = False) -> bool:
        """Get a boolean setting value."""
        value = self.get(key, str(fallback))
        return value.lower() in ("true", "yes", "1", "on")

    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value.

        Args:
            key: Setting name
            value: Setting value
        """
        if not self.config.has_section(self.config_section):
            self.config.add_section(self.config_section)

        self.config.set(self.config_section, key, str(value))

    def as_dict(self) -> Dict[str, str]:
        """
        Get all settings as a dictionary.

        Returns:
            Dictionary of all settings
        """
        if not self.config.has_section(self.config_section):
            return self.defaults.copy()

        return dict(self.config[self.config_section])
