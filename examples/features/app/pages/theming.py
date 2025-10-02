"""
Theming demonstration page.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
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

from qtframework.layouts import FlowLayout

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

        # Connect to theme changes for live updates
        if self.parent_window and hasattr(self.parent_window, "theme_manager"):
            self.parent_window.theme_manager.theme_changed.connect(self._on_external_theme_change)

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
        # Refresh color palette if this is the palette page
        if self.page_type == "palette":
            self._refresh_color_palette()

    def _refresh_color_palette(self):
        """Refresh the color palette to show current theme colors."""
        # Clear existing widgets
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Recreate the color palette
        self._create_color_palette()
        self.add_stretch()

        # Force layout update
        self.updateGeometry()
        self.update()

    def _on_external_theme_change(self, theme_name: str):
        """Handle theme changes from external sources (menu bar, etc.)."""
        self._refresh_theme_dropdown()
        # Refresh color palette if this is the palette page
        if self.page_type == "palette":
            self._refresh_color_palette()

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
        # Get current theme
        theme = None
        if self.parent_window and hasattr(self.parent_window, "theme_manager"):
            theme = self.parent_window.theme_manager.get_current_theme()

        if theme and theme.tokens:
            semantic = theme.tokens.semantic
            components = theme.tokens.components

            # Main colors section (large swatches with flow layout)
            main_group = QGroupBox("Main Action && Feedback Colors")
            main_layout = FlowLayout()

            main_colors = [
                ("Primary Action", semantic.action_primary, "Primary interactive color"),
                ("Secondary Action", semantic.action_secondary, "Secondary interactive color"),
                ("Success", semantic.feedback_success, "Success feedback color"),
                ("Warning", semantic.feedback_warning, "Warning feedback color"),
                ("Error", semantic.feedback_error, "Error feedback color"),
                ("Info", semantic.feedback_info, "Information feedback color"),
            ]

            for name, color, description in main_colors:
                # Container for each main color item
                container = QWidget()
                container.setStyleSheet("background: transparent;")
                container_layout = QHBoxLayout(container)
                container_layout.setContentsMargins(0, 0, 10, 0)
                container_layout.setSpacing(10)

                # Large color swatch
                swatch = QFrame()
                swatch.setStyleSheet(
                    f"background-color: {color}; border: 1px solid rgba(0,0,0,0.1); border-radius: 4px;"
                )
                swatch.setFixedSize(80, 80)
                container_layout.addWidget(swatch)

                # Color info
                info_widget = QWidget()
                info_widget.setStyleSheet("background: transparent;")
                info_widget.setFixedWidth(150)
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
                desc_label.setWordWrap(True)
                info_layout.addWidget(desc_label)

                info_layout.addStretch()
                container_layout.addWidget(info_widget)

                main_layout.addWidget(container)

            main_group.setLayout(main_layout)
            self.content_layout.addWidget(main_group)

            # Semantic colors
            self._add_color_group(
                "Background Colors",
                [
                    ("Primary", semantic.bg_primary),
                    ("Secondary", semantic.bg_secondary),
                    ("Tertiary", semantic.bg_tertiary),
                    ("Elevated", semantic.bg_elevated),
                    ("Overlay", semantic.bg_overlay),
                ],
            )

            self._add_color_group(
                "Text Colors",
                [
                    ("Primary", semantic.fg_primary),
                    ("Secondary", semantic.fg_secondary),
                    ("Tertiary", semantic.fg_tertiary),
                    ("On Accent", semantic.fg_on_accent),
                    ("On Dark", semantic.fg_on_dark),
                    ("On Light", semantic.fg_on_light),
                ],
            )

            self._add_color_group(
                "Action States",
                [
                    ("Primary", semantic.action_primary),
                    ("Primary Hover", semantic.action_primary_hover),
                    ("Primary Active", semantic.action_primary_active),
                    ("Secondary", semantic.action_secondary),
                    ("Secondary Hover", semantic.action_secondary_hover),
                    ("Secondary Active", semantic.action_secondary_active),
                ],
            )

            self._add_color_group(
                "Border Colors",
                [
                    ("Default", semantic.border_default),
                    ("Subtle", semantic.border_subtle),
                    ("Strong", semantic.border_strong),
                    ("Focus", semantic.border_focus),
                ],
            )

            self._add_color_group(
                "Interaction States",
                [
                    ("Hover", semantic.state_hover),
                    ("Selected", semantic.state_selected),
                    ("Disabled", semantic.state_disabled),
                    ("Focus", semantic.state_focus),
                ],
            )

            # Component colors
            self._add_color_group(
                "Button Colors",
                [
                    ("Primary BG", components.button_primary_bg),
                    ("Primary FG", components.button_primary_fg),
                    ("Primary Border", components.button_primary_border),
                    ("Secondary BG", components.button_secondary_bg),
                    ("Secondary FG", components.button_secondary_fg),
                    ("Secondary Border", components.button_secondary_border),
                ],
            )

            self._add_color_group(
                "Input Colors",
                [
                    ("Background", components.input_bg),
                    ("Text", components.input_fg),
                    ("Border", components.input_border),
                    ("Placeholder", components.input_placeholder),
                ],
            )

            self._add_color_group(
                "Table Colors",
                [
                    ("Header BG", components.table_header_bg),
                    ("Header FG", components.table_header_fg),
                    ("Row BG", components.table_row_bg),
                    ("Row Alt BG", components.table_row_bg_alt),
                    ("Row Hover", components.table_row_hover),
                    ("Row Selected", components.table_row_selected),
                    ("Border", components.table_border),
                ],
            )

            self._add_color_group(
                "Menu Colors",
                [
                    ("Background", components.menu_bg),
                    ("Text", components.menu_fg),
                    ("Hover BG", components.menu_hover_bg),
                    ("Hover FG", components.menu_hover_fg),
                    ("Selected BG", components.menu_selected_bg),
                    ("Selected FG", components.menu_selected_fg),
                ],
            )

            self._add_color_group(
                "Tab Colors",
                [
                    ("Background", components.tab_bg),
                    ("Text", components.tab_fg),
                    ("Active BG", components.tab_active_bg),
                    ("Active FG", components.tab_active_fg),
                    ("Hover BG", components.tab_hover_bg),
                    ("Hover FG", components.tab_hover_fg),
                ],
            )

            self._add_color_group(
                "Scrollbar Colors",
                [
                    ("Background", components.scrollbar_bg),
                    ("Thumb", components.scrollbar_thumb),
                    ("Thumb Hover", components.scrollbar_thumb_hover),
                ],
            )

            self._add_color_group(
                "Chart Colors",
                [
                    ("Series 1", components.chart_1),
                    ("Series 2", components.chart_2),
                    ("Series 3", components.chart_3),
                    ("Series 4", components.chart_4),
                    ("Series 5", components.chart_5),
                    ("Series 6", components.chart_6),
                    ("Grid", components.chart_grid),
                    ("Axis", components.chart_axis),
                ],
            )
        else:
            # Fallback static display
            main_group = QGroupBox("Color Palette")
            placeholder = QLabel("No theme loaded - using application default theme")
            placeholder.setProperty("secondary", "true")
            main_group.layout = QVBoxLayout()
            main_group.layout.addWidget(placeholder)
            self.content_layout.addWidget(main_group)

    def _add_color_group(self, title: str, colors: list[tuple[str, str]]):
        """Add a group of colors with smaller swatches."""
        group = QGroupBox(title)
        layout = FlowLayout()

        for name, color in colors:
            item_widget = QWidget()
            item_widget.setStyleSheet("background: transparent;")
            item_widget.setFixedSize(100, 100)  # Fixed size for flow layout
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(4)

            # Small swatch
            swatch = QFrame()
            swatch.setStyleSheet(
                f"background-color: {color}; border: 1px solid rgba(0,0,0,0.1); border-radius: 3px;"
            )
            swatch.setFixedSize(50, 50)
            item_layout.addWidget(swatch, alignment=Qt.AlignmentFlag.AlignCenter)

            # Name
            name_label = QLabel(name)
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setWordWrap(True)
            item_layout.addWidget(name_label)

            # Color value
            color_label = QLabel(color)
            color_label.setStyleSheet("font-family: monospace; font-size: 10px;")
            color_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item_layout.addWidget(color_label)

            layout.addWidget(item_widget)

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
