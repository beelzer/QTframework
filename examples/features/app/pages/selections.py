"""
Selection controls demonstration page.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QButtonGroup, QCheckBox, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QRadioButton, QSlider,
                               QVBoxLayout)

from .base import DemoPage


class SelectionsPage(DemoPage):
    """Page demonstrating selection components."""

    def __init__(self):
        """Initialize the selections page."""
        super().__init__("Selection Components")
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
        """Create checkbox examples."""
        group = QGroupBox("Checkboxes")
        layout = QHBoxLayout()

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

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_radio_buttons(self):
        """Create radio button examples."""
        group = QGroupBox("Radio Buttons")
        layout = QHBoxLayout()

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

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_sliders(self):
        """Create slider examples."""
        group = QGroupBox("Sliders")
        layout = QVBoxLayout()

        # Horizontal slider
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Horizontal:"))
        h_slider = QSlider(Qt.Horizontal)
        h_slider.setRange(0, 100)
        h_slider.setValue(50)
        h_slider.setTickPosition(QSlider.TicksBelow)
        h_slider.setTickInterval(10)
        row1.addWidget(h_slider)

        h_value = QLabel("50")
        h_slider.valueChanged.connect(lambda v: h_value.setText(str(v)))
        row1.addWidget(h_value)
        layout.addLayout(row1)

        # Vertical slider
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Vertical:"))
        v_slider = QSlider(Qt.Vertical)
        v_slider.setRange(0, 100)
        v_slider.setValue(75)
        v_slider.setTickPosition(QSlider.TicksLeft)
        v_slider.setTickInterval(10)
        v_slider.setFixedHeight(150)
        row2.addWidget(v_slider)

        v_value = QLabel("75")
        v_slider.valueChanged.connect(lambda v: v_value.setText(str(v)))
        row2.addWidget(v_value)
        row2.addStretch()
        layout.addLayout(row2)

        group.setLayout(layout)
        return group
