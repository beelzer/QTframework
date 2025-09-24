"""
Qt Framework Feature Showcase - Main Application
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.showcase_window import ShowcaseWindow
from PySide6.QtWidgets import QApplication


def main():
    """Run the showcase application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Qt Framework Showcase")
    app.setOrganizationName("Qt Framework")
    app.setStyle("Fusion")

    window = ShowcaseWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
