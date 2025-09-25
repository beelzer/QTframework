"""
Main application window for the showcase.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QStatusBar, QVBoxLayout, QWidget

from qtframework.config import ConfigManager
from qtframework.navigation import Navigator
from qtframework.state import Store
from qtframework.themes import ThemeManager

from .content import ContentArea
from .dockwidgets import create_dock_widgets
from .menubar import create_menu_bar
from .navigation import NavigationPanel
from .toolbar import create_toolbars


class ShowcaseWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        """Initialize the showcase window."""
        super().__init__()
        self._setup_managers()
        self._init_ui()
        self._apply_initial_theme()

    def _setup_managers(self):
        """Initialize framework managers."""
        # Use the theme manager from the Application instance
        app = QApplication.instance()
        if hasattr(app, "theme_manager"):
            self.theme_manager = app.theme_manager
        else:
            # Fallback in case Application is not used
            resources_path = Path(__file__).parent.parent.parent.parent / "resources"
            self.theme_manager = ThemeManager(resources_path / "themes")
        self.config_manager = ConfigManager()

        # Create a simple reducer for the demo
        def demo_reducer(state, action):
            if state is None:
                state = {"counter": 0}

            action_type = action.type if hasattr(action, "type") else str(action)

            if action_type == "INCREMENT":
                return {**state, "counter": state.get("counter", 0) + 1}
            if action_type == "DECREMENT":
                return {**state, "counter": state.get("counter", 0) - 1}
            if action_type == "SET_COUNTER":
                value = action.payload if hasattr(action, "payload") else 0
                return {**state, "counter": value}
            if action_type == "RESET" or action_type == "@@RESET":
                return {"counter": 0}

            return state

        self.state_store = Store(demo_reducer, initial_state={"counter": 0})
        self.navigator = Navigator()

    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Qt Framework - Feature Showcase")
        self.setGeometry(100, 50, 1400, 900)

        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)

        # Navigation panel
        self.nav_panel = NavigationPanel(self)
        splitter.addWidget(self.nav_panel)

        # Content area
        self.content_area = ContentArea(self)
        splitter.addWidget(self.content_area)

        # Set initial splitter sizes
        splitter.setSizes([250, 1150])
        main_layout.addWidget(splitter)

        # Create UI components
        create_menu_bar(self)
        create_toolbars(self)
        create_dock_widgets(self)
        self._create_status_bar()

    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Qt Framework Showcase - Ready", 5000)

    def _apply_initial_theme(self):
        """Apply the initial theme."""
        self.apply_theme("light")

    def apply_theme(self, theme_name: str):
        """Apply the selected theme."""
        if self.theme_manager.set_theme(theme_name):
            stylesheet = self.theme_manager.get_stylesheet()
            QApplication.instance().setStyleSheet(stylesheet)
            self.status_bar.showMessage(f"Applied theme: {theme_name}", 3000)

            # Update code displays when theme changes
            from .dockwidgets import update_code_display_themes

            update_code_display_themes(self)
