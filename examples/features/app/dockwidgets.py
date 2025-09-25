"""
Dock widgets configuration for the showcase.
"""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class DynamicScrollArea(QScrollArea):
    """Custom scroll area that dynamically adjusts content margins for scrollbar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._adjustment_timer = QTimer()
        self._adjustment_timer.setSingleShot(True)
        self._adjustment_timer.timeout.connect(self._do_adjust_margins)

        # Install event filter on vertical scrollbar to catch visibility changes
        v_bar = self.verticalScrollBar()
        if v_bar:
            v_bar.installEventFilter(self)

    def resizeEvent(self, event):
        """Handle resize events to adjust for scrollbar visibility."""
        super().resizeEvent(event)
        # Debounce the adjustment to avoid too many calls
        self._adjustment_timer.stop()
        self._adjustment_timer.start(10)

    def showEvent(self, event):
        """Handle show events to adjust margins."""
        super().showEvent(event)
        self._adjustment_timer.start(10)

    def setWidget(self, widget):
        """Override setWidget to trigger adjustment when content changes."""
        super().setWidget(widget)
        if widget:
            # Connect to layout changes
            self._adjustment_timer.start(10)

    def _do_adjust_margins(self):
        """Actually perform the margin adjustment."""
        widget = self.widget()
        if not widget or not widget.layout():
            return

        # Get the vertical scrollbar
        v_bar = self.verticalScrollBar()
        if not v_bar:
            return

        # Check actual scrollbar visibility (more reliable than calculating)
        scrollbar_visible = v_bar.isVisible()

        # Get current margins
        margins = widget.layout().contentsMargins()
        current_right_margin = margins.right()

        if scrollbar_visible:
            # Get actual scrollbar width
            scrollbar_width = v_bar.width()
            # Add a small extra buffer (2-3px) to prevent any overlap
            target_right_margin = 10 + scrollbar_width + 3
        else:
            # No scrollbar, use base margin
            target_right_margin = 10

        # Only update if margin needs to change
        if current_right_margin != target_right_margin:
            widget.layout().setContentsMargins(
                margins.left(), margins.top(), target_right_margin, margins.bottom()
            )
            # Force a layout update to apply changes immediately
            widget.layout().update()

    def _adjust_content_margins(self):
        """Public method to trigger margin adjustment."""
        self._adjustment_timer.start(10)

    def eventFilter(self, watched, event):
        """Filter events to catch scrollbar visibility changes."""
        from PySide6.QtCore import QEvent

        if watched == self.verticalScrollBar():
            if event.type() in (QEvent.Show, QEvent.Hide):
                # Scrollbar visibility changed, adjust margins
                self._adjustment_timer.start(10)
        return super().eventFilter(watched, event)


def create_dock_widgets(window):
    """Create dock widgets for the application."""
    # Properties dock
    properties_dock = _create_properties_dock(window)
    window.addDockWidget(Qt.RightDockWidgetArea, properties_dock)

    # Output dock
    output_dock = _create_output_dock(window)
    window.addDockWidget(Qt.BottomDockWidgetArea, output_dock)


def _create_properties_dock(window):
    """Create the properties dock widget."""
    dock = QDockWidget("Properties", window)
    widget = QWidget()
    layout = QVBoxLayout(widget)

    # Title
    title_label = QLabel("Component Properties")
    title_label.setProperty("heading", "h3")
    layout.addWidget(title_label)

    # Create scrollable area for properties using our custom class
    scroll = DynamicScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(
        Qt.ScrollBarAlwaysOff
    )  # No horizontal scrollbar needed with wrapping
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    # Style the scroll area to ensure proper content visibility
    scroll.setStyleSheet("""
        QScrollArea {
            border: none;
        }
        QScrollBar:vertical {
            background: palette(mid);
            width: 12px;
            margin: 0;
        }
    """)

    # Store reference to scroll area for updates
    window.properties_scroll = scroll

    # Properties content widget - will be created in _update_properties
    window.properties_content = None
    window.properties_layout = None

    # Default content
    _update_properties(window, "Buttons", "Core component for user interactions")

    layout.addWidget(scroll)

    dock.setWidget(widget)
    return dock


def _create_output_dock(window):
    """Create the output dock widget."""
    dock = QDockWidget("Output", window)

    window.output_text = QTextEdit()
    window.output_text.setReadOnly(True)
    window.output_text.setMaximumHeight(150)

    # Add initial message
    timestamp = datetime.now().strftime("%H:%M:%S")
    window.output_text.append(f"[{timestamp}] Application started successfully")

    dock.setWidget(window.output_text)
    return dock


def log_output(window, message: str):
    """Log a message to the output panel."""
    if hasattr(window, "output_text"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        window.output_text.append(f"[{timestamp}] {message}")


def _update_properties(window, component_name: str, description: str = ""):
    """Update the properties panel with component information."""
    if not hasattr(window, "properties_scroll"):
        return

    # Create a completely new content widget
    new_content = QWidget()
    new_layout = QVBoxLayout(new_content)

    # Set normal margins - we'll adjust dynamically for scrollbar
    new_layout.setContentsMargins(10, 10, 10, 10)  # left, top, right, bottom

    # Store references
    window.properties_content = new_content
    window.properties_layout = new_layout
    window.current_code_display = None

    # Component name
    name_label = QLabel(f"Component: {component_name}")
    name_label.setStyleSheet("font-weight: bold;")
    new_layout.addWidget(name_label)

    # Description
    if description:
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setProperty("secondary", "true")
        new_layout.addWidget(desc_label)

    # Add separator
    from PySide6.QtWidgets import QFrame

    separator = QFrame()
    separator.setFrameShape(QFrame.HLine)
    separator.setFrameShadow(QFrame.Sunken)
    new_layout.addWidget(separator)

    # Component-specific properties
    properties = _get_component_properties(component_name)

    if properties:
        props_label = QLabel("Properties:")
        props_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        new_layout.addWidget(props_label)

        for prop_name, prop_value in properties.items():
            prop_layout = QHBoxLayout()
            prop_layout.setContentsMargins(0, 2, 0, 2)  # Small vertical spacing
            prop_name_label = QLabel(f"{prop_name}:")
            prop_name_label.setMinimumWidth(100)
            prop_name_label.setMaximumWidth(100)
            prop_name_label.setAlignment(Qt.AlignTop)
            prop_value_label = QLabel(str(prop_value))
            prop_value_label.setProperty("secondary", "true")
            prop_value_label.setWordWrap(True)  # Enable word wrapping for long values
            prop_value_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            prop_layout.addWidget(prop_name_label)
            prop_layout.addWidget(prop_value_label, 1)  # Give it stretch factor
            prop_layout.setSpacing(10)

            prop_widget = QWidget()
            prop_widget.setLayout(prop_layout)
            new_layout.addWidget(prop_widget)

    # Usage example
    usage = _get_usage_example(component_name)
    if usage:
        usage_label = QLabel("Usage Example:")
        usage_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        new_layout.addWidget(usage_label)

        # Use the CodeDisplay widget for syntax highlighting
        from .widgets import CodeDisplay

        code_display = CodeDisplay(usage, "python")
        new_layout.addWidget(code_display)

        # Store reference for theme updates
        window.current_code_display = code_display

    new_layout.addStretch()

    # Set the new widget in the scroll area
    # This completely replaces the old widget and forces proper recalculation
    window.properties_scroll.setWidget(new_content)

    # Trigger margin adjustment after content change
    if isinstance(window.properties_scroll, DynamicScrollArea):
        QTimer.singleShot(10, window.properties_scroll._adjust_content_margins)


def _get_component_properties(component_name: str) -> dict:
    """Get properties for a specific component."""
    properties_map = {
        "Buttons": {
            "Variants": "primary, success, warning, danger, info, ghost, outline, link",
            "Sizes": "small, medium, large",
            "States": "normal, hover, pressed, disabled",
            "Events": "clicked, pressed, released",
        },
        "Inputs": {
            "Types": "text, password, email, number, date, time",
            "Validation": "required, min/max length, pattern",
            "Events": "textChanged, editingFinished, returnPressed",
        },
        "Tables": {
            "Features": "sorting, filtering, pagination, selection",
            "Rows": "alternating colors, hover effects",
            "Columns": "resizable, reorderable, sortable",
        },
        "Dialogs": {
            "Types": "information, warning, error, question",
            "Buttons": "OK, Cancel, Yes, No, Apply",
            "Modal": "true/false",
        },
        "Theme Switcher": {
            "Themes": "light, dark, blue, green",
            "Live Preview": "enabled",
            "Custom": "supported via JSON",
        },
        "State Demo": {
            "Pattern": "Redux-like",
            "Actions": "INCREMENT, DECREMENT, RESET",
            "History": "last 10 actions",
        },
        "Animations": {
            "Types": "fade, slide, scale, rotate",
            "Easing": "linear, ease-in, ease-out, bounce",
            "Duration": "customizable",
        },
    }

    return properties_map.get(component_name, {})


def _get_usage_example(component_name: str) -> str:
    """Get usage example for a specific component."""
    examples = {
        "Buttons": "btn = QPushButton('Click me')\nbtn.setProperty('variant', 'primary')\nbtn.clicked.connect(handler)",
        "Inputs": "input = QLineEdit()\ninput.setPlaceholderText('Enter text')\ninput.textChanged.connect(on_change)",
        "Tables": "table = QTableWidget(5, 3)\ntable.setHorizontalHeaderLabels(['Name', 'Age', 'City'])\ntable.setAlternatingRowColors(True)",
        "Dialogs": "QMessageBox.information(self, 'Title', 'Message')",
        "Theme Switcher": "theme_manager.set_theme('dark')\nstylesheet = theme_manager.get_stylesheet()\napp.setStyleSheet(stylesheet)",
        "State Demo": "store.dispatch(Action(type='INCREMENT'))\nstate = store.get_state()",
        "Animations": "animation = QPropertyAnimation(widget, b'pos')\nanimation.setDuration(1000)\nanimation.start()",
    }

    return examples.get(component_name, "")


def update_properties_for_page(window, page_name: str):
    """Update properties panel when page changes."""
    descriptions = {
        "Buttons": "Interactive button components with multiple variants and styles",
        "Inputs": "Text and data input components for forms",
        "Selections": "Dropdown, checkbox, radio, and slider controls",
        "Display": "Progress bars, labels, and typography elements",
        "Tables": "Data table with sorting and actions",
        "Trees & Lists": "Hierarchical tree and list widgets",
        "Dialogs": "Modal dialogs for user interaction",
        "Grid Layout": "Grid-based layout system",
        "Flex Layout": "Flexible box layout system",
        "Card Layout": "Card-based content organization",
        "Sidebar Layout": "Layout with fixed sidebar",
        "Theme Switcher": "Dynamic theme switching system",
        "Color Palette": "Theme color definitions",
        "Typography": "Text styling and hierarchy",
        "Basic Form": "Simple form components",
        "Validation": "Form validation examples",
        "Complex Form": "Advanced form with multiple sections",
        "State Demo": "Redux-like state management",
        "Transitions": "Fade and slide transitions",
        "Progress": "Animated progress indicators",
        "Effects": "Visual animation effects",
    }

    description = descriptions.get(page_name, "")
    _update_properties(window, page_name, description)


def update_code_display_themes(window):
    """Update all code displays when theme changes."""
    # Update the current code display in properties panel
    if hasattr(window, "current_code_display") and window.current_code_display:
        window.current_code_display.update_theme()
