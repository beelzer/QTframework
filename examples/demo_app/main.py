"""Example application demonstrating Qt Framework usage."""

from __future__ import annotations

import sys
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QTextEdit,
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QSpinBox,
    QCheckBox,
    QPushButton,
    QGroupBox,
    QTabWidget,
    QFormLayout,
    QSlider,
    QDoubleSpinBox,
    QLineEdit,
    QGridLayout,
    QFrame,
)

from shiboken6 import isValid
from qtframework import Application, BaseWindow
from qtframework.layouts import Card, FlexLayout, SidebarLayout
from qtframework.layouts.sidebar import SidebarPosition
from qtframework.layouts.base import Direction
from qtframework.widgets import (
    Button,
    IconButton,
    Input,
    PasswordInput,
    SearchInput,
    TextArea,
    ToggleButton,
)
from qtframework.widgets.buttons import ButtonSize, ButtonVariant
from qtframework.widgets.advanced import (
    LineChart,
    BarChart,
    PieChart,
    DataTable,
    TreeTable,
    NotificationManager,
    Notification,
    InputDialog,
    ConfirmDialog,
    ProgressDialog,
    FormDialog,
    TabWidget,
    BaseTabPage,
)
from qtframework.widgets.advanced.notifications import NotificationType
from qtframework.state import Store, Action
from qtframework.navigation import Router, Navigator, Route
from qtframework.config import ConfigManager
from qtframework.plugins import PluginManager
from qtframework.utils.logger import get_logger

logger = get_logger(__name__)


# Configuration Tab Classes for Demo
class ApplicationConfigTab(BaseTabPage):
    """Configuration tab for application settings."""

    def _setup_ui(self) -> None:
        """Setup application settings UI."""
        # Application Info Group
        app_group = self._create_group("Application Information")

        # App name
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Enter application name")
        self._add_control_to_group(app_group, "Name:", name_edit, "app.name")

        # Version
        version_edit = QLineEdit()
        version_edit.setPlaceholderText("e.g., 1.0.0")
        self._add_control_to_group(app_group, "Version:", version_edit, "app.version")

        # Organization
        org_edit = QLineEdit()
        org_edit.setPlaceholderText("Organization name")
        self._add_control_to_group(app_group, "Organization:", org_edit, "app.organization")

        # Debug mode
        debug_check = QCheckBox()
        debug_check.setText("Enable debug logging and developer features")
        self._add_control_to_group(app_group, "Debug Mode:", debug_check, "app.debug")

        self._layout.addWidget(app_group)
        self._layout.addStretch()

    def _connect_signals(self) -> None:
        """Connect application settings signals."""
        for key, control in self._controls.items():
            if isinstance(control, QLineEdit):
                control.textChanged.connect(
                    lambda text, k=key: self.value_changed.emit(k, text)
                )
            elif isinstance(control, QCheckBox):
                control.toggled.connect(
                    lambda checked, k=key: self.value_changed.emit(k, checked)
                )


class UIConfigTab(BaseTabPage):
    """Configuration tab for UI settings."""

    def _setup_ui(self) -> None:
        """Setup UI settings."""
        # Theme Group
        theme_group = self._create_group("Theme & Appearance")

        # Theme selection
        theme_combo = QComboBox()
        theme_combo.addItems(["monokai", "dark", "light", "blue", "purple"])
        self._add_control_to_group(theme_group, "Theme:", theme_combo, "ui.theme")

        # Language
        lang_combo = QComboBox()
        lang_combo.addItems(["en", "es", "fr", "de", "zh"])
        self._add_control_to_group(theme_group, "Language:", lang_combo, "ui.language")

        # Font size
        font_spin = QSpinBox()
        font_spin.setMinimum(8)
        font_spin.setMaximum(24)
        font_spin.setSuffix(" pt")
        self._add_control_to_group(theme_group, "Font Size:", font_spin, "ui.font_size")

        self._layout.addWidget(theme_group)
        self._layout.addStretch()

    def _connect_signals(self) -> None:
        """Connect UI settings signals."""
        for key, control in self._controls.items():
            if isinstance(control, QComboBox):
                control.currentTextChanged.connect(
                    lambda text, k=key: self.value_changed.emit(k, text)
                )
            elif isinstance(control, QSpinBox):
                control.valueChanged.connect(
                    lambda value, k=key: self.value_changed.emit(k, value)
                )


class FeaturesConfigTab(BaseTabPage):
    """Configuration tab for feature toggles."""

    def _setup_ui(self) -> None:
        """Setup feature settings."""
        # Core Features Group
        core_group = self._create_group("Core Features")

        features = [
            ("charts", "Charts & Graphs"),
            ("tables", "Data Tables"),
            ("notifications", "Notifications"),
            ("state_management", "State Management"),
            ("routing", "Navigation Routing"),
            ("plugins", "Plugin System"),
            ("themes", "Theme System"),
            ("auto_save", "Auto Save"),
            ("developer_mode", "Developer Mode"),
        ]

        for key, title in features:
            check = QCheckBox()
            check.setText(title)
            self._add_control_to_group(core_group, title + ":", check, f"features.{key}")

        self._layout.addWidget(core_group)
        self._layout.addStretch()

    def _connect_signals(self) -> None:
        """Connect feature settings signals."""
        for key, control in self._controls.items():
            if isinstance(control, QCheckBox):
                control.toggled.connect(
                    lambda checked, k=key: self.value_changed.emit(k, checked)
                )


class DemoWindow(BaseWindow):
    """Demo window showcasing framework features."""

    # Centralized path configuration
    RESOURCES_DIR = Path(__file__).parent.parent.parent / "resources"
    CONFIG_FILE = RESOURCES_DIR / "settings.json"
    DEFAULTS_FILE = RESOURCES_DIR / "demo_defaults.json"

    def __init__(self, application: Application | None = None) -> None:
        """Initialize demo window."""
        super().__init__(application, title="Qt Framework Complete Demo")
        self.notification_manager = NotificationManager(self)

        # Initialize config controls dictionary
        self.config_controls = {}

        # Setup store with root reducer
        def root_reducer(state: dict, action: Action) -> dict:
            if state is None:
                state = {"counter": 0, "items": []}

            # Handle counter actions
            if action.type == "INCREMENT":
                state["counter"] = state.get("counter", 0) + 1
            elif action.type == "DECREMENT":
                state["counter"] = state.get("counter", 0) - 1
            elif action.type == "RESET":
                state["counter"] = 0

            # Handle items actions
            elif action.type == "ADD_ITEM":
                items = state.get("items", []).copy()
                items.append(action.payload)
                state["items"] = items
            elif action.type == "REMOVE_ITEM":
                items = state.get("items", []).copy()
                if action.payload in items:
                    items.remove(action.payload)
                state["items"] = items
            elif action.type == "CLEAR_ITEMS":
                state["items"] = []

            return state

        self.store = Store(root_reducer, initial_state={"counter": 0, "items": []})
        self.router = Router()
        self.config_manager = ConfigManager()
        self.plugin_manager = PluginManager()

        self._setup_routing()
        self._setup_config()
        self._setup_ui()

    def _setup_routing(self) -> None:
        """Setup navigation routing."""
        # For demo purposes, we'll use simple widget functions
        # In a real app, these would be actual widget classes
        from PySide6.QtWidgets import QLabel, QTextEdit

        def create_home_widget():
            widget = QTextEdit()
            widget.setReadOnly(True)
            widget.setHtml("""
                <h2>Home Page</h2>
                <p>Welcome to the Qt Framework Demo Home Page!</p>
                <p>This is a demonstration of the routing system.</p>
                <ul>
                    <li>Navigation works between different routes</li>
                    <li>Each route can have its own component</li>
                    <li>History tracking is enabled</li>
                    <li>Back/Forward navigation is supported</li>
                </ul>
            """)
            return widget

        def create_buttons_widget():
            widget = QTextEdit()
            widget.setReadOnly(True)
            widget.setHtml("""
                <h2>Buttons Page</h2>
                <p>This page demonstrates button components:</p>
                <ul>
                    <li>Various button styles and variants</li>
                    <li>Different button sizes</li>
                    <li>Toggle buttons</li>
                    <li>Icon buttons</li>
                </ul>
                <p>Navigate to Basic Widgets section to see actual button examples.</p>
            """)
            return widget

        def create_inputs_widget():
            widget = QTextEdit()
            widget.setReadOnly(True)
            widget.setHtml("""
                <h2>Inputs Page</h2>
                <p>Input components available:</p>
                <ul>
                    <li>Text inputs with placeholders</li>
                    <li>Password inputs</li>
                    <li>Search inputs with instant search</li>
                    <li>Text areas for multi-line input</li>
                </ul>
            """)
            return widget

        def create_charts_widget():
            widget = QTextEdit()
            widget.setReadOnly(True)
            widget.setHtml("""
                <h2>Charts Page</h2>
                <p>Available chart types:</p>
                <ul>
                    <li>Line charts for trends</li>
                    <li>Bar charts for comparisons</li>
                    <li>Pie charts for distributions</li>
                </ul>
                <p>Navigate to Advanced Widgets section to see chart examples.</p>
            """)
            return widget

        def create_tables_widget():
            widget = QTextEdit()
            widget.setReadOnly(True)
            widget.setHtml("""
                <h2>Tables Page</h2>
                <p>Table components:</p>
                <ul>
                    <li>Data tables with sorting</li>
                    <li>Tree tables for hierarchical data</li>
                    <li>Pagination support</li>
                    <li>Selection modes</li>
                </ul>
            """)
            return widget

        # Define routes with actual components
        routes = [
            Route(path="/home", component=create_home_widget, name="home"),
            Route(path="/buttons", component=create_buttons_widget, name="buttons"),
            Route(path="/inputs", component=create_inputs_widget, name="inputs"),
            Route(path="/charts", component=create_charts_widget, name="charts"),
            Route(path="/tables", component=create_tables_widget, name="tables"),
            Route(
                path="/state",
                component=lambda: QLabel("<h2>State Management Page</h2>\nRedux-style state management with actions and reducers"),
                name="state",
            ),
            Route(
                path="/config",
                component=lambda: QLabel("<h2>Configuration Page</h2>\nFlexible configuration management system"),
                name="config",
            ),
        ]

        for route in routes:
            self.router.add_route(route)

        # Connect router signals
        self.router.route_changed.connect(self._on_route_changed)
        self.router.navigation_blocked.connect(self._on_navigation_blocked)

    def _setup_config(self) -> None:
        """Setup configuration management using standardized config system."""
        defaults_path = self.DEFAULTS_FILE
        user_config_path = self.CONFIG_FILE
        loaded_count = 0

        defaults: dict[str, Any] = {}
        if defaults_path.exists():
            try:
                import json
                with open(defaults_path, "r", encoding="utf-8") as f:
                    defaults = json.load(f)
                logger.info(f"Loaded defaults from: {defaults_path}")
            except Exception as exc:
                logger.warning(f"Failed to load defaults from {defaults_path}: {exc}")

        if not defaults:
            defaults = {
                "$schema_version": "1.0.0",
                "app": {
                    "name": "Qt Framework Complete Demo",
                    "version": "1.0.0",
                    "debug": False,
                    "organization": "Qt Framework Team"
                },
                "ui": {
                    "theme": "monokai",
                    "language": "en",
                    "font_size": 12,
                    "window": {
                        "width": 1400,
                        "height": 900,
                        "remember_size": True,
                        "center_on_startup": True
                    },
                    "animations": {
                        "enabled": True,
                        "duration": 250
                    }
                },
                "features": {
                    "charts": True,
                    "tables": True,
                    "notifications": True,
                    "state_management": True,
                    "routing": True,
                    "plugins": True,
                    "themes": True,
                    "auto_save": True,
                    "developer_mode": False
                },
                "performance": {
                    "cache_size": 100,
                    "max_threads": 4,
                    "lazy_loading": True,
                    "prefetch_data": False
                },
                "demo": {
                    "show_welcome": True,
                    "sample_data_size": 1000,
                    "enable_tooltips": True,
                    "highlight_new_features": True
                }
            }
            logger.info("Using embedded defaults for configuration")

        self.config_manager.load_defaults(defaults)
        loaded_count += 1

        if user_config_path.exists():
            try:
                if self.config_manager.load_file(user_config_path, validate=True):
                    loaded_count += 1
                    logger.info(f"Loaded overrides from: {user_config_path}")
            except Exception as exc:
                logger.warning(f"Failed to load overrides from {user_config_path}: {exc}")
        else:
            logger.info(f"User config not found, expected at {user_config_path}")

        env_prefix = "QTFRAMEWORKCOMPLETEDEMO_"
        self.config_manager.load_env(env_prefix)

        self._apply_runtime_config()

    def _setup_ui(self) -> None:
        """Setup UI components."""
        super()._setup_ui()
        self.setMinimumSize(1400, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = SidebarLayout(
            central_widget,
            sidebar_width=300,
            position=SidebarPosition.LEFT,
        )

        self._setup_sidebar(main_layout)
        self._setup_content(main_layout)

        central_layout = FlexLayout(
            Direction.VERTICAL,
            spacing=0,
            margins=0,
            parent=central_widget,
        )
        central_layout.add_widget(main_layout, stretch=1)

    def _setup_sidebar(self, layout: SidebarLayout) -> None:
        """Setup sidebar content."""
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(16)
        sidebar_layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("<h2>Framework Demo</h2>")
        sidebar_layout.addWidget(title)

        # Theme settings
        theme_card = Card(title="Theme Settings")
        theme_label = QLabel("Select Theme:")
        theme_combo = QComboBox()
        theme_combo.addItems(["light", "dark", "monokai"])

        # Set the combo box to show the current theme
        if self._app and self._app.theme_manager:
            current_theme = self._app.theme_manager.get_current_theme_name()
            index = theme_combo.findText(current_theme)
            if index >= 0:
                theme_combo.setCurrentIndex(index)

        theme_combo.currentTextChanged.connect(self._on_theme_changed)

        theme_card.add_widget(theme_label)
        theme_card.add_widget(theme_combo)
        sidebar_layout.addWidget(theme_card)

        # Navigation
        nav_card = Card(title="Navigation")
        self.nav_list = QListWidget()
        self.nav_list.addItems([
            "Basic Widgets",
            "Advanced Widgets",
            "State Management",
            "Navigation/Routing",
            "Configuration",
            "Plugins",
            "Notifications",
        ])
        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        nav_card.add_widget(self.nav_list)
        sidebar_layout.addWidget(nav_card)

        # Quick Actions
        actions_card = Card(title="Quick Actions")

        show_notification_btn = Button("Show Notification", variant=ButtonVariant.PRIMARY)
        show_notification_btn.clicked.connect(self._show_notification)
        actions_card.add_widget(show_notification_btn)

        show_dialog_btn = Button("Show Dialog", variant=ButtonVariant.SECONDARY)
        show_dialog_btn.clicked.connect(self._show_dialog)
        actions_card.add_widget(show_dialog_btn)

        sidebar_layout.addWidget(actions_card)

        sidebar_layout.addStretch()

        layout.set_sidebar_widget(sidebar)

    def _setup_content(self, layout: SidebarLayout) -> None:
        """Setup content area."""
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setSpacing(24)
        self.content_layout.setContentsMargins(24, 24, 24, 24)

        self._show_basic_widgets()

        self.scroll.setWidget(self.content)
        layout.set_content_widget(self.scroll)

    def _on_nav_changed(self, index: int) -> None:
        """Handle navigation change."""
        # Clear content
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Show selected content
        if index == 0:
            self._show_basic_widgets()
        elif index == 1:
            self._show_advanced_widgets()
        elif index == 2:
            self._show_state_management()
        elif index == 3:
            self._show_navigation()
        elif index == 4:
            self._show_configuration()
        elif index == 5:
            self._show_plugins()
        elif index == 6:
            self._show_notifications_demo()

    def _show_basic_widgets(self) -> None:
        """Show basic widgets section."""
        self.content_layout.addWidget(QLabel("<h1>Basic Qt Framework Components</h1>"))

        # Buttons section
        self._setup_buttons_section(self.content_layout)

        # Inputs section
        self._setup_inputs_section(self.content_layout)

        # Cards section
        self._setup_cards_section(self.content_layout)

        self.content_layout.addStretch()

    def _show_advanced_widgets(self) -> None:
        """Show advanced widgets section."""
        self.content_layout.addWidget(QLabel("<h1>Advanced Widgets</h1>"))

        # Charts section
        charts_card = Card(title="Enhanced Charts with Grid & Legend", elevated=True)

        charts_layout = QHBoxLayout()

        # Line chart with realistic sales trend data
        line_chart = LineChart()
        line_chart.set_title("Monthly Sales Trend (2024)")
        # Realistic sales data with growth trend
        sales_data = [120, 135, 158, 142, 189, 234, 267, 298, 312, 345, 389, 421]
        line_chart.set_data(sales_data, ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
        line_chart.set_show_grid(True)  # Enable grid
        line_chart.setMinimumSize(350, 250)
        charts_layout.addWidget(line_chart)

        # Bar chart with product sales data
        bar_chart = BarChart()
        bar_chart.set_title("Product Sales Q4 2024")
        product_sales = [1250, 985, 743, 612, 498]
        bar_chart.set_data(product_sales, ["Laptops", "Tablets", "Phones", "Accessories", "Software"])
        bar_chart.set_show_grid(True)  # Enable grid
        bar_chart.setMinimumSize(350, 250)
        charts_layout.addWidget(bar_chart)

        # Pie chart with market share and legend
        pie_chart = PieChart()
        pie_chart.set_title("Market Share Distribution")
        market_share = [35, 28, 18, 12, 7]
        pie_chart.set_data(market_share, ["Apple", "Samsung", "Google", "Microsoft", "Others"])
        pie_chart.set_show_legend(True)  # Enable legend
        pie_chart.setMinimumSize(400, 250)  # Wider for legend
        charts_layout.addWidget(pie_chart)

        charts_widget = QWidget()
        charts_widget.setLayout(charts_layout)
        charts_card.add_widget(charts_widget)

        self.content_layout.addWidget(charts_card)

        # Enhanced Tables section
        tables_card = Card(title="Enhanced Data Tables with Search & Filter", elevated=True)

        # Enhanced Data table with search/filter capabilities
        data_table = DataTable()
        data_table.set_headers(["ID", "Name", "Department", "Email", "Salary", "Status"])

        # More realistic employee data
        employee_data = [
            ["001", "John Doe", "Engineering", "john.doe@company.com", "$85,000", "Active"],
            ["002", "Jane Smith", "Marketing", "jane.smith@company.com", "$72,000", "Active"],
            ["003", "Bob Johnson", "Engineering", "bob.johnson@company.com", "$92,000", "Active"],
            ["004", "Alice Brown", "HR", "alice.brown@company.com", "$68,000", "Active"],
            ["005", "Charlie Davis", "Sales", "charlie.davis@company.com", "$65,000", "Pending"],
            ["006", "Diana Wilson", "Engineering", "diana.wilson@company.com", "$88,000", "Active"],
            ["007", "Eva Martinez", "Finance", "eva.martinez@company.com", "$75,000", "Active"],
            ["008", "Frank Miller", "Sales", "frank.miller@company.com", "$70,000", "Inactive"],
            ["009", "Grace Lee", "Marketing", "grace.lee@company.com", "$73,000", "Active"],
            ["010", "Henry Taylor", "IT", "henry.taylor@company.com", "$82,000", "Active"],
        ]

        data_table.set_data(employee_data)
        data_table.setMinimumHeight(250)

        # Connect demonstration signals
        data_table.row_selected.connect(lambda row: logger.debug(f"Selected employee at row {row}"))
        data_table.cell_edited.connect(lambda row, col, text: logger.debug(f"Cell edited: Row {row}, Col {col}, New value: {text}"))
        data_table.row_double_clicked.connect(lambda row: logger.debug(f"Double-clicked employee at row {row}"))

        tables_card.add_widget(QLabel("Enhanced DataTable with Search/Filter (Try searching 'Engineering' or filtering by department):"))
        tables_card.add_widget(data_table)

        # Enhanced Tree table with file browser structure
        tree_table = TreeTable()
        tree_table.set_headers(["Name", "Type", "Size", "Modified"])

        # Create a realistic file browser structure
        project_root = tree_table.add_item(None, ["MyProject", "Folder", "-", "2024-01-15"])

        # Source folder
        src_folder = tree_table.add_item(project_root, ["src", "Folder", "-", "2024-01-15"])
        tree_table.add_item(src_folder, ["main.py", "Python File", "12.5 KB", "2024-01-15"])
        tree_table.add_item(src_folder, ["utils.py", "Python File", "8.3 KB", "2024-01-14"])
        tree_table.add_item(src_folder, ["config.py", "Python File", "2.1 KB", "2024-01-10"])

        # Components subfolder
        components_folder = tree_table.add_item(src_folder, ["components", "Folder", "-", "2024-01-12"])
        tree_table.add_item(components_folder, ["button.py", "Python File", "5.2 KB", "2024-01-12"])
        tree_table.add_item(components_folder, ["input.py", "Python File", "7.8 KB", "2024-01-11"])
        tree_table.add_item(components_folder, ["chart.py", "Python File", "15.4 KB", "2024-01-12"])

        # Tests folder
        tests_folder = tree_table.add_item(project_root, ["tests", "Folder", "-", "2024-01-13"])
        tree_table.add_item(tests_folder, ["test_main.py", "Python File", "6.7 KB", "2024-01-13"])
        tree_table.add_item(tests_folder, ["test_utils.py", "Python File", "4.2 KB", "2024-01-12"])

        # Documentation folder
        docs_folder = tree_table.add_item(project_root, ["docs", "Folder", "-", "2024-01-08"])
        tree_table.add_item(docs_folder, ["README.md", "Markdown", "8.9 KB", "2024-01-08"])
        tree_table.add_item(docs_folder, ["API.md", "Markdown", "15.2 KB", "2024-01-07"])
        tree_table.add_item(docs_folder, ["CHANGELOG.md", "Markdown", "3.4 KB", "2024-01-05"])

        # Assets folder
        assets_folder = tree_table.add_item(project_root, ["assets", "Folder", "-", "2024-01-06"])
        tree_table.add_item(assets_folder, ["logo.png", "Image", "45.6 KB", "2024-01-06"])
        tree_table.add_item(assets_folder, ["icon.svg", "Vector Image", "8.2 KB", "2024-01-06"])
        tree_table.add_item(assets_folder, ["styles.css", "CSS File", "12.8 KB", "2024-01-05"])

        # Configuration files
        tree_table.add_item(project_root, ["requirements.txt", "Text File", "1.2 KB", "2024-01-10"])
        tree_table.add_item(project_root, [".gitignore", "Git Ignore", "0.8 KB", "2024-01-01"])
        tree_table.add_item(project_root, ["setup.py", "Python File", "3.5 KB", "2024-01-01"])

        tree_table.setMinimumHeight(300)

        # Connect demonstration signals
        tree_table.item_selected.connect(lambda item: logger.debug(f"Selected tree item: {item}"))
        tree_table.item_expanded.connect(lambda item: logger.debug(f"Expanded tree item: {item}"))
        tree_table.item_double_clicked.connect(lambda item: logger.debug(f"Double-clicked tree item: {item}"))

        tables_card.add_widget(QLabel("Enhanced TreeTable with Search & Expand/Collapse (Try searching 'test' or 'docs'):"))
        tables_card.add_widget(tree_table)

        self.content_layout.addWidget(tables_card)

        self.content_layout.addStretch()

    def _show_state_management(self) -> None:
        """Show state management section."""
        self.content_layout.addWidget(QLabel("<h1>State Management</h1>"))

        state_card = Card(title="Redux-style State Management", elevated=True)

        # Counter demo
        counter_group = QGroupBox("Counter Example")
        counter_layout = QHBoxLayout()

        self.counter_label = QLabel(f"Counter: {self.store.get_state().get('counter', 0)}")
        counter_layout.addWidget(self.counter_label)

        inc_btn = Button("Increment", variant=ButtonVariant.PRIMARY)
        inc_btn.clicked.connect(lambda: self._update_counter("INCREMENT"))
        counter_layout.addWidget(inc_btn)

        dec_btn = Button("Decrement", variant=ButtonVariant.SECONDARY)
        dec_btn.clicked.connect(lambda: self._update_counter("DECREMENT"))
        counter_layout.addWidget(dec_btn)

        reset_btn = Button("Reset", variant=ButtonVariant.DANGER)
        reset_btn.clicked.connect(lambda: self._update_counter("RESET"))
        counter_layout.addWidget(reset_btn)

        counter_group.setLayout(counter_layout)
        state_card.add_widget(counter_group)

        # Items list demo
        items_group = QGroupBox("List Management")
        items_layout = QVBoxLayout()

        add_item_layout = QHBoxLayout()
        self.item_input = Input(placeholder="Enter item name...")
        add_item_btn = Button("Add Item", variant=ButtonVariant.PRIMARY)
        add_item_btn.clicked.connect(self._add_item)
        add_item_layout.addWidget(self.item_input)
        add_item_layout.addWidget(add_item_btn)

        items_layout.addLayout(add_item_layout)

        self.items_list = QListWidget()
        self.items_list.setMaximumHeight(150)
        items_layout.addWidget(self.items_list)

        clear_btn = Button("Clear All", variant=ButtonVariant.DANGER)
        clear_btn.clicked.connect(self._clear_items)
        items_layout.addWidget(clear_btn)

        items_group.setLayout(items_layout)
        state_card.add_widget(items_group)

        # State display
        state_display = QGroupBox("Current State")
        state_layout = QVBoxLayout()
        self.state_text = QTextEdit()
        self.state_text.setReadOnly(True)
        self.state_text.setMaximumHeight(150)
        self._update_state_display()
        state_layout.addWidget(self.state_text)
        state_display.setLayout(state_layout)
        state_card.add_widget(state_display)

        self.content_layout.addWidget(state_card)

        # Subscribe to state changes
        self.store.subscribe(self._on_state_change)

        self.content_layout.addStretch()

    def _show_navigation(self) -> None:
        """Show navigation/routing section."""
        self.content_layout.addWidget(QLabel("<h1>Navigation & Routing</h1>"))

        nav_card = Card(title="Router Navigation", elevated=True)

        nav_info = QLabel("The framework includes a router for navigation between different views/pages.")
        nav_info.setWordWrap(True)
        nav_card.add_widget(nav_info)

        # Navigation buttons
        nav_buttons_layout = QHBoxLayout()
        for route in ["/home", "/buttons", "/inputs", "/charts", "/tables"]:
            route_name = route.replace("/", "").title()
            nav_btn = Button(f"Go to {route_name}", variant=ButtonVariant.SECONDARY)
            nav_btn.clicked.connect(lambda checked, r=route: self.router.navigate(r))
            nav_buttons_layout.addWidget(nav_btn)

        nav_buttons_widget = QWidget()
        nav_buttons_widget.setLayout(nav_buttons_layout)
        nav_card.add_widget(nav_buttons_widget)

        # Route info
        self.route_label = QLabel(f"Current Route: {self.router.current_path}")
        nav_card.add_widget(self.route_label)

        # Navigator widget to display route components
        self.route_display = QGroupBox("Route Component Display")
        route_display_layout = QVBoxLayout()
        self.route_content = QLabel("Navigate to a route to see its component")
        self.route_content.setWordWrap(True)
        self.route_content.setMinimumHeight(100)
        self.route_content.setStyleSheet("QLabel { background-color: palette(base); padding: 10px; }")
        route_display_layout.addWidget(self.route_content)
        self.route_display.setLayout(route_display_layout)
        nav_card.add_widget(self.route_display)

        # History
        history_group = QGroupBox("Navigation History")
        history_layout = QVBoxLayout()
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(150)
        self._update_history_display()
        history_layout.addWidget(self.history_list)

        history_btns_layout = QHBoxLayout()
        back_btn = Button("Back", variant=ButtonVariant.SECONDARY)
        back_btn.clicked.connect(self._handle_back)
        forward_btn = Button("Forward", variant=ButtonVariant.SECONDARY)
        forward_btn.clicked.connect(self._handle_forward)
        clear_btn = Button("Clear History", variant=ButtonVariant.DANGER)
        clear_btn.clicked.connect(self._clear_history)
        history_btns_layout.addWidget(back_btn)
        history_btns_layout.addWidget(forward_btn)
        history_btns_layout.addWidget(clear_btn)

        history_layout.addLayout(history_btns_layout)
        history_group.setLayout(history_layout)
        nav_card.add_widget(history_group)

        self.content_layout.addWidget(nav_card)
        self.content_layout.addStretch()

    def _show_configuration(self) -> None:
        """Show configuration management section."""
        self.content_layout.addWidget(QLabel("<h1>Configuration Management</h1>"))

        config_card = Card(title="Configuration System", elevated=True)

        info = QLabel("The framework includes a flexible configuration management system with multiple providers and schema versioning.")
        info.setWordWrap(True)
        config_card.add_widget(info)

        # Configuration sources
        sources_group = QGroupBox("Configuration Sources (Priority Order)")
        sources_layout = QVBoxLayout()

        sources = self.config_manager.get_sources()
        for i, source in enumerate(sources, 1):
            source_label = QLabel(f"{i}. {source}")
            if source == "defaults":
                source_label.setText(f"{i}. {source} (Framework defaults)")
            elif "resources" in source:
                source_label.setText(f"{i}. {source} (Custom defaults)")
            sources_layout.addWidget(source_label)

        sources_group.setLayout(sources_layout)
        config_card.add_widget(sources_group)

        # Current config
        config_group = QGroupBox("Current Configuration")
        config_layout = QVBoxLayout()

        config_items = [
            f"Schema Version: {self.config_manager.get_config_schema_version()}",
            f"app.name: {self.config_manager.get('app.name', 'Not set')}",
            f"app.version: {self.config_manager.get('app.version', 'Not set')}",
            f"app.debug: {self.config_manager.get('app.debug', 'Not set')}",
            f"ui.theme: {self.config_manager.get('ui.theme', 'Not set')}",
            f"ui.font_size: {self.config_manager.get('ui.font_size', 'Not set')}",
            f"ui.window.width: {self.config_manager.get('ui.window.width', 'Not set')}",
            f"ui.window.height: {self.config_manager.get('ui.window.height', 'Not set')}",
            f"features.charts: {self.config_manager.get('features.charts', False)}",
            f"features.tables: {self.config_manager.get('features.tables', False)}",
            f"features.notifications: {self.config_manager.get('features.notifications', False)}",
            f"features.themes: {self.config_manager.get('features.themes', False)}",
            f"performance.cache_size: {self.config_manager.get('performance.cache_size', 'Not set')}",
            f"demo.sample_data_size: {self.config_manager.get('demo.sample_data_size', 'Not set')}",
        ]

        for item in config_items:
            config_layout.addWidget(QLabel(item))

        config_group.setLayout(config_layout)
        config_card.add_widget(config_group)

        # Config file viewer
        viewer_group = QGroupBox("Configuration Files")
        viewer_layout = QVBoxLayout()

        # Show custom config info
        resources_config = self.CONFIG_FILE

        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(150)

        defaults_path = self.DEFAULTS_FILE
        loaded_sources = self.config_manager.get_sources()
        defaults_path = self.DEFAULTS_FILE
        loaded_sources = self.config_manager.get_sources()
        existing_configs = sorted(self.RESOURCES_DIR.glob("*.json"))
        info_lines = [
            f"Config Directory: {self.RESOURCES_DIR}",
            f"Defaults Config Path: {defaults_path if defaults_path.exists() else 'Not found'}",
            f"User Config Path: {resources_config if resources_config.exists() else 'Not found'}",
            f"Available Config Files: {', '.join(str(p.relative_to(self.RESOURCES_DIR)) for p in existing_configs) if existing_configs else 'None'}",
            f"Loaded Sources: {', '.join(loaded_sources) if loaded_sources else 'None'}",
        ]

        info_text.setPlainText("\n".join(info_lines))
        viewer_layout.addWidget(QLabel("Configuration File Info:"))
        viewer_layout.addWidget(info_text)
        self.config_viewer = QTextEdit()
        self.config_viewer.setMaximumHeight(200)
        self.config_viewer.setReadOnly(True)
        self._update_config_viewer()

        viewer_layout.addWidget(QLabel("Current Configuration (JSON):"))
        viewer_layout.addWidget(self.config_viewer)

        # Refresh button
        refresh_btn = Button("Refresh Config View", variant=ButtonVariant.SECONDARY)
        refresh_btn.clicked.connect(self._reload_config_from_resources)
        viewer_layout.addWidget(refresh_btn)

        viewer_group.setLayout(viewer_layout)
        config_card.add_widget(viewer_group)

        # Advanced Config Editor
        editor_group = QGroupBox("Advanced Configuration Editor")
        editor_layout = QVBoxLayout()

        # Create tabbed editor with new framework TabWidget
        self.config_tabs = TabWidget()

        # Get current configuration data
        config_data = self.config_manager.get_all()

        # Create specialized config tab instances with relevant data sections
        self.app_tab = ApplicationConfigTab(self._filter_config(config_data, "app"))
        self.ui_tab = UIConfigTab(self._filter_config(config_data, "ui"))
        self.features_tab = FeaturesConfigTab(self._filter_config(config_data, "features"))

        # Connect tab value change signals
        self.app_tab.value_changed.connect(self._on_config_value_changed)
        self.ui_tab.value_changed.connect(self._on_config_value_changed)
        self.features_tab.value_changed.connect(self._on_config_value_changed)
        self._config_tab_pages = [("app", self.app_tab), ("ui", self.ui_tab), ("features", self.features_tab)]

        # Add tabs to widget
        self.config_tabs.add_tab(self.app_tab, "Application")
        self.config_tabs.add_tab(self.ui_tab, "User Interface")
        self.config_tabs.add_tab(self.features_tab, "Features")

        editor_layout.addWidget(self.config_tabs)

        # Control buttons
        button_layout = QHBoxLayout()

        reset_btn = Button("Reset to Defaults", variant=ButtonVariant.WARNING)
        reset_btn.clicked.connect(self._reset_config_to_defaults)

        apply_btn = Button("Apply Changes", variant=ButtonVariant.PRIMARY)
        apply_btn.clicked.connect(self._apply_config_changes)

        save_btn = Button("Save User Config", variant=ButtonVariant.SUCCESS)
        save_btn.clicked.connect(self._save_user_config)

        button_layout.addWidget(reset_btn)
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(save_btn)
        editor_layout.addLayout(button_layout)

        editor_group.setLayout(editor_layout)
        config_card.add_widget(editor_group)

        self.content_layout.addWidget(config_card)
        self.content_layout.addStretch()

    def _on_config_value_changed(self, key: str, value: Any) -> None:
        """Handle configuration value changes from tabs."""
        try:
            self.config_manager.set(key, value)
            if key in ('ui.theme', 'ui.font_size'):
                self._apply_runtime_config()
            if hasattr(self, 'config_viewer'):
                self._update_config_viewer()
        except Exception as exc:
            logger.warning(f"Failed to update configuration for {key}: {exc}")


    def _filter_config(self, config_data: dict[str, Any], prefix: str) -> dict[str, Any]:
        """Filter configuration data by prefix.

        Args:
            config_data: Full configuration dictionary
            prefix: Prefix to filter by (e.g., 'app', 'ui', 'features')

        Returns:
            Dictionary with only keys matching the prefix
        """
        flat_data = self._flatten_dict(config_data)
        return {
            key: value
            for key, value in flat_data.items()
            if key.startswith(f"{prefix}.")
        }

    def _show_plugins(self) -> None:
        """Show plugin system section."""
        self.content_layout.addWidget(QLabel("<h1>Plugin System</h1>"))

        plugin_card = Card(title="Extensible Plugin Architecture", elevated=True)

        info = QLabel("The framework supports a plugin system for extending functionality. Plugins can hook into the application lifecycle and add new features.")
        info.setWordWrap(True)
        plugin_card.add_widget(info)

        # Plugin list
        plugin_group = QGroupBox("Available Plugins")
        plugin_layout = QVBoxLayout()

        plugin_list = QListWidget()
        plugin_list.addItems([
            "Theme Plugin - Custom themes support",
            "Export Plugin - Data export functionality",
            "Analytics Plugin - Usage analytics",
            "Auth Plugin - Authentication support",
            "Database Plugin - Database connectivity",
        ])
        plugin_list.setMaximumHeight(150)
        plugin_layout.addWidget(plugin_list)

        plugin_group.setLayout(plugin_layout)
        plugin_card.add_widget(plugin_group)

        # Plugin actions
        actions_layout = QHBoxLayout()
        load_btn = Button("Load Plugin", variant=ButtonVariant.PRIMARY)
        load_btn.clicked.connect(lambda: self._show_message("Plugin loaded successfully"))
        unload_btn = Button("Unload Plugin", variant=ButtonVariant.SECONDARY)
        unload_btn.clicked.connect(lambda: self._show_message("Plugin unloaded"))
        reload_btn = Button("Reload All", variant=ButtonVariant.WARNING)
        reload_btn.clicked.connect(lambda: self._show_message("All plugins reloaded"))

        actions_layout.addWidget(load_btn)
        actions_layout.addWidget(unload_btn)
        actions_layout.addWidget(reload_btn)

        actions_widget = QWidget()
        actions_widget.setLayout(actions_layout)
        plugin_card.add_widget(actions_widget)

        self.content_layout.addWidget(plugin_card)
        self.content_layout.addStretch()

    def _show_notifications_demo(self) -> None:
        """Show notifications demo section."""
        self.content_layout.addWidget(QLabel("<h1>Notifications System</h1>"))

        notif_card = Card(title="Toast Notifications", elevated=True)

        info = QLabel("The framework includes a notification system for displaying toast messages to users.")
        info.setWordWrap(True)
        notif_card.add_widget(info)

        # Notification types
        types_group = QGroupBox("Notification Types")
        types_layout = QVBoxLayout()

        info_btn = Button("Show Info", variant=ButtonVariant.PRIMARY)
        info_btn.clicked.connect(lambda: self.notification_manager.notify(
            "Information", "This is an informational message", NotificationType.INFO
        ))
        types_layout.addWidget(info_btn)

        success_btn = Button("Show Success", variant=ButtonVariant.SUCCESS)
        success_btn.clicked.connect(lambda: self.notification_manager.notify(
            "Success!", "Operation completed successfully", NotificationType.SUCCESS
        ))
        types_layout.addWidget(success_btn)

        warning_btn = Button("Show Warning", variant=ButtonVariant.WARNING)
        warning_btn.clicked.connect(lambda: self.notification_manager.notify(
            "Warning", "Please review this important information", NotificationType.WARNING
        ))
        types_layout.addWidget(warning_btn)

        error_btn = Button("Show Error", variant=ButtonVariant.DANGER)
        error_btn.clicked.connect(lambda: self.notification_manager.notify(
            "Error", "An error occurred during operation", NotificationType.ERROR
        ))
        types_layout.addWidget(error_btn)

        types_group.setLayout(types_layout)
        notif_card.add_widget(types_group)

        # Custom notification
        custom_group = QGroupBox("Custom Notification")
        custom_layout = QVBoxLayout()

        title_input = Input(placeholder="Notification title...")
        message_input = TextArea(placeholder="Notification message...")
        message_input.setMaximumHeight(60)

        duration_layout = QHBoxLayout()
        duration_label = QLabel("Duration (ms):")
        duration_spin = QSpinBox()
        duration_spin.setRange(1000, 10000)
        duration_spin.setValue(3000)
        duration_spin.setSingleStep(500)
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(duration_spin)
        duration_layout.addStretch()

        custom_btn = Button("Show Custom Notification", variant=ButtonVariant.PRIMARY)
        custom_btn.clicked.connect(lambda: self.notification_manager.notify(
            title_input.text() or "Custom Notification",
            message_input.toPlainText() or "This is a custom message",
            NotificationType.INFO,
            duration_spin.value()
        ))

        custom_layout.addWidget(title_input)
        custom_layout.addWidget(message_input)
        custom_layout.addLayout(duration_layout)
        custom_layout.addWidget(custom_btn)

        custom_group.setLayout(custom_layout)
        notif_card.add_widget(custom_group)

        self.content_layout.addWidget(notif_card)
        self.content_layout.addStretch()

    def _setup_buttons_section(self, parent_layout: Any) -> None:
        """Setup buttons section."""
        section_card = Card(title="Buttons", elevated=True)

        # Variants row
        variants_widget = QWidget()
        variants_layout = QHBoxLayout(variants_widget)
        for variant in ButtonVariant:
            btn = Button(
                variant.value.title(),
                variant=variant,
                size=ButtonSize.MEDIUM,
            )
            btn.clicked.connect(lambda checked, v=variant: self._show_message(f"Clicked {v.value}"))
            variants_layout.addWidget(btn)
        section_card.add_widget(QLabel("Button Variants:"))
        section_card.add_widget(variants_widget)

        # Sizes row
        sizes_widget = QWidget()
        sizes_layout = QHBoxLayout(sizes_widget)
        for size in ButtonSize:
            btn = Button(
                size.value.title(),
                variant=ButtonVariant.PRIMARY,
                size=size,
            )
            sizes_layout.addWidget(btn)
        section_card.add_widget(QLabel("Button Sizes:"))
        section_card.add_widget(sizes_widget)

        # Toggle buttons
        toggle_layout = QHBoxLayout()
        toggle_btn = ToggleButton(
            "Toggle Me",
            on_text="Enabled",
            off_text="Disabled",
        )
        toggle_layout.addWidget(toggle_btn)

        # Icon button would require QIcon
        # For demo purposes, use another toggle button instead
        toggle_btn2 = ToggleButton(
            "Feature",
            on_text="On",
            off_text="Off",
        )
        toggle_layout.addWidget(toggle_btn2)

        toggle_widget = QWidget()
        toggle_widget.setLayout(toggle_layout)
        section_card.add_widget(QLabel("Special Buttons:"))
        section_card.add_widget(toggle_widget)

        parent_layout.addWidget(section_card)

    def _setup_inputs_section(self, parent_layout: Any) -> None:
        """Setup inputs section."""
        section_card = Card(title="Input Components", elevated=True)

        section_card.add_widget(QLabel("Text Input:"))
        text_input = Input(
            placeholder="Enter text here...",
        )
        section_card.add_widget(text_input)

        section_card.add_widget(QLabel("Password Input:"))
        password_input = PasswordInput(
            placeholder="Enter password...",
        )
        section_card.add_widget(password_input)

        section_card.add_widget(QLabel("Search Input:"))
        search_input = SearchInput(
            placeholder="Search...",
            instant_search=True,
        )
        search_input.search_triggered.connect(
            lambda text: self._show_message(f"Searching for: {text}")
        )
        section_card.add_widget(search_input)

        section_card.add_widget(QLabel("Text Area:"))
        text_area = TextArea(
            placeholder="Enter multiple lines of text...",
        )
        text_area.setMaximumHeight(100)
        section_card.add_widget(text_area)

        parent_layout.addWidget(section_card)

    def _setup_cards_section(self, parent_layout: Any) -> None:
        """Setup cards section."""
        section_card = Card(title="Card Layouts", elevated=True)

        cards_widget = QWidget()
        cards_layout = QHBoxLayout(cards_widget)

        for i in range(3):
            card = Card(
                title=f"Card {i + 1}",
                elevated=True,
            )
            card_content = QLabel(
                f"This is the content of card {i + 1}.\n"
                "Cards can contain any widget\n"
                "and are great for organizing content."
            )
            card_content.setWordWrap(True)
            card.add_widget(card_content)

            # Add action button to card
            card_btn = Button(f"Action {i + 1}", variant=ButtonVariant.SECONDARY, size=ButtonSize.SMALL)
            card.add_widget(card_btn)

            card.setMinimumWidth(250)
            cards_layout.addWidget(card)

        section_card.add_widget(cards_widget)
        parent_layout.addWidget(section_card)

    def _on_theme_changed(self, theme_name: str) -> None:
        """Handle theme change."""
        self.config_manager.set('ui.theme', theme_name)
        if hasattr(self, 'config_viewer'):
            self._update_config_viewer()
        self._update_config_tabs()

        if self._app and self._app.theme_manager:
            current_theme = self._app.theme_manager.get_current_theme_name()
            if current_theme != theme_name:
                self._app.theme_manager.set_theme(theme_name)
                self._show_notification(f"Theme changed to {theme_name}")

    def _show_message(self, message: str) -> None:
        """Show message dialog."""
        QMessageBox.information(self, "Info", message)

    def _show_notification(self, message: str = None) -> None:
        """Show a notification."""
        if message:
            self.notification_manager.notify("Info", message, NotificationType.INFO)
        else:
            self.notification_manager.notify(
                "Sample Notification",
                "This is a sample notification message",
                NotificationType.SUCCESS
            )

    def _show_dialog(self) -> None:
        """Show various dialogs."""
        dialog = ConfirmDialog(
            "Confirm Action",
            "Are you sure you want to proceed with this action?",
            self
        )
        if dialog.exec():
            self._show_notification("Action confirmed!")
        else:
            self._show_notification("Action cancelled")

    def _show_page(self, page_name: str) -> None:
        """Show page for routing demo."""
        self.route_label.setText(f"Current Route: {page_name}")
        self.history_list.addItem(page_name)

    def _update_counter(self, action_type: str) -> None:
        """Update counter in state."""
        self.store.dispatch(Action(action_type, None))

    def _add_item(self) -> None:
        """Add item to state."""
        text = self.item_input.text()
        if text:
            self.store.dispatch(Action("ADD_ITEM", text))
            self.item_input.clear()

    def _clear_items(self) -> None:
        """Clear all items from state."""
        self.store.dispatch(Action("CLEAR_ITEMS", None))

    def _on_state_change(self, state: dict) -> None:
        """Handle state changes."""
        # Update counter display
        if hasattr(self, 'counter_label'):
            self.counter_label.setText(f"Counter: {state.get('counter', 0)}")

        # Update items list
        if hasattr(self, 'items_list'):
            self.items_list.clear()
            self.items_list.addItems(state.get('items', []))

        # Update state display
        if hasattr(self, 'state_text'):
            self._update_state_display()

    def _update_state_display(self) -> None:
        """Update the state display text."""
        import json
        state = self.store.get_state()
        self.state_text.setPlainText(json.dumps(state, indent=2))

    def _update_config_viewer(self) -> None:
        """Update the configuration viewer with current config."""
        viewer = getattr(self, 'config_viewer', None)
        if not self._is_widget_valid(viewer):
            return
        try:
            import json
            config_data = self.config_manager.config.to_dict()
            formatted_json = json.dumps(config_data, indent=2)
            viewer.setPlainText(formatted_json)
        except Exception as e:
            if self._is_widget_valid(viewer):
                viewer.setPlainText(f"Error displaying config: {e}")

    def _set_config_and_refresh(self, key_input: Input, value_input: Input) -> None:
        """Set configuration value and refresh the viewer."""
        key = key_input.text()
        value = value_input.text()
        if key and value:
            # Try to parse value as JSON for proper types
            try:
                import json
                parsed_value = json.loads(value)
            except (json.JSONDecodeError, ValueError):
                # If not JSON, use as string
                parsed_value = value

            self.config_manager.set(key, parsed_value)
            if key in ('ui.theme', 'ui.font_size'):
                self._apply_runtime_config()
            self._show_notification(f"Configuration updated: {key} = {parsed_value}")

            # Clear inputs
            key_input.clear()
            value_input.clear()

            # Refresh the config viewer
            if hasattr(self, 'config_viewer'):
                self._update_config_viewer()

    def _save_user_config(self) -> None:
        """Save current configuration to resources directory."""
        try:
            # Save to resources directory
            config_path = self.CONFIG_FILE

            # Ensure directory exists
            self.RESOURCES_DIR.mkdir(exist_ok=True)

            # Get current config excluding defaults
            current_config = self.config_manager.get_config(exclude_defaults=True)
            if '$schema_version' not in current_config:
                current_config['$schema_version'] = self.config_manager.get_config_schema_version()

            # Save to JSON file
            import json
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(current_config, f, indent=2)

            logger.info(f"Configuration saved to: {config_path}")
            self._show_notification(f"Configuration saved to: {config_path}")

            # Update the config viewer to reflect the new saved file
            self._update_config_viewer()

        except Exception as e:
            self._show_notification(f"Error saving config: {e}")

    def _reload_config_from_resources(self) -> None:
        """Reload configuration from resources directory and update viewers."""
        try:
            # Use the built-in reload functionality
            self.config_manager.reload()

            # Update all viewers with the reloaded config
            self._update_config_viewer()
            self._update_config_tabs()
            self._apply_runtime_config()

            logger.info("Configuration reloaded successfully")
            self._show_notification("Configuration reloaded successfully")

        except Exception as e:
            self._show_notification(f"Error reloading config: {e}")
            logger.error(f"Error reloading config: {e}")

    def _update_config_tabs(self) -> None:
        """Update all config tab controls with current config values."""
        config_data = self.config_manager.get_all()
        for prefix, tab in getattr(self, '_config_tab_pages', []):
            if not self._is_widget_valid(tab):
                continue
            tab.update_data(self._filter_config(config_data, prefix))

    def _apply_runtime_config(self) -> None:
        """Apply runtime configuration values to the live application."""
        if not getattr(self, '_app', None):
            return

        theme_manager = getattr(self._app, 'theme_manager', None)
        if theme_manager:
            theme_name = self.config_manager.get('ui.theme')
            if theme_name:
                current_theme = theme_manager.get_current_theme_name()
                if current_theme != theme_name:
                    theme_manager.set_theme(theme_name)
            font_size = self.config_manager.get('ui.font_size')
            self._apply_font_settings(theme_manager, font_size)

    def _create_app_config_tab(self) -> QWidget:
        """Create the application configuration tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # App Name
        app_name_input = QLineEdit()
        app_name_input.setText(self.config_manager.get('app.name', ''))
        app_name_input.setPlaceholderText("Application Name")
        self.config_controls['app.name'] = app_name_input
        layout.addRow("Application Name:", app_name_input)

        # App Version
        app_version_input = QLineEdit()
        app_version_input.setText(self.config_manager.get('app.version', ''))
        app_version_input.setPlaceholderText("1.0.0")
        self.config_controls['app.version'] = app_version_input
        layout.addRow("Version:", app_version_input)

        # Organization
        org_input = QLineEdit()
        org_input.setText(self.config_manager.get('app.organization', ''))
        org_input.setPlaceholderText("Organization Name")
        self.config_controls['app.organization'] = org_input
        layout.addRow("Organization:", org_input)

        # Debug Mode
        debug_check = QCheckBox()
        debug_check.setChecked(self.config_manager.get('app.debug', False))
        self.config_controls['app.debug'] = debug_check
        layout.addRow("Debug Mode:", debug_check)

        return tab

    def _create_ui_config_tab(self) -> QWidget:
        """Create the UI configuration tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Theme Selection
        theme_combo = QComboBox()
        theme_combo.addItems(["light", "dark", "monokai"])
        current_theme = self.config_manager.get('ui.theme', 'light')
        theme_combo.setCurrentText(current_theme)
        self.config_controls['ui.theme'] = theme_combo
        layout.addRow("Theme:", theme_combo)

        # Language
        language_combo = QComboBox()
        language_combo.addItems(["en", "es", "fr", "de", "ja", "zh"])
        current_lang = self.config_manager.get('ui.language', 'en')
        language_combo.setCurrentText(current_lang)
        self.config_controls['ui.language'] = language_combo
        layout.addRow("Language:", language_combo)

        # Font Size
        font_size_spin = QSpinBox()
        font_size_spin.setRange(8, 72)
        font_size_spin.setValue(self.config_manager.get('ui.font_size', 12))
        font_size_spin.setSuffix(" pt")
        self.config_controls['ui.font_size'] = font_size_spin
        layout.addRow("Font Size:", font_size_spin)

        # Window Width
        width_spin = QSpinBox()
        width_spin.setRange(800, 3840)
        width_spin.setValue(self.config_manager.get('ui.window.width', 1400))
        width_spin.setSuffix(" px")
        self.config_controls['ui.window.width'] = width_spin
        layout.addRow("Window Width:", width_spin)

        # Window Height
        height_spin = QSpinBox()
        height_spin.setRange(600, 2160)
        height_spin.setValue(self.config_manager.get('ui.window.height', 900))
        height_spin.setSuffix(" px")
        self.config_controls['ui.window.height'] = height_spin
        layout.addRow("Window Height:", height_spin)

        # Remember Size
        remember_size_check = QCheckBox()
        remember_size_check.setChecked(self.config_manager.get('ui.window.remember_size', True))
        self.config_controls['ui.window.remember_size'] = remember_size_check
        layout.addRow("Remember Window Size:", remember_size_check)

        # Center on Startup
        center_check = QCheckBox()
        center_check.setChecked(self.config_manager.get('ui.window.center_on_startup', True))
        self.config_controls['ui.window.center_on_startup'] = center_check
        layout.addRow("Center on Startup:", center_check)

        # Animations Enabled
        animations_check = QCheckBox()
        animations_check.setChecked(self.config_manager.get('ui.animations.enabled', True))
        self.config_controls['ui.animations.enabled'] = animations_check
        layout.addRow("Enable Animations:", animations_check)

        # Animation Duration
        duration_spin = QSpinBox()
        duration_spin.setRange(50, 1000)
        duration_spin.setValue(self.config_manager.get('ui.animations.duration', 250))
        duration_spin.setSuffix(" ms")
        self.config_controls['ui.animations.duration'] = duration_spin
        layout.addRow("Animation Duration:", duration_spin)

        return tab

    def _create_features_config_tab(self) -> QWidget:
        """Create the features configuration tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Feature toggles
        features = [
            ('features.charts', 'Charts', True),
            ('features.tables', 'Data Tables', True),
            ('features.notifications', 'Notifications', True),
            ('features.state_management', 'State Management', True),
            ('features.routing', 'Routing', True),
            ('features.plugins', 'Plugin System', True),
            ('features.themes', 'Theme System', True),
            ('features.auto_save', 'Auto Save', True),
            ('features.developer_mode', 'Developer Mode', False),
        ]

        for key, label, default in features:
            checkbox = QCheckBox()
            checkbox.setChecked(self.config_manager.get(key, default))
            self.config_controls[key] = checkbox
            layout.addRow(f"Enable {label}:", checkbox)

        return tab

    def _create_performance_config_tab(self) -> QWidget:
        """Create the performance configuration tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Cache Size with slider
        cache_layout = QVBoxLayout()
        cache_spin = QSpinBox()
        cache_spin.setRange(10, 1000)
        cache_spin.setValue(self.config_manager.get('performance.cache_size', 100))
        cache_spin.setSuffix(" MB")

        cache_slider = QSlider(Qt.Horizontal)
        cache_slider.setRange(10, 1000)
        cache_slider.setValue(cache_spin.value())

        # Connect slider and spinbox
        cache_slider.valueChanged.connect(cache_spin.setValue)
        cache_spin.valueChanged.connect(cache_slider.setValue)

        cache_layout.addWidget(cache_spin)
        cache_layout.addWidget(cache_slider)
        cache_widget = QWidget()
        cache_widget.setLayout(cache_layout)

        self.config_controls['performance.cache_size'] = cache_spin
        layout.addRow("Cache Size:", cache_widget)

        # Max Threads
        threads_spin = QSpinBox()
        threads_spin.setRange(1, 64)
        threads_spin.setValue(self.config_manager.get('performance.max_threads', 4))
        self.config_controls['performance.max_threads'] = threads_spin
        layout.addRow("Max Threads:", threads_spin)

        # Lazy Loading
        lazy_check = QCheckBox()
        lazy_check.setChecked(self.config_manager.get('performance.lazy_loading', True))
        self.config_controls['performance.lazy_loading'] = lazy_check
        layout.addRow("Lazy Loading:", lazy_check)

        # Prefetch Data
        prefetch_check = QCheckBox()
        prefetch_check.setChecked(self.config_manager.get('performance.prefetch_data', False))
        self.config_controls['performance.prefetch_data'] = prefetch_check
        layout.addRow("Prefetch Data:", prefetch_check)

        return tab

    def _create_demo_config_tab(self) -> QWidget:
        """Create the demo-specific configuration tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Show Welcome
        welcome_check = QCheckBox()
        welcome_check.setChecked(self.config_manager.get('demo.show_welcome', True))
        self.config_controls['demo.show_welcome'] = welcome_check
        layout.addRow("Show Welcome Screen:", welcome_check)

        # Sample Data Size with slider
        data_layout = QVBoxLayout()
        data_spin = QSpinBox()
        data_spin.setRange(100, 10000)
        data_spin.setValue(self.config_manager.get('demo.sample_data_size', 1000))

        data_slider = QSlider(Qt.Horizontal)
        data_slider.setRange(100, 10000)
        data_slider.setValue(data_spin.value())

        # Connect slider and spinbox
        data_slider.valueChanged.connect(data_spin.setValue)
        data_spin.valueChanged.connect(data_slider.setValue)

        data_layout.addWidget(data_spin)
        data_layout.addWidget(data_slider)
        data_widget = QWidget()
        data_widget.setLayout(data_layout)

        self.config_controls['demo.sample_data_size'] = data_spin
        layout.addRow("Sample Data Size:", data_widget)

        # Enable Tooltips
        tooltips_check = QCheckBox()
        tooltips_check.setChecked(self.config_manager.get('demo.enable_tooltips', True))
        self.config_controls['demo.enable_tooltips'] = tooltips_check
        layout.addRow("Enable Tooltips:", tooltips_check)

        # Highlight New Features
        highlight_check = QCheckBox()
        highlight_check.setChecked(self.config_manager.get('demo.highlight_new_features', True))
        self.config_controls['demo.highlight_new_features'] = highlight_check
        layout.addRow("Highlight New Features:", highlight_check)

        return tab

    def _apply_config_changes(self) -> None:
        """Apply all configuration changes from the GUI controls."""
        try:
            changes_made = False
            for _prefix, tab in getattr(self, '_config_tab_pages', []):
                if not self._is_widget_valid(tab):
                    continue
                for key, new_value in tab.get_values().items():
                    current_value = self.config_manager.get(key)
                    if current_value != new_value:
                        self.config_manager.set(key, new_value)
                        if key in ('ui.theme', 'ui.font_size'):
                            self._apply_runtime_config()
                        changes_made = True

            if changes_made:
                if hasattr(self, 'config_viewer'):
                    self._update_config_viewer()
                self._apply_runtime_config()
                self._show_notification('Configuration changes applied successfully!')
            else:
                self._show_notification('No changes to apply')

        except Exception as exc:
            self._show_notification(f'Error applying changes: {exc}')
            logger.warning(f'Error applying configuration changes: {exc}')


    def _reset_config_to_defaults(self) -> None:
        """Reset all configuration values to their defaults."""
        try:
            defaults_path = self.DEFAULTS_FILE
            if defaults_path.exists():
                try:
                    import json
                    with open(defaults_path, 'r', encoding='utf-8') as f:
                        defaults = json.load(f)
                    self.config_manager.load_defaults(defaults)
                except Exception as exc:
                    logger.warning(f'Failed to reload defaults from {defaults_path}: {exc}')

            self.config_manager.reset_to_defaults()
            if hasattr(self, 'config_viewer'):
                self._update_config_viewer()
            self._update_config_tabs()
            self._apply_runtime_config()
            self._show_notification('Configuration reset to defaults!')
        except Exception as exc:
            self._show_notification(f'Error resetting config: {exc}')
            logger.warning(f'Error resetting configuration: {exc}')

    def _update_gui_controls(self) -> None:
        """Update all GUI controls with current config values."""
        self._update_config_tabs()

    def _is_widget_valid(self, widget: Any | None) -> bool:
        """Check whether a Qt widget pointer is still valid."""
        return widget is not None and isValid(widget)

    def _apply_font_settings(self, theme_manager: Any, font_size: Any) -> None:
        """Apply font size configuration to the theme and application."""
        try:
            size = int(font_size) if font_size is not None else None
        except (TypeError, ValueError):
            size = None
        if not size or size <= 0:
            return

        app_font = self._app.font()
        if app_font.pointSize() != size:
            app_font.setPointSize(size)
            self._app.setFont(app_font)

        theme = theme_manager.get_theme()
        if not theme:
            return

        current_base = theme.typography.font_size_base
        if current_base == size:
            return

        delta = size - current_base
        typography = theme.typography
        typography.font_size_base = size
        typography.font_size_small = max(6, typography.font_size_small + delta)
        typography.font_size_large = max(6, typography.font_size_large + delta)
        typography.font_size_h1 = max(6, typography.font_size_h1 + delta)
        typography.font_size_h2 = max(6, typography.font_size_h2 + delta)
        typography.font_size_h3 = max(6, typography.font_size_h3 + delta)
        typography.font_size_h4 = max(6, typography.font_size_h4 + delta)
        typography.font_size_h5 = max(6, typography.font_size_h5 + delta)
        typography.font_size_h6 = max(6, typography.font_size_h6 + delta)

        new_stylesheet = theme_manager.get_stylesheet()
        if hasattr(self._app, '_apply_stylesheet'):
            self._app._apply_stylesheet(new_stylesheet)
        elif new_stylesheet != self._app.styleSheet():
            self._app.setStyleSheet(new_stylesheet)

    def _flatten_dict(self, d: dict, parent_key: str = '', sep: str = '.') -> dict:
        """Flatten nested dictionary with dot notation keys."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def _set_config(self, key: str, value: str) -> None:
        """Set configuration value."""
        if key and value:
            self.config_manager.set(key, value)
            if key in ('ui.theme', 'ui.font_size'):
                self._apply_runtime_config()
            self._show_notification(f"Configuration updated: {key} = {value}")

    def _on_route_changed(self, path: str, params: dict) -> None:
        """Handle route change."""
        # Update route label
        if hasattr(self, 'route_label'):
            self.route_label.setText(f"Current Route: {path}")

        # Update route content display
        if hasattr(self, 'route_content'):
            component = self.router.get_route_component()
            if component:
                # Clear old content
                layout = self.route_display.layout()
                while layout.count() > 0:
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

                # Add new component
                layout.addWidget(component)
            else:
                self.route_content.setText(f"Component for route '{path}' loaded")

        # Update history display
        self._update_history_display()

        # Log navigation
        logger.info(f"Navigated to: {path} with params: {params}")

    def _on_navigation_blocked(self, from_path: str, to_path: str) -> None:
        """Handle blocked navigation."""
        self._show_notification(f"Navigation blocked from {from_path} to {to_path}")
        logger.warning(f"Navigation blocked: {from_path} -> {to_path}")

    def _update_history_display(self) -> None:
        """Update the history list display."""
        if hasattr(self, 'history_list'):
            self.history_list.clear()

            # Add current path
            current = self.router.current_path
            if current:
                self.history_list.addItem(f"→ {current} (current)")

            # Add history
            history = self.router.get_history()
            for i, path in enumerate(reversed(history[-5:])):
                self.history_list.addItem(f"  {path}")

    def _handle_back(self) -> None:
        """Handle back navigation."""
        if self.router.back():
            self._show_notification("Navigated back")
        else:
            self._show_notification("No history to go back")

    def _handle_forward(self) -> None:
        """Handle forward navigation."""
        if self.router.forward():
            self._show_notification("Navigated forward")
        else:
            self._show_notification("No history to go forward")

    def _clear_history(self) -> None:
        """Clear navigation history."""
        self.router.clear_history()
        self._update_history_display()
        self._show_notification("History cleared")


def main() -> None:
    """Run the demo application."""
    from qtframework.utils import setup_logging

    setup_logging()

    sys.exit(
        Application.create_and_run(
            DemoWindow,
            app_name="QtFrameworkCompleteDemo",
            org_name="QtFramework",
        )
    )


if __name__ == "__main__":
    main()
