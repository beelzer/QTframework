"""Example application demonstrating Qt Framework usage."""

from __future__ import annotations

import sys
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from PySide6.QtCore import Qt, QTimer
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
)

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
)
from qtframework.widgets.advanced.notifications import NotificationType
from qtframework.state import Store, Action
from qtframework.navigation import Router, Navigator, Route
from qtframework.config import ConfigManager
from qtframework.plugins import PluginManager
from qtframework.utils.logger import get_logger

logger = get_logger(__name__)


class DemoWindow(BaseWindow):
    """Demo window showcasing framework features."""

    def __init__(self, application: Application | None = None) -> None:
        """Initialize demo window."""
        super().__init__(application, title="Qt Framework Complete Demo")
        self.notification_manager = NotificationManager(self)

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
            Route(path="/state", component=lambda: QLabel("<h2>State Management Page</h2>\nRedux-style state management with actions and reducers"), name="state"),
            Route(path="/config", component=lambda: QLabel("<h2>Configuration Page</h2>\nFlexible configuration management system"), name="config"),
        ]

        for route in routes:
            self.router.add_route(route)

        # Connect router signals
        self.router.route_changed.connect(self._on_route_changed)
        self.router.navigation_blocked.connect(self._on_navigation_blocked)

    def _setup_config(self) -> None:
        """Setup configuration management."""
        # Try to load config from file if it exists
        config_file = Path("demo_config.json")
        if config_file.exists():
            self.config_manager.load_file(config_file)

        # Set default configuration values
        self.config_manager.config.set("app.name", "Qt Framework Demo")
        self.config_manager.config.set("app.version", "1.0.0")
        self.config_manager.config.set("features.charts", True)
        self.config_manager.config.set("features.tables", True)
        self.config_manager.config.set("features.notifications", True)

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
        data_table.row_selected.connect(lambda row: print(f"Selected employee at row {row}"))
        data_table.cell_edited.connect(lambda row, col, text: print(f"Cell edited: Row {row}, Col {col}, New value: {text}"))
        data_table.row_double_clicked.connect(lambda row: print(f"Double-clicked employee at row {row}"))

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
        tree_table.item_selected.connect(lambda item: print(f"Selected tree item: {item}"))
        tree_table.item_expanded.connect(lambda item: print(f"Expanded tree item: {item}"))
        tree_table.item_double_clicked.connect(lambda item: print(f"Double-clicked tree item: {item}"))

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

        info = QLabel("The framework includes a flexible configuration management system with multiple providers.")
        info.setWordWrap(True)
        config_card.add_widget(info)

        # Current config
        config_group = QGroupBox("Current Configuration")
        config_layout = QVBoxLayout()

        config_items = [
            f"app.name: {self.config_manager.config.get('app.name', 'Not set')}",
            f"app.version: {self.config_manager.config.get('app.version', 'Not set')}",
            f"features.charts: {self.config_manager.config.get('features.charts', False)}",
            f"features.tables: {self.config_manager.config.get('features.tables', False)}",
            f"features.notifications: {self.config_manager.config.get('features.notifications', False)}",
        ]

        for item in config_items:
            config_layout.addWidget(QLabel(item))

        config_group.setLayout(config_layout)
        config_card.add_widget(config_group)

        # Config editor
        editor_group = QGroupBox("Configuration Editor")
        editor_layout = QVBoxLayout()

        key_input = Input(placeholder="Config key (e.g., app.name)")
        value_input = Input(placeholder="Config value")

        set_btn = Button("Set Configuration", variant=ButtonVariant.PRIMARY)
        set_btn.clicked.connect(lambda: self._set_config(key_input.text(), value_input.text()))

        editor_layout.addWidget(QLabel("Key:"))
        editor_layout.addWidget(key_input)
        editor_layout.addWidget(QLabel("Value:"))
        editor_layout.addWidget(value_input)
        editor_layout.addWidget(set_btn)

        editor_group.setLayout(editor_layout)
        config_card.add_widget(editor_group)

        self.content_layout.addWidget(config_card)
        self.content_layout.addStretch()

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
        if self._app and self._app.theme_manager:
            # Check if theme is already set to prevent infinite recursion
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

    def _set_config(self, key: str, value: str) -> None:
        """Set configuration value."""
        if key and value:
            self.config_manager.config.set(key, value)
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