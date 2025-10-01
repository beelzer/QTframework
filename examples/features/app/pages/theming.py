"""
Theming demonstration page.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from .base import DemoPage


class ThemingPage(DemoPage):
    """Page demonstrating theming system."""

    def __init__(self, parent_window=None, page_type: str = "switcher"):
        """Initialize the theming page."""
        self.parent_window = parent_window
        self.page_type = page_type

        titles = {
            "switcher": "Theme Switcher",
            "palette": "Color Palette",
            "typography": "Typography System",
        }
        super().__init__(titles.get(page_type, "Theming"))
        self._create_content()

    def _create_content(self):
        """Create content based on page type."""
        if self.page_type == "switcher":
            self._create_theme_switcher()
        elif self.page_type == "palette":
            self._create_color_palette()
        elif self.page_type == "typography":
            self._create_typography()
        else:
            self._create_theme_switcher()

        self.add_stretch()

    def _create_theme_switcher(self):
        """Create theme switcher interface."""
        group = QGroupBox("Theme Selection")
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Current Theme:"))

        self.theme_combo = QComboBox()
        if self.parent_window and hasattr(self.parent_window, "theme_manager"):
            theme_manager = self.parent_window.theme_manager
            theme_names = theme_manager.list_themes()

            # Add themes with display names
            for theme_name in theme_names:
                theme_info = theme_manager.get_theme_info(theme_name)
                display_name = (
                    theme_info.get("display_name", theme_name.replace("_", " ").title())
                    if theme_info
                    else theme_name.replace("_", " ").title()
                )
                self.theme_combo.addItem(display_name, theme_name)  # Store theme_name as data

            # Set current theme as selected
            current_theme = theme_manager.get_current_theme()
            if current_theme:
                for i in range(self.theme_combo.count()):
                    if self.theme_combo.itemData(i) == current_theme:
                        self.theme_combo.setCurrentIndex(i)
                        break

            # Connect to apply theme using the stored data (theme_name)
            self.theme_combo.currentIndexChanged.connect(
                lambda index: self.parent_window.apply_theme(self.theme_combo.itemData(index))
            )

            # Listen for theme changes from other sources (menu bar, etc.)
            theme_manager.theme_changed.connect(self._on_external_theme_change)
        else:
            self.theme_combo.addItems(["Light", "Dark", "Blue", "Green"])

        layout.addWidget(self.theme_combo)

        live_preview = QCheckBox("Live Preview")
        live_preview.setChecked(True)
        layout.addWidget(live_preview)

        layout.addStretch()
        group.setLayout(layout)
        self.content_layout.addWidget(group)

    def page_shown(self):
        """Called when this page is shown in the content area."""
        self._refresh_theme_dropdown()

    def _on_external_theme_change(self, theme_name: str):
        """Handle theme changes from external sources (menu bar, etc.)."""
        self._refresh_theme_dropdown()

    def _refresh_theme_dropdown(self):
        """Refresh the theme dropdown to match current theme."""
        if not hasattr(self, "theme_combo"):
            return

        if not self.parent_window or not hasattr(self.parent_window, "theme_manager"):
            return

        # Block signals to prevent triggering apply_theme again
        self.theme_combo.blockSignals(True)

        # Get current theme
        current_theme = self.parent_window.theme_manager.get_current_theme()
        if current_theme:
            # Update dropdown to match current theme
            for i in range(self.theme_combo.count()):
                if self.theme_combo.itemData(i) == current_theme.name:
                    self.theme_combo.setCurrentIndex(i)
                    break

        # Re-enable signals
        self.theme_combo.blockSignals(False)

    def _create_color_palette(self):
        """Create color palette display."""
        group = QGroupBox("Color Palette")
        layout = QGridLayout()

        colors = [
            ("Primary", "#007bff", "Primary brand color"),
            ("Secondary", "#6c757d", "Secondary brand color"),
            ("Success", "#28a745", "Success state color"),
            ("Warning", "#ffc107", "Warning state color"),
            ("Danger", "#dc3545", "Error state color"),
            ("Info", "#17a2b8", "Information color"),
            ("Light", "#f8f9fa", "Light background"),
            ("Dark", "#343a40", "Dark background"),
            ("Background", "#ffffff", "Default background"),
            ("Surface", "#f5f5f5", "Surface color"),
            ("Text", "#212529", "Primary text"),
            ("Text Secondary", "#6c757d", "Secondary text"),
        ]

        for i, (name, color, description) in enumerate(colors):
            row = i // 3
            col = (i % 3) * 2

            # Color swatch
            swatch = QFrame()
            swatch.setStyleSheet(f"background-color: {color}; border: 1px solid #ddd;")
            swatch.setFixedSize(60, 60)
            layout.addWidget(swatch, row, col)

            # Color info
            info_widget = QWidget()
            info_layout = QVBoxLayout(info_widget)
            info_layout.setContentsMargins(0, 0, 0, 0)

            name_label = QLabel(name)
            name_label.setProperty("heading", "h3")
            info_layout.addWidget(name_label)

            color_label = QLabel(color)
            color_label.setStyleSheet("font-family: monospace;")
            info_layout.addWidget(color_label)

            desc_label = QLabel(description)
            desc_label.setProperty("secondary", "true")
            info_layout.addWidget(desc_label)

            layout.addWidget(info_widget, row, col + 1)

        group.setLayout(layout)
        self.content_layout.addWidget(group)

    def _create_typography(self):
        """Create typography examples."""
        group = QGroupBox("Typography Scale")
        layout = QVBoxLayout()

        typography = [
            ("Display", "48px", "Display text for hero sections"),
            ("Heading 1", "36px", "Page titles"),
            ("Heading 2", "30px", "Section headers"),
            ("Heading 3", "24px", "Subsection headers"),
            ("Heading 4", "20px", "Card titles"),
            ("Body Large", "18px", "Emphasized body text"),
            ("Body", "16px", "Default body text"),
            ("Body Small", "14px", "Secondary text"),
            ("Caption", "12px", "Helper text and captions"),
            ("Overline", "10px", "Overline text"),
        ]

        for name, size, usage in typography:
            item_layout = QHBoxLayout()

            # Example text
            example = QLabel(name)
            if "Heading" in name:
                level = name.split()[-1]
                example.setProperty("heading", f"h{level}")
            elif name == "Display":
                example.setStyleSheet("font-size: 48px; font-weight: bold;")
            elif name == "Body Large":
                example.setStyleSheet("font-size: 18px;")
            elif name == "Body Small":
                example.setStyleSheet("font-size: 14px;")
            elif name == "Caption":
                example.setStyleSheet("font-size: 12px;")
            elif name == "Overline":
                example.setStyleSheet("font-size: 10px; text-transform: uppercase;")

            item_layout.addWidget(example)

            # Size info
            size_label = QLabel(size)
            size_label.setStyleSheet("font-family: monospace; color: #666;")
            item_layout.addWidget(size_label)

            # Usage info
            usage_label = QLabel(usage)
            usage_label.setProperty("secondary", "true")
            item_layout.addWidget(usage_label)

            item_layout.addStretch()
            layout.addLayout(item_layout)

        group.setLayout(layout)
        self.content_layout.addWidget(group)
