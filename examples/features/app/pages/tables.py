"""
Tables demonstration page.
"""

from __future__ import annotations

from PySide6.QtWidgets import QPushButton, QTableWidget, QTableWidgetItem

from .base import DemoPage


class TablesPage(DemoPage):
    """Page demonstrating table components."""

    def __init__(self):
        """Initialize the tables page."""
        super().__init__("Table Components")
        self._create_content()

    def _create_content(self):
        """Create the page content."""
        # Basic table
        self.add_section("Basic Table", self._create_basic_table())

        # Table with actions
        self.add_section("Table with Actions", self._create_action_table())

        self.add_stretch()

    def _create_basic_table(self):
        """Create a basic table."""
        table = QTableWidget(5, 4)
        table.setHorizontalHeaderLabels(["Name", "Age", "City", "Status"])
        table.setAlternatingRowColors(True)

        # Sample data
        data = [
            ["John Doe", "30", "New York", "Active"],
            ["Jane Smith", "25", "Los Angeles", "Active"],
            ["Bob Johnson", "35", "Chicago", "Inactive"],
            ["Alice Brown", "28", "Houston", "Active"],
            ["Charlie Wilson", "32", "Phoenix", "Pending"],
        ]

        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                table.setItem(row, col, item)

        return table

    def _create_action_table(self):
        """Create a table with action buttons."""
        table = QTableWidget(5, 5)
        table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Role", "Actions"])
        table.setAlternatingRowColors(True)

        # Sample data
        data = [
            ["001", "Admin User", "admin@example.com", "Administrator"],
            ["002", "Editor User", "editor@example.com", "Editor"],
            ["003", "Viewer User", "viewer@example.com", "Viewer"],
            ["004", "Guest User", "guest@example.com", "Guest"],
            ["005", "Test User", "test@example.com", "Tester"],
        ]

        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                table.setItem(row, col, item)

            # Add action buttons
            actions_widget = self._create_action_buttons()
            table.setCellWidget(row, 4, actions_widget)

        return table

    def _create_action_buttons(self):
        """Create action buttons for table rows."""
        from PySide6.QtWidgets import QHBoxLayout, QWidget

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 0, 4, 0)

        edit_btn = QPushButton("Edit")
        edit_btn.setProperty("variant", "link")
        layout.addWidget(edit_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setProperty("variant", "link")
        layout.addWidget(delete_btn)

        return widget
