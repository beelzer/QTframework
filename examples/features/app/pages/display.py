"""
Display elements demonstration page.
"""

from PySide6.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QProgressBar,
                               QVBoxLayout)

from .base import DemoPage


class DisplayPage(DemoPage):
    """Page demonstrating display components."""

    def __init__(self):
        """Initialize the display page."""
        super().__init__("Display Components")
        self._create_content()

    def _create_content(self):
        """Create the page content."""
        # Progress bars
        progress_group = self._create_progress_bars()
        self.add_section("", progress_group)

        # Labels and badges
        labels_group = self._create_labels()
        self.add_section("", labels_group)

        # Typography
        typography_group = self._create_typography()
        self.add_section("", typography_group)

        self.add_stretch()

    def _create_progress_bars(self):
        """Create progress bar examples."""
        group = QGroupBox("Progress Indicators")
        layout = QVBoxLayout()

        # Standard progress
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Standard:"))
        progress1 = QProgressBar()
        progress1.setValue(75)
        row1.addWidget(progress1)
        layout.addLayout(row1)

        # Indeterminate progress
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Indeterminate:"))
        progress2 = QProgressBar()
        progress2.setRange(0, 0)
        row2.addWidget(progress2)
        layout.addLayout(row2)

        # Custom range progress
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Custom Range:"))
        progress3 = QProgressBar()
        progress3.setRange(0, 200)
        progress3.setValue(150)
        progress3.setFormat("%v / %m")
        row3.addWidget(progress3)
        layout.addLayout(row3)

        group.setLayout(layout)
        return group

    def _create_labels(self):
        """Create label and badge examples."""
        group = QGroupBox("Labels & Badges")
        layout = QHBoxLayout()

        badges = [
            ("Default", None),
            ("Primary", "primary"),
            ("Success", "success"),
            ("Warning", "warning"),
            ("Danger", "danger"),
            ("Info", "info")
        ]

        for text, variant in badges:
            label = QLabel(text)
            if variant:
                label.setProperty("badge", variant)
            layout.addWidget(label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_typography(self):
        """Create typography examples."""
        group = QGroupBox("Typography")
        layout = QVBoxLayout()

        # Headings
        h1 = QLabel("Heading 1 - Main Title")
        h1.setProperty("heading", "h1")
        layout.addWidget(h1)

        h2 = QLabel("Heading 2 - Section Title")
        h2.setProperty("heading", "h2")
        layout.addWidget(h2)

        h3 = QLabel("Heading 3 - Subsection")
        h3.setProperty("heading", "h3")
        layout.addWidget(h3)

        # Text variants
        normal = QLabel("Normal text - Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
        layout.addWidget(normal)

        secondary = QLabel("Secondary text - Used for less important information.")
        secondary.setProperty("secondary", "true")
        layout.addWidget(secondary)

        disabled = QLabel("Disabled text - This text is disabled.")
        disabled.setEnabled(False)
        layout.addWidget(disabled)

        # Special text
        code = QLabel("Code: print('Hello, World!')")
        code.setStyleSheet("font-family: monospace; background-color: #f0f0f0; padding: 4px;")
        layout.addWidget(code)

        group.setLayout(layout)
        return group
