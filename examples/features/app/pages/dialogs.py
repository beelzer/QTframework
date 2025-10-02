"""
Dialogs demonstration page.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QColorDialog,
    QFileDialog,
    QFontDialog,
    QGroupBox,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
)

from qtframework.widgets import ScrollablePage as DemoPage


class DialogsPage(DemoPage):
    """Page demonstrating dialog components."""

    def __init__(self, parent_window=None):
        """Initialize the dialogs page."""
        super().__init__("Dialog Components")
        self.parent_window = parent_window
        self._create_content()

    def _create_content(self):
        """Create the page content."""
        # Message dialogs
        message_group = self._create_message_dialogs()
        self.add_section("", message_group)

        # System dialogs
        system_group = self._create_system_dialogs()
        self.add_section("", system_group)

        self.add_stretch()

    def _create_message_dialogs(self):
        """Create message dialog buttons."""
        group = QGroupBox("Message Dialogs")
        layout = QHBoxLayout()

        info_btn = QPushButton("Information")
        info_btn.clicked.connect(self._show_info)
        layout.addWidget(info_btn)

        warning_btn = QPushButton("Warning")
        warning_btn.setProperty("variant", "warning")
        warning_btn.clicked.connect(self._show_warning)
        layout.addWidget(warning_btn)

        error_btn = QPushButton("Error")
        error_btn.setProperty("variant", "danger")
        error_btn.clicked.connect(self._show_error)
        layout.addWidget(error_btn)

        question_btn = QPushButton("Question")
        question_btn.setProperty("variant", "info")
        question_btn.clicked.connect(self._show_question)
        layout.addWidget(question_btn)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _create_system_dialogs(self):
        """Create system dialog buttons."""
        group = QGroupBox("System Dialogs")
        layout = QHBoxLayout()

        file_btn = QPushButton("File Dialog")
        file_btn.clicked.connect(self._show_file_dialog)
        layout.addWidget(file_btn)

        folder_btn = QPushButton("Folder Dialog")
        folder_btn.clicked.connect(self._show_folder_dialog)
        layout.addWidget(folder_btn)

        color_btn = QPushButton("Color Dialog")
        color_btn.clicked.connect(self._show_color_dialog)
        layout.addWidget(color_btn)

        font_btn = QPushButton("Font Dialog")
        font_btn.clicked.connect(self._show_font_dialog)
        layout.addWidget(font_btn)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def _show_info(self):
        """Show information dialog."""
        QMessageBox.information(
            self.parent_window or self,
            "Information",
            "This is an informational message.\n\nIt provides helpful details to the user.",
        )

    def _show_warning(self):
        """Show warning dialog."""
        QMessageBox.warning(
            self.parent_window or self,
            "Warning",
            "This is a warning message.\n\nPlease proceed with caution.",
        )

    def _show_error(self):
        """Show error dialog."""
        QMessageBox.critical(
            self.parent_window or self,
            "Error",
            "This is an error message.\n\nSomething went wrong!",
        )

    def _show_question(self):
        """Show question dialog."""
        result = QMessageBox.question(
            self.parent_window or self,
            "Question",
            "Do you want to continue?\n\nThis action cannot be undone.",
        )
        if result == QMessageBox.Yes:
            QMessageBox.information(self.parent_window or self, "Result", "You selected: Yes")

    def _show_file_dialog(self):
        """Show file dialog."""
        filename, _ = QFileDialog.getOpenFileName(
            self.parent_window or self,
            "Select File",
            "",
            "All Files (*);;Python Files (*.py);;Text Files (*.txt)",
        )
        if filename:
            QMessageBox.information(
                self.parent_window or self, "File Selected", f"You selected:\n{filename}"
            )

    def _show_folder_dialog(self):
        """Show folder dialog."""
        folder = QFileDialog.getExistingDirectory(self.parent_window or self, "Select Folder")
        if folder:
            QMessageBox.information(
                self.parent_window or self, "Folder Selected", f"You selected:\n{folder}"
            )

    def _show_color_dialog(self):
        """Show color dialog."""
        color = QColorDialog.getColor(Qt.white, self.parent_window or self, "Select Color")
        if color.isValid():
            QMessageBox.information(
                self.parent_window or self, "Color Selected", f"You selected:\n{color.name()}"
            )

    def _show_font_dialog(self):
        """Show font dialog."""
        from PySide6.QtGui import QFont

        font, ok = QFontDialog.getFont(QFont(), self.parent_window or self, "Select Font")
        if ok:
            QMessageBox.information(
                self.parent_window or self,
                "Font Selected",
                f"You selected:\n{font.family()}, {font.pointSize()}pt",
            )
