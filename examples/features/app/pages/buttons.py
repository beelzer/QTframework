"""
Buttons demonstration page with responsive layout.
"""

from __future__ import annotations

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QPushButton, QToolButton, QVBoxLayout

from qtframework.layouts import FlowLayout

from .base import DemoPage


class ButtonsPage(DemoPage):
    """Page demonstrating button components with responsive flow layout."""

    def __init__(self):
        """Initialize the buttons page."""
        super().__init__("Button Components")
        self._create_content()

    def _create_content(self):
        """Create the page content."""
        # Standard buttons
        standard_group = self._create_standard_buttons()
        self.add_section("", standard_group)

        # Size variants
        size_group = self._create_size_variants()
        self.add_section("", size_group)

        # Icon buttons
        icon_group = self._create_icon_buttons()
        self.add_section("", icon_group)

        self.add_stretch()

    def _create_standard_buttons(self):
        """Create standard button variants with responsive flow layout."""
        group = QGroupBox("Standard Buttons")
        layout = FlowLayout(margin=10, h_spacing=10, v_spacing=10)

        # Primary variants
        layout.addWidget(self._create_button("Default"))
        layout.addWidget(self._create_button("Primary", "primary"))
        layout.addWidget(self._create_button("Success", "success"))
        layout.addWidget(self._create_button("Warning", "warning"))
        layout.addWidget(self._create_button("Danger", "danger"))
        layout.addWidget(self._create_button("Info", "info"))

        # Style variants
        layout.addWidget(self._create_button("Ghost", "ghost"))
        layout.addWidget(self._create_button("Outline", "outline"))
        layout.addWidget(self._create_button("Link", "link"))

        disabled_btn = self._create_button("Disabled")
        disabled_btn.setEnabled(False)
        layout.addWidget(disabled_btn)

        group.setLayout(layout)
        return group

    def _create_size_variants(self):
        """Create size variant buttons with responsive flow layout."""
        group = QGroupBox("Size Variants")
        layout = FlowLayout(margin=10, h_spacing=10, v_spacing=10)

        small_btn = self._create_button("Small")
        small_btn.setProperty("size", "small")
        layout.addWidget(small_btn)

        layout.addWidget(self._create_button("Medium"))

        large_btn = self._create_button("Large")
        large_btn.setProperty("size", "large")
        layout.addWidget(large_btn)

        # Add more examples to show wrapping
        for size in ["Extra Small", "Default", "Extra Large"]:
            btn = self._create_button(size)
            if size == "Extra Small":
                btn.setProperty("size", "xs")
            elif size == "Extra Large":
                btn.setProperty("size", "xl")
            layout.addWidget(btn)

        group.setLayout(layout)
        return group

    def _create_icon_buttons(self):
        """Create icon buttons with responsive flow layout."""
        group = QGroupBox("Icon Buttons")
        layout = FlowLayout(margin=10, h_spacing=10, v_spacing=10)

        # Add more icons to demonstrate wrapping
        icons = ["⚙", "📁", "🔍", "✏️", "🗑️", "⭐", "💾", "📊", "🔔", "🏠", "👤", "📧"]
        for icon in icons:
            btn = QToolButton()
            btn.setText(icon)
            btn.setMinimumSize(40, 40)  # Ensure consistent button size
            layout.addWidget(btn)

        group.setLayout(layout)
        return group

    def _create_button(self, text: str, variant: str = None):
        """Create a styled button."""
        btn = QPushButton(text)
        if variant:
            btn.setProperty("variant", variant)
        return btn
