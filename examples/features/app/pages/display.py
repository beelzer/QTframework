"""
Display elements demonstration page with responsive layout.
"""

from __future__ import annotations

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout

from qtframework.layouts import FlowLayout
from qtframework.widgets import Badge, BadgeVariant, CountBadge

from qtframework.widgets import ScrollablePage as DemoPage


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

        # Status/Label badges
        badges_group = self._create_badges()
        self.add_section("", badges_group)

        # Notification count badges
        count_badges_group = self._create_count_badges()
        self.add_section("", count_badges_group)

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

    def _create_badges(self):
        """Create badge examples with responsive flow layout."""
        group = QGroupBox("Status Badges")
        layout = FlowLayout(margin=10, h_spacing=10, v_spacing=10)

        # Create badges with different variants
        badges = [
            ("Default", BadgeVariant.DEFAULT),
            ("Primary", BadgeVariant.PRIMARY),
            ("Secondary", BadgeVariant.SECONDARY),
            ("Success", BadgeVariant.SUCCESS),
            ("Warning", BadgeVariant.WARNING),
            ("Danger", BadgeVariant.DANGER),
            ("Info", BadgeVariant.INFO),
            ("Light", BadgeVariant.LIGHT),
            ("Dark", BadgeVariant.DARK),
        ]

        for text, variant in badges:
            badge = Badge(text, variant)
            layout.addWidget(badge)

        group.setLayout(layout)
        return group

    def _create_count_badges(self):
        """Create count/notification badge examples."""
        group = QGroupBox("Notification Badges")
        layout = FlowLayout(margin=10, h_spacing=10, v_spacing=10)

        # Create count badges - these are now visually distinct, compact circles/pills
        counts = [
            (1, BadgeVariant.DANGER),  # Single digit - circular
            (5, BadgeVariant.PRIMARY),
            (23, BadgeVariant.SUCCESS),  # Double digit - oval
            (99, BadgeVariant.WARNING),
            (150, BadgeVariant.DANGER),  # Will show as 99+ - pill shaped
            (1234, BadgeVariant.INFO),  # Will show as 99+
        ]

        for count, variant in counts:
            count_badge = CountBadge(count, variant)
            layout.addWidget(count_badge)

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
