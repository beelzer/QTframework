"""Quick test for dropdown arrow rendering."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import (QApplication, QComboBox, QLabel, QPushButton,
                               QSpinBox, QVBoxLayout, QWidget)

from qtframework.themes import ThemeManager

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Dropdown Arrow Test")
layout = QVBoxLayout(window)

# Theme selector
theme_manager = ThemeManager(Path(__file__).parent / "resources/themes")
theme_combo = QComboBox()
theme_combo.addItems(theme_manager.list_themes())

def apply_theme(theme_name):
    theme_manager.set_theme(theme_name)
    app.setStyleSheet(theme_manager.get_stylesheet())

theme_combo.currentTextChanged.connect(apply_theme)
layout.addWidget(QLabel("Select Theme:"))
layout.addWidget(theme_combo)

# Test combo box
test_combo = QComboBox()
test_combo.addItems(["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"])
layout.addWidget(QLabel("\nTest ComboBox:"))
layout.addWidget(test_combo)

# Test spin box
spin_box = QSpinBox()
spin_box.setRange(0, 100)
spin_box.setValue(50)
layout.addWidget(QLabel("\nTest SpinBox:"))
layout.addWidget(spin_box)

# Apply initial theme
apply_theme("light")

window.resize(300, 250)
window.show()

sys.exit(app.exec())
