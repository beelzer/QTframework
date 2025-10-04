# Instructions for Building PServer Manager Using QTframework as a Submodule

This document provides detailed instructions for creating the PServer Manager application using the QTframework as a Git submodule. Follow these steps to set up your project structure and leverage the framework's features.

**Important**: This project uses `uv` for Python package management, which is faster and more reliable than pip.

## Project Setup

### 1. Create Your App Repository

```bash
# Create new directory for your app
mkdir pserver-manager
cd pserver-manager

# Initialize git repository
git init

# Add QTframework as a submodule
git submodule add https://github.com/beelzer/QTframework.git qtframework

# Initialize and update the submodule
git submodule update --init --recursive
```

### 2. Initialize UV Project

```bash
# Initialize uv project (creates pyproject.toml and .python-version)
uv init --name pserver-manager --python 3.13

# Add the framework as an editable dependency
# This installs qtframework and all its dependencies
uv add --editable ./qtframework
```

### 3. Create Your App Structure

```bash
# Create main app directory structure
mkdir -p pserver_manager/plugins
mkdir -p pserver_manager/themes
mkdir -p pserver_manager/icons
mkdir -p pserver_manager/pages
mkdir -p pserver_manager/resources

# Create empty __init__.py files
# On Windows:
type nul > pserver_manager/__init__.py
type nul > pserver_manager/pages/__init__.py

# On Linux/macOS:
# touch pserver_manager/__init__.py
# touch pserver_manager/pages/__init__.py
```

Your directory structure should look like:

```
pserver-manager/
├── .git/
├── .gitmodules
├── .python-version          # Python version (3.13)
├── pyproject.toml           # UV project configuration
├── uv.lock                  # UV lock file
├── qtframework/             # Submodule
│   ├── src/
│   │   └── qtframework/
│   ├── resources/
│   │   ├── themes/
│   │   │   ├── monokai.yaml
│   │   │   └── nord.yaml
│   │   └── icons/
│   ├── tests/
│   └── pyproject.toml
├── pserver_manager/
│   ├── __init__.py
│   ├── main.py              # Your main application entry point
│   ├── pages/               # Your custom pages
│   │   └── __init__.py
│   ├── plugins/             # Your custom plugins
│   ├── themes/              # Your custom themes (override built-in)
│   └── icons/               # Your custom icons
├── .gitignore
└── README.md
```

## Framework Overview

### Core Components

The QTframework provides several key components:

1. **Application**: Main application class with theme and context management
2. **ResourceManager**: Manages themes, icons, and translations with configurable paths
3. **ThemeManager**: Handles theme switching and stylesheet generation
4. **PluginManager**: Loads and manages plugins from multiple directories
5. **BaseWindow**: Base window class with framework integration
6. **Widgets**: Pre-built components (buttons, inputs, containers, etc.)
7. **State Management**: Redux-like state management system
8. **Navigation**: Routing and navigation system
9. **Configuration**: YAML-based configuration with validation
10. **Internationalization**: Translation support with Babel

### Built-in Themes

The framework includes these built-in themes:

- `light` - Standard light theme
- `dark` - Standard dark theme
- `monokai` - Dark code editor theme
- `nord` - Arctic-inspired theme

You can override these by creating YAML files with the same name in your `my_app/themes/` directory.

## Creating Your Application

### Basic Application Structure

Create `pserver_manager/main.py`:

```python
"""Main application entry point."""

from __future__ import annotations

import sys
from pathlib import Path

from qtframework import Application
from qtframework.core import BaseWindow
from qtframework.plugins import PluginManager
from qtframework.utils import ResourceManager
from qtframework.widgets import Button, VBox


class MainWindow(BaseWindow):
    """Main application window."""

    def __init__(self, application: Application) -> None:
        """Initialize main window.

        Args:
            application: Application instance
        """
        super().__init__(application=application)
        self.setWindowTitle("PServer Manager")
        self.setMinimumSize(1024, 768)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # Create main layout
        layout = VBox()

        # Add some widgets
        welcome_button = Button("Welcome to PServer Manager!")
        welcome_button.clicked.connect(self._on_welcome_clicked)
        layout.add_widget(welcome_button)

        # Set central widget
        self.set_content(layout)

    def _on_welcome_clicked(self) -> None:
        """Handle welcome button click."""
        print("Welcome button clicked!")


def main() -> int:
    """Run the application.

    Returns:
        Application exit code
    """
    # Setup custom resource manager
    resource_manager = ResourceManager()

    # Add custom resource paths (searched before framework paths)
    resource_manager.add_search_path("themes", Path("pserver_manager/themes"))
    resource_manager.add_search_path("icons", Path("pserver_manager/icons"))
    resource_manager.add_search_path("translations", Path("pserver_manager/translations"))

    # Create application with custom resources
    app = Application(
        argv=sys.argv,
        app_name="PServerManager",
        org_name="PServerManager",
        org_domain="pservermanager.local",
        resource_manager=resource_manager,
    )

    # Setup plugin manager
    plugin_manager = PluginManager(application=app)
    plugin_manager.add_plugin_path(Path("pserver_manager/plugins"))

    # Discover and load plugins
    available_plugins = plugin_manager.discover_plugins()
    for plugin_metadata in available_plugins:
        print(f"Found plugin: {plugin_metadata.id} - {plugin_metadata.name}")
        plugin_manager.load_plugin(plugin_metadata.id)
        plugin_manager.activate_plugin(plugin_metadata.id)

    # Set theme (uses custom theme if exists, otherwise built-in)
    app.theme_manager.set_theme("dark")

    # Create and show main window
    window = MainWindow(application=app)
    window.show()

    # Run application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
```

## Creating Custom Themes

### Theme File Structure

Create a custom theme in `my_app/themes/my_theme.yaml`:

```yaml
name: "my_theme"
display_name: "My Custom Theme"
description: "A custom theme for my application"
author: "Your Name"
version: "1.0.0"

tokens:
  semantic:
    # Background colors
    bg_primary: "#1e1e2e"
    bg_secondary: "#313244"
    bg_tertiary: "#45475a"
    bg_elevated: "#585b70"
    bg_overlay: "rgba(0, 0, 0, 0.7)"

    # Foreground/Text colors
    fg_primary: "#cdd6f4"
    fg_secondary: "#bac2de"
    fg_tertiary: "#a6adc8"
    fg_on_accent: "#ffffff"
    fg_on_dark: "#ffffff"
    fg_on_light: "#1e1e2e"

    # Action/Interactive colors
    action_primary: "#89b4fa"
    action_primary_hover: "#74c7ec"
    action_primary_active: "#89dceb"
    action_secondary: "#cba6f7"
    action_secondary_hover: "#f5c2e7"
    action_secondary_active: "#eba0ac"

    # Feedback colors
    feedback_success: "#a6e3a1"
    feedback_warning: "#f9e2af"
    feedback_error: "#f38ba8"
    feedback_info: "#94e2d5"

    # Border colors
    border_default: "#45475a"
    border_subtle: "#313244"
    border_strong: "#585b70"
    border_focus: "#89b4fa"

    # State colors
    state_hover: "#313244"
    state_active: "#45475a"
    state_selected: "#89b4fa"
    state_disabled: "#6c7086"

  spacing:
    space_1: 4
    space_2: 8
    space_3: 12
    space_4: 16
    space_6: 24
    space_8: 32
    space_12: 48
    space_16: 64

  typography:
    font_family_default: "Segoe UI, system-ui, sans-serif"
    font_family_mono: "Consolas, monospace"
    font_size_xs: 10
    font_size_sm: 12
    font_size_md: 14
    font_size_lg: 16
    font_size_xl: 18
    font_size_2xl: 20
    font_size_3xl: 24
    font_size_4xl: 32
    font_size_5xl: 40

  borders:
    radius_sm: 4
    radius_md: 8
    radius_lg: 12
    radius_xl: 16
    radius_full: 9999
    width_thin: 1
    width_medium: 2
    width_thick: 3

custom_styles:
  "QWidget[custom-widget='true']": |
    background-color: #f5c2e7;
    border-radius: 8px;
    padding: 16px;
```

### Override Built-in Theme

To override a built-in theme (e.g., `light`), create `my_app/themes/light.yaml` with the same structure. Your custom version will take precedence.

## Creating Custom Plugins

### Plugin Structure

Each plugin must be in its own directory with:

1. `main.py` - Contains the plugin implementation
2. `plugin.json` - Plugin metadata

Create `my_app/plugins/example_plugin/plugin.json`:

```json
{
  "id": "example_plugin",
  "name": "Example Plugin",
  "description": "An example plugin demonstrating plugin capabilities",
  "version": "1.0.0",
  "author": "Your Name",
  "dependencies": []
}
```

Create `my_app/plugins/example_plugin/main.py`:

```python
"""Example plugin implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtframework.plugins import Plugin, PluginMetadata, PluginState


if TYPE_CHECKING:
    from qtframework.core.application import Application


class ExamplePlugin(Plugin):
    """Example plugin demonstrating plugin capabilities."""

    def __init__(self) -> None:
        """Initialize the plugin."""
        metadata = PluginMetadata(
            id="example_plugin",
            name="Example Plugin",
            description="An example plugin",
            version="1.0.0",
            author="Your Name",
        )
        super().__init__(metadata)

    def initialize(self) -> bool:
        """Initialize the plugin.

        Returns:
            True if initialization was successful
        """
        print(f"Initializing {self.metadata.name}")
        return True

    def activate(self) -> bool:
        """Activate the plugin.

        Returns:
            True if activation was successful
        """
        print(f"Activating {self.metadata.name}")

        # Access application if needed
        if self._application:
            print(f"Current theme: {self._application.context.get('theme')}")

        return True

    def deactivate(self) -> bool:
        """Deactivate the plugin.

        Returns:
            True if deactivation was successful
        """
        print(f"Deactivating {self.metadata.name}")
        return True

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        print(f"Cleaning up {self.metadata.name}")


def create_plugin() -> Plugin:
    """Create plugin instance.

    This function is required and must be named 'create_plugin'.

    Returns:
        Plugin instance
    """
    return ExamplePlugin()
```

## Using Framework Widgets

### Available Widgets

The framework provides these pre-built widgets:

**Basic Widgets:**

- `Button` - Enhanced button with variants (primary, secondary, danger, success)
- `Input` - Text input with validation
- `PasswordInput` - Password input with show/hide toggle
- `Select` - Dropdown/combo box
- `CheckBox` - Checkbox
- `RadioButton` - Radio button

**Layout Containers:**

- `VBox` - Vertical box layout
- `HBox` - Horizontal box layout
- `Card` - Card container
- `InfoCard` - Card with icon and info layout
- `FlowLayout` - Flow layout (wraps items)
- `SidebarLayout` - Sidebar + content layout

**Advanced Widgets:**

- `Table` - Data table with sorting/filtering
- `TabWidget` - Tabbed interface
- `NotificationManager` - Toast notifications
- `PageManager` - Page-based navigation
- `ChartWidget` - Charts (line, bar, pie)

### Example: Using Widgets

```python
from qtframework.widgets import Button, Card, HBox, Input, VBox


def create_form_page():
    """Create a form page with various widgets."""
    # Main layout
    layout = VBox(spacing=16)

    # Card container
    card = Card(title="User Information")
    card_layout = VBox(spacing=12)

    # Input fields
    name_input = Input(placeholder="Enter your name")
    email_input = Input(placeholder="Enter your email")

    # Buttons
    button_row = HBox(spacing=8)
    submit_btn = Button("Submit", variant="primary")
    cancel_btn = Button("Cancel", variant="secondary")

    button_row.add_widget(submit_btn)
    button_row.add_widget(cancel_btn)

    # Add to card
    card_layout.add_widget(name_input)
    card_layout.add_widget(email_input)
    card_layout.add_widget(button_row)

    card.set_content(card_layout)
    layout.add_widget(card)

    return layout
```

## Resource Management

### How Resources Work

The `ResourceManager` searches for resources in this order:

1. **User custom paths** (added via `add_search_path`)
2. **Framework built-in paths** (automatically included)

This means:

- You automatically get all built-in themes, icons, and resources
- Your custom resources override built-in ones with the same name
- You can extend the framework with additional resources

### Example: Using Custom Icons

```python
# Add custom icon path
resource_manager.add_search_path("icons", Path("my_app/icons"))

# Find icon (searches custom path first, then framework)
icon_path = resource_manager.find_resource("icons", "my-icon.svg")

# Use in stylesheet
icon_url = resource_manager.get_resource_url("icons", "my-icon.svg")
```

## State Management

### Using the State Store

```python
from qtframework.state import Store, Action


# Define actions
class SetUserAction(Action):
    """Action to set user data."""

    def __init__(self, user_data: dict):
        super().__init__("SET_USER", user_data)


# Create reducer
def user_reducer(state: dict, action: Action) -> dict:
    """Reduce user state."""
    if action.type == "SET_USER":
        return {**state, "user": action.payload}
    return state


# Use in your app
store = Store(initial_state={"user": None}, reducer=user_reducer)

# Subscribe to changes
def on_state_change(state):
    print(f"User: {state.get('user')}")

store.subscribe(on_state_change)

# Dispatch actions
store.dispatch(SetUserAction({"name": "John", "email": "john@example.com"}))
```

## Configuration Management

### Create Configuration File

Create `config.yaml` in your app root:

```yaml
app:
  name: "My QTFramework App"
  version: "1.0.0"
  theme: "dark"

database:
  host: "localhost"
  port: 5432
  name: "myapp_db"

features:
  enable_plugins: true
  enable_analytics: false
```

### Load Configuration

```python
from qtframework.config import ConfigManager, Config
from pathlib import Path


# Create config schema
class AppConfig(Config):
    """Application configuration."""

    app_name: str = "MyApp"
    app_version: str = "1.0.0"
    theme: str = "light"
    enable_plugins: bool = True


# Load config
config_manager = ConfigManager(
    app_name="MyApp",
    config_class=AppConfig,
)

config = config_manager.load_config(Path("config.yaml"))
print(f"App: {config.app_name} v{config.app_version}")
print(f"Theme: {config.theme}")
```

## Navigation System

### Using the Router

```python
from qtframework.navigation import Router, Route
from qtframework.widgets import VBox


# Define pages
class HomePage(VBox):
    """Home page."""

    def __init__(self):
        super().__init__()
        # Add widgets
        ...


class SettingsPage(VBox):
    """Settings page."""

    def __init__(self):
        super().__init__()
        # Add widgets
        ...


# Setup router
router = Router()
router.register_route(Route("home", "/", HomePage))
router.register_route(Route("settings", "/settings", SettingsPage))

# Navigate
router.navigate("/settings")
```

## Development Workflow

### Running Your App

```bash
# Run your app using uv
uv run python pserver_manager/main.py

# Or run as a module
uv run python -m pserver_manager.main

# For development with auto-reload (if implemented)
uv run python pserver_manager/main.py --dev
```

### Updating the Framework

```bash
# Pull latest framework changes
cd qtframework
git pull origin master
cd ..

# Update your repo's submodule reference
git add qtframework
git commit -m "Update framework to latest version"
```

### Making Framework Changes

If you find bugs or need features while building your app:

```bash
# Make changes in the submodule
cd qtframework
# Edit files, test changes
git add .
git commit -m "Fix bug found while building PServer Manager"
git push

# Back to your app
cd ..

# Reinstall framework with changes
uv sync --reinstall-package qtframework

# Update submodule reference
git add qtframework
git commit -m "Update to framework with bug fix"
```

## Testing

### Running Framework Tests

```bash
# Run framework tests to ensure nothing broke
cd qtframework
uv run pytest tests/

# Run specific tests
uv run pytest tests/unit/test_application.py -v
```

### Creating Your App Tests

Create `tests/` directory in your app:

```python
# tests/test_main.py
import pytest
from pserver_manager.main import MainWindow
from qtframework import Application


def test_main_window_creation(qtbot):
    """Test main window can be created."""
    app = Application(app_name="TestApp")
    window = MainWindow(application=app)

    qtbot.addWidget(window)
    assert window.windowTitle() == "PServer Manager"
```

Run your tests with UV:

```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=pserver_manager --cov-report=html

# Run specific test file
uv run pytest tests/test_main.py -v
```

## Dependencies

### Managing Dependencies with UV

```bash
# Add dependencies using uv
uv add requests
uv add pillow

# Add development dependencies
uv add --dev pytest
uv add --dev pytest-qt
uv add --dev ruff

# Add optional dependencies
uv add --optional psutil  # For server monitoring
uv add --optional paramiko  # For SSH connections

# Install all dependencies (including framework)
uv sync

# Update dependencies
uv lock --upgrade
```

Your `pyproject.toml` will look like:

```toml
[project]
name = "pserver-manager"
version = "0.1.0"
description = "PServer Manager - Server management application"
requires-python = ">=3.13"
dependencies = [
    "qtframework @ {path = 'qtframework', editable = true}",
    "requests>=2.31.0",
    "pillow>=10.0.0",
]

[project.optional-dependencies]
server = [
    "psutil>=5.9.0",
    "paramiko>=3.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Version Control

### .gitignore

Create `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# App specific
config.local.yaml
*.log
```

### Commit Workflow

```bash
# Add your app files
git add my_app/ tests/ requirements.txt README.md

# Commit your changes
git commit -m "Add main application structure"

# When you update the framework submodule
git add qtframework
git commit -m "Update framework to version X.Y.Z"

# Push everything
git push origin main
```

## Cloning Your App (For Other Developers)

```bash
# Clone with submodules
git clone --recursive https://github.com/yourusername/pserver-manager.git
cd pserver-manager

# Or if already cloned without --recursive:
git submodule update --init --recursive

# Install uv if not already installed
# On Windows (PowerShell):
# irm https://astral.sh/uv/install.ps1 | iex

# On macOS/Linux:
# curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync all dependencies (installs framework + dependencies)
uv sync

# Run the app
uv run python pserver_manager/main.py
```

## Common Patterns

### Accessing Application Context

```python
# Get application instance
app = Application.instance()

# Access context
theme = app.context.get("theme")
app.context.set("user_logged_in", True)

# Access theme manager
app.theme_manager.set_theme("dark")

# Access resource manager
app.resource_manager.add_search_path("themes", Path("extra/themes"))
```

### Theme Switching

```python
from qtframework.widgets import Button, ComboBox, HBox


def create_theme_switcher():
    """Create theme switcher widget."""
    layout = HBox()

    # Get available themes
    app = Application.instance()
    themes = list(app.theme_manager.get_all_themes().keys())

    # Create combo box
    theme_combo = ComboBox()
    theme_combo.addItems(themes)

    # Connect to theme change
    def on_theme_changed(theme_name):
        app.theme_manager.set_theme(theme_name)

    theme_combo.currentTextChanged.connect(on_theme_changed)

    layout.add_widget(theme_combo)
    return layout
```

### Using Notifications

```python
from qtframework.widgets.advanced import NotificationManager, NotificationType


# Create notification manager
notifications = NotificationManager(parent_widget)

# Show notifications
notifications.show("Success!", NotificationType.SUCCESS, duration=3000)
notifications.show("Warning!", NotificationType.WARNING, duration=5000)
notifications.show("Error occurred", NotificationType.ERROR, duration=0)  # Persistent
notifications.show("Info message", NotificationType.INFO, duration=4000)
```

## Debugging

### Enable Framework Logging

```python
from qtframework.utils import setup_logging
import logging


# Setup logging at application start
setup_logging(level=logging.DEBUG)

# Now you'll see debug messages from the framework
```

### Common Issues

#### Issue: Submodule not found

```bash
git submodule update --init --recursive
```

#### Issue: Changes to framework not reflected

```bash
uv sync --reinstall-package qtframework
```

#### Issue: UV commands not working

```bash
# Make sure uv is installed
uv --version

# If not installed, install it:
# Windows: irm https://astral.sh/uv/install.ps1 | iex
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Issue: Theme not loading

- Check theme YAML syntax
- Verify theme file is in correct directory
- Check logs for theme loading errors

#### Issue: Plugin not loading

- Ensure `plugin.json` exists and is valid JSON
- Verify `main.py` has `create_plugin()` function
- Check plugin path is added before `discover_plugins()`

## Best Practices

1. **Use UV for all dependency management**: Always use `uv add` instead of `pip install`
2. **Keep submodule updated**: Regularly pull framework updates with `cd qtframework && git pull`
3. **Lock dependencies**: Run `uv lock` after adding dependencies to ensure reproducible builds
4. **Test after framework updates**: Run `uv run pytest` after updating the framework
5. **Document custom themes**: Add comments to theme YAML files
6. **Organize plugins**: One plugin per directory with clear purpose
7. **Use type hints**: Leverage the framework's type hints for better IDE support
8. **Follow framework patterns**: Use framework widgets and layouts for consistency
9. **Version your resources**: Track custom themes/icons in git
10. **Create migration path**: If framework changes, document how to migrate your app
11. **Commit lock file**: Always commit `uv.lock` to ensure team has same dependencies

## Additional Resources

- **Framework Source**: `qtframework/src/qtframework/`
- **Framework Tests**: `qtframework/tests/` (examples of usage)
- **Framework Examples**: `qtframework/examples/` (if available)
- **Built-in Themes**: `qtframework/resources/themes/`

## Getting Help

When asking for help building your app:

1. Specify you're using QTframework as a submodule
2. Provide your app structure and relevant code
3. Include error messages and logs
4. Mention which framework version (commit hash) you're using
5. Describe what you're trying to achieve

## Summary

You now have a complete guide to:

- ✅ Set up QTframework as a submodule
- ✅ Create custom themes that override built-in ones
- ✅ Build custom plugins
- ✅ Use framework widgets and layouts
- ✅ Manage resources (icons, themes, translations)
- ✅ Structure your application properly
- ✅ Follow best practices for development

Start by creating the basic structure, then incrementally add features as you build your app. The framework handles themes, state, navigation, and widgets - you focus on your app's unique functionality!
