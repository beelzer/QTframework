"""
Qt Framework Feature Showcase - Main Application
"""

from __future__ import annotations

import sys
from pathlib import Path


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.showcase_window import ShowcaseWindow

from qtframework.core import Application
from qtframework.i18n import I18nManager


def main():
    """Run the showcase application."""
    # Set Qt attributes before creating QApplication to prevent flickering
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication as QApp

    QApp.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApp.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = Application(sys.argv)
    app.setApplicationName("Qt Framework Showcase")
    app.setOrganizationName("Qt Framework")
    app.setStyle("Fusion")

    # Initialize i18n manager
    i18n_manager = I18nManager()
    app.i18n = i18n_manager  # Store on application instance

    window = ShowcaseWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
