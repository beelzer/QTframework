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
        # Always apply theme from config.yaml to sync with config file
        self._apply_initial_theme()

    def _setup_managers(self):
        """Initialize framework managers."""
        # Initialize config manager first to get font_scale
        self._init_config_manager()

        # Use the theme manager from the Application instance
        app = QApplication.instance()
        if hasattr(app, "theme_manager"):
            self.theme_manager = app.theme_manager
        else:
            # Fallback in case Application is not used
            resources_path = Path(__file__).parent.parent.parent.parent / "resources"
            font_scale = self.config_manager.get("ui.font_scale", 100)
            self.theme_manager = ThemeManager(resources_path / "themes", font_scale=font_scale)

    def _init_config_manager(self):
        """Initialize config manager and load configuration."""

        # Initialize config manager and load from YAML template
        self.config_manager = ConfigManager()
        config_dir = Path(__file__).parent.parent
        self.config_file = config_dir / "config.yaml"  # Store path for saving later
        config_example = config_dir / "config.yaml.example"

        # Copy example to config.yaml if it doesn't exist
        if not self.config_file.exists() and config_example.exists():
            try:
                import shutil

                shutil.copy(config_example, self.config_file)
                print(f"Created config.yaml from config.yaml.example")
            except Exception as e:
                print(f"Warning: Could not copy example config: {e}")

        # Load config file
        if self.config_file.exists():
            try:
                self.config_manager.load_file(self.config_file)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                # Fall back to defaults if file loading fails
                self._load_default_config()
        else:
            self._load_default_config()

    def _load_default_config(self):
        """Load default configuration as fallback."""
        self.config_manager.load_defaults({
            "$schema_version": "1.0.0",
            "app": {
                "name": "Qt Framework Showcase",
                "version": "1.0.0",
                "debug": False,
            },
            "ui": {
                "theme": "light",
                "language": "en_US",
                "font_scale": 100,
            },
            "performance": {
                "cache_size": 100,
                "max_threads": 4,
            },
        })

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
        """Apply the initial theme from config."""
        # Get theme from config, default to "light" if not set
        theme_name = self.config_manager.get("ui.theme", "light")
        self.apply_theme(theme_name)

    def apply_theme(self, theme_name: str):
        """Apply the selected theme."""
        if self.theme_manager.set_theme(theme_name):
            stylesheet = self.theme_manager.get_stylesheet()
            QApplication.instance().setStyleSheet(stylesheet)
            self.status_bar.showMessage(f"Applied theme: {theme_name}", 3000)

            # Update config with new theme
            self.config_manager.set("ui.theme", theme_name)
            self.save_config()

            # Update code displays when theme changes
            from .dockwidgets import update_code_display_themes

            update_code_display_themes(self)

    def save_config(self):
        """Save current configuration to file."""
        if hasattr(self, "config_file") and self.config_file:
            try:
                self.config_manager.save(self.config_file)
            except Exception as e:
                print(f"Warning: Could not save config file: {e}")
