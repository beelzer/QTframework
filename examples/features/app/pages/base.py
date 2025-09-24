"""
Base class for demo pages.
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget


class DemoPage(QWidget):
    """Base class for all demo pages."""

    def __init__(self, title: str = "", scrollable: bool = True):
        """Initialize the demo page."""
        super().__init__()
        self.title = title
        self._init_ui(scrollable)

    def _init_ui(self, scrollable: bool):
        """Initialize the UI."""
        main_layout = QVBoxLayout(self)

        if scrollable:
            # Create scroll area
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)

            # Create content widget
            self.content_widget = QWidget()
            self.content_layout = QVBoxLayout(self.content_widget)

            # Add title if provided
            if self.title:
                title_label = QLabel(self.title)
                title_label.setProperty("heading", "h1")
                self.content_layout.addWidget(title_label)

            scroll.setWidget(self.content_widget)
            main_layout.addWidget(scroll)
        else:
            self.content_layout = main_layout

            # Add title if provided
            if self.title:
                title_label = QLabel(self.title)
                title_label.setProperty("heading", "h1")
                self.content_layout.addWidget(title_label)

    def add_section(self, title: str, widget: QWidget):
        """Add a section to the page."""
        if title:
            section_title = QLabel(title)
            section_title.setProperty("heading", "h2")
            self.content_layout.addWidget(section_title)

        self.content_layout.addWidget(widget)

    def add_stretch(self):
        """Add stretch to the layout."""
        self.content_layout.addStretch()
