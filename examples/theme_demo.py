"""Demo application showcasing the modern theming system."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
                               QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                               QListWidget, QMainWindow, QMenu, QMenuBar,
                               QMessageBox, QProgressBar, QPushButton,
                               QRadioButton, QSlider, QStatusBar, QTableWidget,
                               QTableWidgetItem, QTabWidget, QTextEdit,
                               QToolBar, QVBoxLayout, QWidget)

from qtframework.themes import ThemeManager


class ThemeShowcase(QMainWindow):
    """Main window showcasing theme components."""

    def __init__(self):
        """Initialize the showcase window."""
        super().__init__()
        self.theme_manager = ThemeManager(Path(__file__).parent.parent / "resources/themes")
        self.init_ui()
        self.apply_theme("light")

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Qt Framework - Modern Theming Demo")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Theme selector
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Select Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.theme_manager.list_themes())
        self.theme_combo.currentTextChanged.connect(self.apply_theme)

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        main_layout.addLayout(theme_layout)

        # Create tabs for different component groups
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # Basic controls tab
        tabs.addTab(self.create_basic_controls(), "Basic Controls")

        # Advanced controls tab
        tabs.addTab(self.create_advanced_controls(), "Advanced Controls")

        # Tables and lists tab
        tabs.addTab(self.create_tables_lists(), "Tables & Lists")

        # Status and feedback tab
        tabs.addTab(self.create_status_feedback(), "Status & Feedback")

        # Menu bar
        self.create_menu_bar()

        # Tool bar
        self.create_tool_bar()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Theme system demo")

    def create_basic_controls(self):
        """Create basic control widgets."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Buttons section
        button_group = QGroupBox("Buttons")
        button_layout = QHBoxLayout()

        # Primary button
        primary_btn = QPushButton("Primary")
        primary_btn.setProperty("variant", "primary")
        button_layout.addWidget(primary_btn)

        # Secondary button
        secondary_btn = QPushButton("Secondary")
        button_layout.addWidget(secondary_btn)

        # Success button
        success_btn = QPushButton("Success")
        success_btn.setProperty("variant", "success")
        button_layout.addWidget(success_btn)

        # Warning button
        warning_btn = QPushButton("Warning")
        warning_btn.setProperty("variant", "warning")
        button_layout.addWidget(warning_btn)

        # Danger button
        danger_btn = QPushButton("Danger")
        danger_btn.setProperty("variant", "danger")
        button_layout.addWidget(danger_btn)

        # Info button
        info_btn = QPushButton("Info")
        info_btn.setProperty("variant", "info")
        button_layout.addWidget(info_btn)

        # Ghost button
        ghost_btn = QPushButton("Ghost")
        ghost_btn.setProperty("variant", "ghost")
        button_layout.addWidget(ghost_btn)

        # Outline button
        outline_btn = QPushButton("Outline")
        outline_btn.setProperty("variant", "outline")
        button_layout.addWidget(outline_btn)

        # Disabled button
        disabled_btn = QPushButton("Disabled")
        disabled_btn.setEnabled(False)
        button_layout.addWidget(disabled_btn)

        button_group.setLayout(button_layout)
        layout.addWidget(button_group)

        # Input controls section
        input_group = QGroupBox("Input Controls")
        input_layout = QVBoxLayout()

        # Text input
        input_h_layout1 = QHBoxLayout()
        input_h_layout1.addWidget(QLabel("Text Input:"))
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Enter text here...")
        input_h_layout1.addWidget(line_edit)
        input_layout.addLayout(input_h_layout1)

        # Combo box
        input_h_layout2 = QHBoxLayout()
        input_h_layout2.addWidget(QLabel("Dropdown:"))
        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3", "Option 4"])
        input_h_layout2.addWidget(combo)
        input_layout.addLayout(input_h_layout2)

        # Checkboxes and Radio buttons
        input_h_layout3 = QHBoxLayout()
        check1 = QCheckBox("Checkbox 1")
        check2 = QCheckBox("Checkbox 2")
        check2.setChecked(True)
        radio1 = QRadioButton("Radio 1")
        radio2 = QRadioButton("Radio 2")
        radio1.setChecked(True)

        input_h_layout3.addWidget(check1)
        input_h_layout3.addWidget(check2)
        input_h_layout3.addWidget(radio1)
        input_h_layout3.addWidget(radio2)
        input_h_layout3.addStretch()
        input_layout.addLayout(input_h_layout3)

        # Slider
        input_h_layout4 = QHBoxLayout()
        input_h_layout4.addWidget(QLabel("Slider:"))
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(50)
        input_h_layout4.addWidget(slider)
        input_layout.addLayout(input_h_layout4)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Text areas
        text_group = QGroupBox("Text Areas")
        text_layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Multi-line text editor...")
        text_edit.setMaximumHeight(150)
        text_layout.addWidget(text_edit)
        text_group.setLayout(text_layout)
        layout.addWidget(text_group)

        layout.addStretch()
        return widget

    def create_advanced_controls(self):
        """Create advanced control widgets."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Typography examples
        typo_group = QGroupBox("Typography")
        typo_layout = QVBoxLayout()

        h1 = QLabel("Heading 1")
        h1.setProperty("heading", "h1")
        typo_layout.addWidget(h1)

        h2 = QLabel("Heading 2")
        h2.setProperty("heading", "h2")
        typo_layout.addWidget(h2)

        h3 = QLabel("Heading 3")
        h3.setProperty("heading", "h3")
        typo_layout.addWidget(h3)

        normal_text = QLabel("Normal text - Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
        typo_layout.addWidget(normal_text)

        secondary_text = QLabel("Secondary text - Used for less important information.")
        secondary_text.setProperty("secondary", "true")
        typo_layout.addWidget(secondary_text)

        disabled_text = QLabel("Disabled text - This text is disabled.")
        disabled_text.setProperty("disabled", "true")
        typo_layout.addWidget(disabled_text)

        typo_group.setLayout(typo_layout)
        layout.addWidget(typo_group)

        # Cards/Frames
        card_group = QGroupBox("Cards & Frames")
        card_layout = QHBoxLayout()

        # Card 1
        card1 = QFrame()
        card1.setProperty("card", "true")
        card1_layout = QVBoxLayout(card1)
        card1_layout.addWidget(QLabel("Card Title"))
        card1_layout.addWidget(QLabel("Card content goes here.\nSupports multiple lines."))
        card1_layout.addWidget(QPushButton("Action"))
        card_layout.addWidget(card1)

        # Card 2
        card2 = QFrame()
        card2.setProperty("card", "true")
        card2_layout = QVBoxLayout(card2)
        card2_layout.addWidget(QLabel("Another Card"))
        card2_layout.addWidget(QLabel("Different content here."))
        primary_btn = QPushButton("Primary Action")
        primary_btn.setProperty("variant", "primary")
        card2_layout.addWidget(primary_btn)
        card_layout.addWidget(card2)

        card_group.setLayout(card_layout)
        layout.addWidget(card_group)

        layout.addStretch()
        return widget

    def create_tables_lists(self):
        """Create table and list widgets."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Table
        table_group = QGroupBox("Table")
        table_layout = QVBoxLayout()

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
                table.setItem(row, col, QTableWidgetItem(value))

        table_layout.addWidget(table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # List
        list_group = QGroupBox("List")
        list_layout = QVBoxLayout()

        list_widget = QListWidget()
        list_widget.addItems([
            "List Item 1",
            "List Item 2",
            "List Item 3 - Selected",
            "List Item 4",
            "List Item 5",
            "List Item 6",
        ])
        list_widget.setCurrentRow(2)

        list_layout.addWidget(list_widget)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)

        return widget

    def create_status_feedback(self):
        """Create status and feedback widgets."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Progress bars
        progress_group = QGroupBox("Progress Indicators")
        progress_layout = QVBoxLayout()

        # Normal progress
        progress1 = QProgressBar()
        progress1.setValue(75)
        progress_layout.addWidget(QLabel("Normal Progress:"))
        progress_layout.addWidget(progress1)

        # Indeterminate progress
        progress2 = QProgressBar()
        progress2.setRange(0, 0)
        progress_layout.addWidget(QLabel("Indeterminate Progress:"))
        progress_layout.addWidget(progress2)

        # Animated progress
        self.animated_progress = QProgressBar()
        self.animated_progress.setRange(0, 100)
        progress_layout.addWidget(QLabel("Animated Progress:"))
        progress_layout.addWidget(self.animated_progress)

        # Timer for animation
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(100)
        self.progress_value = 0

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # Message buttons
        message_group = QGroupBox("Messages & Dialogs")
        message_layout = QHBoxLayout()

        info_btn = QPushButton("Show Info")
        info_btn.clicked.connect(lambda: QMessageBox.information(self, "Information", "This is an info message"))
        message_layout.addWidget(info_btn)

        warning_btn = QPushButton("Show Warning")
        warning_btn.clicked.connect(lambda: QMessageBox.warning(self, "Warning", "This is a warning message"))
        message_layout.addWidget(warning_btn)

        error_btn = QPushButton("Show Error")
        error_btn.clicked.connect(lambda: QMessageBox.critical(self, "Error", "This is an error message"))
        message_layout.addWidget(error_btn)

        question_btn = QPushButton("Show Question")
        question_btn.clicked.connect(lambda: QMessageBox.question(self, "Question", "Do you want to proceed?"))
        message_layout.addWidget(question_btn)

        message_group.setLayout(message_layout)
        layout.addWidget(message_group)

        layout.addStretch()
        return widget

    def create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New")
        file_menu.addAction("Open")
        file_menu.addAction("Save")
        file_menu.addSeparator()
        file_menu.addAction("Exit")

        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")
        edit_menu.addSeparator()
        edit_menu.addAction("Cut")
        edit_menu.addAction("Copy")
        edit_menu.addAction("Paste")

        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Zoom In")
        view_menu.addAction("Zoom Out")
        view_menu.addAction("Reset Zoom")

        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("Documentation")
        help_menu.addAction("About")

    def create_tool_bar(self):
        """Create tool bar."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        toolbar.addAction("New")
        toolbar.addAction("Open")
        toolbar.addAction("Save")
        toolbar.addSeparator()
        toolbar.addAction("Cut")
        toolbar.addAction("Copy")
        toolbar.addAction("Paste")
        toolbar.addSeparator()
        toolbar.addAction("Undo")
        toolbar.addAction("Redo")

    def update_progress(self):
        """Update animated progress bar."""
        self.progress_value = (self.progress_value + 2) % 101
        self.animated_progress.setValue(self.progress_value)

    def apply_theme(self, theme_name: str):
        """Apply selected theme to the application."""
        if self.theme_manager.set_theme(theme_name):
            stylesheet = self.theme_manager.get_stylesheet()
            QApplication.instance().setStyleSheet(stylesheet)
            self.status_bar.showMessage(f"Applied theme: {theme_name}")


def main():
    """Run the demo application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Qt Framework Theme Demo")

    window = ThemeShowcase()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
