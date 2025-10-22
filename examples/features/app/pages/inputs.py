"""Input controls demonstration page."""

from __future__ import annotations

import math
from datetime import datetime

from PySide6.QtWidgets import (
    QDateEdit,
    QDateTimeEdit,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
)

from qtframework.widgets import ScrollablePage as DemoPage


class InputsPage(DemoPage):
    """Page demonstrating input components."""

    def __init__(self):
        """Initialize the inputs page."""
        super().__init__("Input Components")
        self._create_content()

    def _create_content(self):
        """Create the page content."""
        # Text inputs
        text_group = self._create_text_inputs()
        self.add_section("", text_group)

        # Number inputs
        number_group = self._create_number_inputs()
        self.add_section("", number_group)

        # Date/Time inputs
        datetime_group = self._create_datetime_inputs()
        self.add_section("", datetime_group)

        # Text area
        textarea_group = self._create_text_area()
        self.add_section("", textarea_group)

        self.add_stretch()

    def _create_text_inputs(self):
        """Create text input fields."""
        group = QGroupBox("Text Inputs")
        layout = QGridLayout()

        # Standard text input
        layout.addWidget(QLabel("Text Input:"), 0, 0)
        text_input = QLineEdit()
        text_input.setPlaceholderText("Enter text...")
        layout.addWidget(text_input, 0, 1)

        # Password input
        layout.addWidget(QLabel("Password:"), 1, 0)
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setPlaceholderText("Enter password...")
        layout.addWidget(password_input, 1, 1)

        # Email input
        layout.addWidget(QLabel("Email:"), 2, 0)
        email_input = QLineEdit()
        email_input.setPlaceholderText("user@example.com")
        layout.addWidget(email_input, 2, 1)

        # Search input
        layout.addWidget(QLabel("Search:"), 3, 0)
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search...")
        layout.addWidget(search_input, 3, 1)

        group.setLayout(layout)
        return group

    def _create_number_inputs(self):
        """Create number input fields."""
        group = QGroupBox("Number Inputs")
        layout = QGridLayout()

        # Integer spin box
        layout.addWidget(QLabel("Integer:"), 0, 0)
        spin_box = QSpinBox()
        spin_box.setRange(0, 100)
        spin_box.setValue(42)
        layout.addWidget(spin_box, 0, 1)

        # Double spin box
        layout.addWidget(QLabel("Decimal:"), 1, 0)
        double_spin = QDoubleSpinBox()
        double_spin.setRange(0.0, 100.0)
        double_spin.setValue(math.pi)
        double_spin.setDecimals(3)
        layout.addWidget(double_spin, 1, 1)

        # Percentage
        layout.addWidget(QLabel("Percentage:"), 2, 0)
        percent_spin = QSpinBox()
        percent_spin.setRange(0, 100)
        percent_spin.setSuffix("%")
        percent_spin.setValue(75)
        layout.addWidget(percent_spin, 2, 1)

        group.setLayout(layout)
        return group

    def _create_datetime_inputs(self):
        """Create date and time input fields."""
        group = QGroupBox("Date & Time Inputs")
        layout = QGridLayout()

        # Date edit
        layout.addWidget(QLabel("Date:"), 0, 0)
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(datetime.now().date())
        layout.addWidget(date_edit, 0, 1)

        # Time edit
        layout.addWidget(QLabel("Time:"), 1, 0)
        time_edit = QTimeEdit()
        time_edit.setTime(datetime.now().time())
        layout.addWidget(time_edit, 1, 1)

        # DateTime edit
        layout.addWidget(QLabel("DateTime:"), 2, 0)
        datetime_edit = QDateTimeEdit()
        datetime_edit.setCalendarPopup(True)
        datetime_edit.setDateTime(datetime.now())
        layout.addWidget(datetime_edit, 2, 1)

        group.setLayout(layout)
        return group

    def _create_text_area(self):
        """Create text area field."""
        group = QGroupBox("Text Area")
        layout = QVBoxLayout()

        text_area = QTextEdit()
        text_area.setPlaceholderText("Enter multiple lines of text...")
        text_area.setMaximumHeight(150)
        layout.addWidget(text_area)

        group.setLayout(layout)
        return group
