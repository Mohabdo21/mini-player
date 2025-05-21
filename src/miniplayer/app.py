"""
Main entry point for MiniPlayer application.

This module contains the application entry point and startup logic.
"""

import sys

from PyQt6.QtWidgets import QApplication

from miniplayer.ui import MainWindow


def main():
    """Main function to start the MiniPlayer application."""
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
