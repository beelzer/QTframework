"""
Forms demonstration page.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from .base import DemoPage


class FormsPage(DemoPage):
    """Page demonstrating form components."""

    def __init__(self, form_type: str = "basic"):
        """Initialize the forms page."""
        self.form_type = form_type
        titles = {"basic": "Basic Form", "validation": "Form Validation", "complex": "Complex Form"}
        super().__init__(titles.get(form_type, "Forms"))
        self._create_content()

    def _create_content(self):
        """Create content based on form type."""
        if self.form_type == "basic":
            self._create_basic_form()
        elif self.form_type == "validation":
            self._create_validation_form()
        elif self.form_type == "complex":
            self._create_complex_form()

        self.add_stretch()

    def _create_basic_form(self):
        """Create a basic form."""
        group = QGroupBox("Basic Contact Form")
        layout = QGridLayout()

        # Name field
        layout.addWidget(QLabel("Name:"), 0, 0)
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter your name")
        layout.addWidget(name_input, 0, 1)

        # Email field
        layout.addWidget(QLabel("Email:"), 1, 0)
        email_input = QLineEdit()
        email_input.setPlaceholderText("email@example.com")
        layout.addWidget(email_input, 1, 1)

        # Subject field
        layout.addWidget(QLabel("Subject:"), 2, 0)
        subject_input = QLineEdit()
        subject_input.setPlaceholderText("Message subject")
        layout.addWidget(subject_input, 2, 1)

        # Message field
        layout.addWidget(QLabel("Message:"), 3, 0)
        message_input = QTextEdit()
        message_input.setPlaceholderText("Enter your message...")
        message_input.setMaximumHeight(100)
        layout.addWidget(message_input, 3, 1)

        # Submit button
        submit_btn = QPushButton("Submit")
        submit_btn.setProperty("variant", "primary")
        layout.addWidget(submit_btn, 4, 1)

        group.setLayout(layout)
        self.content_layout.addWidget(group)

    def _create_validation_form(self):
        """Create form with validation examples."""
        group = QGroupBox("Form with Validation")
        layout = QVBoxLayout()

        # Valid field
        valid_layout = QHBoxLayout()
        valid_layout.addWidget(QLabel("Valid Input:"))
        valid_input = QLineEdit()
        valid_input.setText("valid@example.com")
        valid_input.setStyleSheet("border: 2px solid #28a745;")
        valid_layout.addWidget(valid_input)
        layout.addLayout(valid_layout)

        valid_msg = QLabel("✅ Email address is valid")
        valid_msg.setStyleSheet("color: #28a745;")
        layout.addWidget(valid_msg)

        # Invalid field
        invalid_layout = QHBoxLayout()
        invalid_layout.addWidget(QLabel("Invalid Input:"))
        invalid_input = QLineEdit()
        invalid_input.setText("invalid-email")
        invalid_input.setStyleSheet("border: 2px solid #dc3545;")
        invalid_layout.addWidget(invalid_input)
        layout.addLayout(invalid_layout)

        invalid_msg = QLabel("❌ Please enter a valid email address")
        invalid_msg.setStyleSheet("color: #dc3545;")
        layout.addWidget(invalid_msg)

        # Warning field
        warning_layout = QHBoxLayout()
        warning_layout.addWidget(QLabel("Password:"))
        warning_input = QLineEdit()
        warning_input.setEchoMode(QLineEdit.Password)
        warning_input.setText("weak")
        warning_input.setStyleSheet("border: 2px solid #ffc107;")
        warning_layout.addWidget(warning_input)
        layout.addLayout(warning_layout)

        warning_msg = QLabel("⚠️ Password is weak. Consider using a stronger password")
        warning_msg.setStyleSheet("color: #ffc107;")
        layout.addWidget(warning_msg)

        group.setLayout(layout)
        self.content_layout.addWidget(group)

    def _create_complex_form(self):
        """Create a complex registration form."""
        group = QGroupBox("User Registration Form")
        layout = QGridLayout()

        row = 0

        # Section: Personal Information
        layout.addWidget(self._create_section_label("Personal Information"), row, 0, 1, 4)
        row += 1

        layout.addWidget(QLabel("First Name:*"), row, 0)
        first_name = QLineEdit()
        first_name.setPlaceholderText("John")
        layout.addWidget(first_name, row, 1)

        layout.addWidget(QLabel("Last Name:*"), row, 2)
        last_name = QLineEdit()
        last_name.setPlaceholderText("Doe")
        layout.addWidget(last_name, row, 3)
        row += 1

        layout.addWidget(QLabel("Date of Birth:"), row, 0)

        from PySide6.QtWidgets import QDateEdit

        dob = QDateEdit()
        dob.setCalendarPopup(True)
        layout.addWidget(dob, row, 1)

        layout.addWidget(QLabel("Gender:"), row, 2)
        gender = QComboBox()
        gender.addItems(["Select", "Male", "Female", "Other"])
        layout.addWidget(gender, row, 3)
        row += 1

        # Section: Contact Information
        layout.addWidget(self._create_section_label("Contact Information"), row, 0, 1, 4)
        row += 1

        layout.addWidget(QLabel("Email:*"), row, 0)
        email = QLineEdit()
        email.setPlaceholderText("john.doe@example.com")
        layout.addWidget(email, row, 1)

        layout.addWidget(QLabel("Phone:"), row, 2)
        phone = QLineEdit()
        phone.setPlaceholderText("+1 234 567 8900")
        layout.addWidget(phone, row, 3)
        row += 1

        layout.addWidget(QLabel("Address:"), row, 0)
        address = QLineEdit()
        address.setPlaceholderText("123 Main Street")
        layout.addWidget(address, row, 1, 1, 3)
        row += 1

        layout.addWidget(QLabel("City:"), row, 0)
        city = QLineEdit()
        city.setPlaceholderText("New York")
        layout.addWidget(city, row, 1)

        layout.addWidget(QLabel("Country:"), row, 2)
        country = QComboBox()
        country.addItems(["United States", "Canada", "Mexico", "Other"])
        layout.addWidget(country, row, 3)
        row += 1

        # Section: Account Settings
        layout.addWidget(self._create_section_label("Account Settings"), row, 0, 1, 4)
        row += 1

        layout.addWidget(QLabel("Username:*"), row, 0)
        username = QLineEdit()
        username.setPlaceholderText("johndoe")
        layout.addWidget(username, row, 1)

        layout.addWidget(QLabel("Password:*"), row, 2)
        password = QLineEdit()
        password.setEchoMode(QLineEdit.Password)
        password.setPlaceholderText("••••••••")
        layout.addWidget(password, row, 3)
        row += 1

        # Preferences
        layout.addWidget(self._create_section_label("Preferences"), row, 0, 1, 4)
        row += 1

        newsletter = QCheckBox("Subscribe to newsletter")
        layout.addWidget(newsletter, row, 0, 1, 2)

        notifications = QCheckBox("Enable notifications")
        notifications.setChecked(True)
        layout.addWidget(notifications, row, 2, 1, 2)
        row += 1

        # Terms
        terms = QCheckBox("I agree to the Terms and Conditions*")
        layout.addWidget(terms, row, 0, 1, 4)
        row += 1

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(cancel_btn)

        submit_btn = QPushButton("Register")
        submit_btn.setProperty("variant", "primary")
        button_layout.addWidget(submit_btn)

        layout.addLayout(button_layout, row, 0, 1, 4)

        group.setLayout(layout)
        self.content_layout.addWidget(group)

    def _create_section_label(self, text: str):
        """Create a section label."""
        label = QLabel(text)
        label.setProperty("heading", "h3")
        label.setStyleSheet("margin-top: 10px; margin-bottom: 5px;")
        return label
