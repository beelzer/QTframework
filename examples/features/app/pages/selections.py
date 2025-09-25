"""
Selection controls demonstration page with responsive layout.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
)

from qtframework.layouts import FlowLayout

from .base import DemoPage


class SelectionsPage(DemoPage):
    """Page demonstrating selection components."""

    def __init__(self):
        """Initialize the selections page."""
        super().__init__("Selection Controls")
        self._create_content()

    def _create_content(self):
        """Create the page content."""
        # Dropdowns
        dropdown_group = self._create_dropdowns()
        self.add_section("", dropdown_group)

        # Checkboxes
        checkbox_group = self._create_checkboxes()
        self.add_section("", checkbox_group)

        # Radio buttons
        radio_group = self._create_radio_buttons()
        self.add_section("", radio_group)

        # Sliders
        slider_group = self._create_sliders()
        self.add_section("", slider_group)

        self.add_stretch()

    def _create_dropdowns(self):
        """Create dropdown/combobox examples."""
        group = QGroupBox("Dropdowns")
        layout = QVBoxLayout()

        # Standard dropdown
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Standard:"))
        combo1 = QComboBox()
        combo1.addItems(["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"])
        row1.addWidget(combo1)
        row1.addStretch()
        layout.addLayout(row1)

        # Editable dropdown
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Editable:"))
        combo2 = QComboBox()
        combo2.setEditable(True)
        combo2.addItems(["Suggestion 1", "Suggestion 2", "Suggestion 3"])
        row2.addWidget(combo2)
        row2.addStretch()
        layout.addLayout(row2)

        # Disabled dropdown
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Disabled:"))
        combo3 = QComboBox()
        combo3.addItems(["Disabled Option"])
        combo3.setEnabled(False)
        row3.addWidget(combo3)
        row3.addStretch()
        layout.addLayout(row3)

        group.setLayout(layout)
        return group

    def _create_checkboxes(self):
        """Create checkbox examples with responsive flow layout."""
        group = QGroupBox("Checkboxes")
        layout = FlowLayout(margin=10, h_spacing=15, v_spacing=10)

        check1 = QCheckBox("Unchecked")
        layout.addWidget(check1)

        check2 = QCheckBox("Checked")
        check2.setChecked(True)
        layout.addWidget(check2)

        check3 = QCheckBox("Partial")
        check3.setTristate(True)
        check3.setCheckState(Qt.PartiallyChecked)
        layout.addWidget(check3)

        check4 = QCheckBox("Disabled")
        check4.setEnabled(False)
        layout.addWidget(check4)

        # Add more checkbox examples
        check5 = QCheckBox("Required")
        check5.setStyleSheet("QCheckBox { font-weight: bold; }")
        layout.addWidget(check5)

        check6 = QCheckBox("Optional")
        layout.addWidget(check6)

        group.setLayout(layout)
        return group

    def _create_radio_buttons(self):
        """Create radio button examples with responsive flow layout."""
        group = QGroupBox("Radio Buttons")
        layout = FlowLayout(margin=10, h_spacing=15, v_spacing=10)

        radio_group = QButtonGroup()

        radio1 = QRadioButton("Option 1")
        radio1.setChecked(True)
        radio_group.addButton(radio1)
        layout.addWidget(radio1)

        radio2 = QRadioButton("Option 2")
        radio_group.addButton(radio2)
        layout.addWidget(radio2)

        radio3 = QRadioButton("Option 3")
        radio_group.addButton(radio3)
        layout.addWidget(radio3)

        radio4 = QRadioButton("Disabled")
        radio4.setEnabled(False)
        layout.addWidget(radio4)

        # Add more radio button examples
        radio5 = QRadioButton("Option 4")
        radio_group.addButton(radio5)
        layout.addWidget(radio5)

        radio6 = QRadioButton("Option 5")
        radio_group.addButton(radio6)
        layout.addWidget(radio6)

        group.setLayout(layout)
        return group

    def _create_sliders(self):
        """Create slider examples."""
        group = QGroupBox("Sliders & Spinners")
        layout = QVBoxLayout()

        # Horizontal slider
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Horizontal:"))
        slider1 = QSlider(Qt.Horizontal)
        slider1.setRange(0, 100)
        slider1.setValue(50)
        row1.addWidget(slider1)
        spin1 = QSpinBox()
        spin1.setRange(0, 100)
        spin1.setValue(50)
        slider1.valueChanged.connect(spin1.setValue)
        spin1.valueChanged.connect(slider1.setValue)
        row1.addWidget(spin1)
        layout.addLayout(row1)

        # Vertical slider section
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Vertical:"))
        slider2 = QSlider(Qt.Vertical)
        slider2.setRange(0, 100)
        slider2.setValue(75)
        slider2.setMinimumHeight(100)
        row2.addWidget(slider2)
        row2.addStretch()
        layout.addLayout(row2)

        # Disabled slider
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Disabled:"))
        slider3 = QSlider(Qt.Horizontal)
        slider3.setEnabled(False)
        slider3.setValue(30)
        row3.addWidget(slider3)
        layout.addLayout(row3)

        group.setLayout(layout)
        return group
