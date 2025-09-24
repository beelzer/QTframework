"""
Buttons demonstration page.
"""

from __future__ import annotations

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QPushButton, QToolButton, QVBoxLayout

from .base import DemoPage


class ButtonsPage(DemoPage):
    """Page demonstrating button components."""

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
        """Create standard button variants."""
        group = QGroupBox("Standard Buttons")
        layout = QVBoxLayout()

        # Primary variants
        row1 = QHBoxLayout()
        row1.addWidget(self._create_button("Default"))
        row1.addWidget(self._create_button("Primary", "primary"))
        row1.addWidget(self._create_button("Success", "success"))
        row1.addWidget(self._create_button("Warning", "warning"))
        row1.addWidget(self._create_button("Danger", "danger"))
        row1.addWidget(self._create_button("Info", "info"))
        row1.addStretch()
        layout.addLayout(row1)

        # Style variants
        row2 = QHBoxLayout()
        row2.addWidget(self._create_button("Ghost", "ghost"))
        row2.addWidget(self._create_button("Outline", "outline"))
        row2.addWidget(self._create_button("Link", "link"))

        disabled_btn = self._create_button("Disabled")
        disabled_btn.setEnabled(False)
        row2.addWidget(disabled_btn)

        row2.addStretch()
        layout.addLayout(row2)

        group.setLayout(layout)
        return group

    def _create_size_variants(self):
        """Create size variant buttons."""
        group = QGroupBox("Size Variants")
        layout = QHBoxLayout()

        small_btn = self._create_button("Small")
        small_btn.setProperty("size", "small")
        layout.addWidget(small_btn)

        layout.addWidget(self._create_button("Medium"))

        large_btn = self._create_button("Large")
        large_btn.setProperty("size", "large")
        layout.addWidget(large_btn)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_icon_buttons(self):
        """Create icon buttons."""
        group = QGroupBox("Icon Buttons")
        layout = QHBoxLayout()

        icons = ["⚙", "📁", "🔍", "✏️", "🗑️", "⭐"]
        for icon in icons:
            btn = QToolButton()
            btn.setText(icon)
            layout.addWidget(btn)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_button(self, text: str, variant: str = None):
        """Create a styled button."""
        btn = QPushButton(text)
        if variant:
            btn.setProperty("variant", variant)
        return btn
