# Plugins Guide

Qt Framework includes a powerful plugin system that allows you to extend functionality and create modular, reusable components.

## Overview

The plugin system provides:

- **Dynamic Loading** - Load plugins at runtime
- **Lifecycle Management** - Initialize, activate, deactivate, and unload plugins
- **Dependency Resolution** - Handle plugin dependencies automatically
- **Plugin Discovery** - Auto-discover plugins in directories
- **Hot Reload** - Reload plugins during development
- **Configuration** - Per-plugin configuration support

## Quick Start

### Creating a Plugin

```python
from qtframework.plugins import Plugin, PluginMetadata

class MyPlugin(Plugin):
    """A simple example plugin."""

    metadata = PluginMetadata(
        name="my_plugin",
        display_name="My Plugin",
        version="1.0.0",
        author="Your Name",
        description="Does something useful",
        dependencies=[]
    )

    def initialize(self, context):
        """Called when plugin is loaded."""
        print(f"Initializing {self.metadata.display_name}")
        self.context = context

    def activate(self):
        """Called when plugin is activated."""
        print("Plugin activated")
        # Register services, add menu items, etc.

    def deactivate(self):
        """Called when plugin is deactivated."""
        print("Plugin deactivated")
        # Clean up resources

    def unload(self):
        """Called when plugin is unloaded."""
        print("Plugin unloaded")
```

### Using the Plugin Manager

```python
from qtframework.plugins import PluginManager
from qtframework.core import Application

app = Application()
plugin_manager = PluginManager(app.context)

# Load plugins from directory
plugin_manager.discover_plugins("plugins/")

# Load specific plugin
plugin_manager.load_plugin("my_plugin")

# Activate plugin
plugin_manager.activate_plugin("my_plugin")

# Get plugin instance
plugin = plugin_manager.get_plugin("my_plugin")

# List all plugins
for name, plugin in plugin_manager.get_all_plugins().items():
    print(f"{name}: {plugin.metadata.display_name}")

# Deactivate and unload
plugin_manager.deactivate_plugin("my_plugin")
plugin_manager.unload_plugin("my_plugin")
```

## Plugin Structure

### Plugin Class

```python
from qtframework.plugins import Plugin, PluginMetadata

class AdvancedPlugin(Plugin):
    """Advanced plugin example."""

    metadata = PluginMetadata(
        name="advanced_plugin",
        display_name="Advanced Plugin",
        version="2.0.0",
        author="Developer Name",
        author_email="dev@example.com",
        description="An advanced plugin with many features",
        url="https://github.com/user/plugin",
        license="MIT",
        dependencies=["base_plugin>=1.0.0"],
        python_requires=">=3.9",
        tags=["utility", "enhancement"]
    )

    def __init__(self):
        super().__init__()
        self.config = {}
        self.service = None

    def initialize(self, context):
        """Initialize plugin with application context."""
        self.context = context

        # Load configuration
        self.config = context.config.get_plugin_config(self.metadata.name)

        # Register with context
        context.register_service("my_service", self.create_service())

    def activate(self):
        """Activate plugin and make it functional."""
        # Start service
        self.service = self.context.get_service("my_service")
        self.service.start()

        # Add to application menu
        self.add_menu_items()

        # Register event handlers
        self.register_handlers()

    def deactivate(self):
        """Deactivate plugin but keep it loaded."""
        # Stop service
        if self.service:
            self.service.stop()

        # Remove menu items
        self.remove_menu_items()

        # Unregister handlers
        self.unregister_handlers()

    def unload(self):
        """Clean up before unloading."""
        # Unregister from context
        self.context.unregister_service("my_service")

        # Save any persistent state
        self.save_state()

    def create_service(self):
        """Factory method for service creation."""
        return MyService(self.config)

    def add_menu_items(self):
        """Add plugin items to application menu."""
        menu_service = self.context.get_service("menu_service")
        menu_service.add_item("Tools", "My Plugin", self.on_menu_click)

    def remove_menu_items(self):
        """Remove plugin menu items."""
        menu_service = self.context.get_service("menu_service")
        menu_service.remove_item("Tools", "My Plugin")

    def on_menu_click(self):
        """Handle menu item click."""
        print("Plugin menu item clicked!")

    def register_handlers(self):
        """Register event handlers."""
        event_bus = self.context.get_service("event_bus")
        event_bus.subscribe("app.startup", self.on_app_startup)

    def unregister_handlers(self):
        """Unregister event handlers."""
        event_bus = self.context.get_service("event_bus")
        event_bus.unsubscribe("app.startup", self.on_app_startup)

    def on_app_startup(self, event):
        """Handle application startup."""
        print("Application started!")

    def save_state(self):
        """Save plugin state."""
        # Save configuration or state
        pass
```

### Plugin Metadata

```python
from qtframework.plugins import PluginMetadata

metadata = PluginMetadata(
    # Required
    name="my_plugin",                    # Unique identifier
    display_name="My Plugin",            # Human-readable name
    version="1.0.0",                     # Semantic version

    # Optional
    author="Developer Name",
    author_email="dev@example.com",
    description="Plugin description",
    url="https://github.com/user/repo",
    license="MIT",
    dependencies=[                       # Other plugins required
        "base_plugin>=1.0.0",
        "utils_plugin>=2.1.0,<3.0.0"
    ],
    python_requires=">=3.9",            # Python version requirement
    tags=["utility", "tools"],          # Categorization tags
    icon="path/to/icon.png",            # Plugin icon
    settings_widget=SettingsWidget,     # Custom settings UI
)
```

## Plugin Dependencies

### Declaring Dependencies

```python
metadata = PluginMetadata(
    name="dependent_plugin",
    version="1.0.0",
    dependencies=[
        "base_plugin>=1.0.0",           # Minimum version
        "utils_plugin>=2.0.0,<3.0.0",   # Version range
        "optional_plugin",              # Any version
    ]
)
```

### Loading with Dependencies

```python
# Plugin manager resolves dependencies automatically
plugin_manager.load_plugin("dependent_plugin")
# This will load base_plugin and utils_plugin first
```

### Optional Dependencies

```python
class MyPlugin(Plugin):
    def initialize(self, context):
        # Check if optional dependency is available
        if plugin_manager.has_plugin("optional_plugin"):
            optional = plugin_manager.get_plugin("optional_plugin")
            # Use optional plugin
        else:
            # Fall back to basic functionality
            pass
```

## Plugin Discovery

### Auto-discovery

```python
# Discover plugins in directory
plugin_manager.discover_plugins("plugins/")

# Discover in multiple directories
plugin_manager.discover_plugins([
    "plugins/",
    "user_plugins/",
    "~/.myapp/plugins/"
])

# Discover with pattern
plugin_manager.discover_plugins("plugins/", pattern="*_plugin.py")
```

### Manual Registration

```python
# Register plugin class directly
plugin_manager.register_plugin_class(MyPlugin)

# Register from module
plugin_manager.register_plugin_from_module("myapp.plugins.my_plugin", "MyPlugin")
```

## Plugin Configuration

### Plugin Settings

```python
class ConfigurablePlugin(Plugin):
    """Plugin with configuration."""

    DEFAULT_CONFIG = {
        "enabled": True,
        "interval": 60,
        "api_key": "",
        "options": {
            "verbose": False,
            "timeout": 30
        }
    }

    def initialize(self, context):
        # Load config with defaults
        self.config = context.config.get_plugin_config(
            self.metadata.name,
            default=self.DEFAULT_CONFIG
        )

        # Access config values
        self.enabled = self.config.get("enabled")
        self.interval = self.config.get("interval")

    def update_config(self, new_config):
        """Update plugin configuration."""
        self.config.update(new_config)

        # Save to disk
        self.context.config.set_plugin_config(
            self.metadata.name,
            self.config
        )

        # Apply changes
        self.apply_config()

    def apply_config(self):
        """Apply configuration changes."""
        # Reconfigure plugin based on new settings
        pass
```

### Settings UI

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QSpinBox

class PluginSettingsWidget(QWidget):
    """Custom settings UI for plugin."""

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

        # Create UI controls
        self.enabled_check = QCheckBox("Enable Plugin")
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 3600)

        layout = QVBoxLayout()
        layout.addWidget(self.enabled_check)
        layout.addWidget(self.interval_spin)
        self.setLayout(layout)

        # Load current values
        self.load_settings()

    def load_settings(self):
        """Load settings from plugin."""
        self.enabled_check.setChecked(self.plugin.config.get("enabled"))
        self.interval_spin.setValue(self.plugin.config.get("interval"))

    def save_settings(self):
        """Save settings to plugin."""
        new_config = {
            "enabled": self.enabled_check.isChecked(),
            "interval": self.interval_spin.value()
        }
        self.plugin.update_config(new_config)

# Register in metadata
metadata = PluginMetadata(
    name="my_plugin",
    version="1.0.0",
    settings_widget=PluginSettingsWidget
)
```

## Plugin Communication

### Using Application Context

```python
class CommunicatingPlugin(Plugin):
    def initialize(self, context):
        self.context = context

        # Register a service
        context.register_service("my_service", MyService())

    def activate(self):
        # Access another plugin's service
        other_service = self.context.get_service("other_service")
        if other_service:
            other_service.do_something()
```

### Event Bus

```python
class EventPlugin(Plugin):
    def activate(self):
        # Subscribe to events
        event_bus = self.context.get_service("event_bus")
        event_bus.subscribe("data.updated", self.on_data_updated)

        # Publish events
        event_bus.publish("plugin.activated", {
            "plugin": self.metadata.name
        })

    def on_data_updated(self, event):
        """Handle data update event."""
        print(f"Data updated: {event.data}")
```

### Direct Plugin Communication

```python
class ProviderPlugin(Plugin):
    """Provides data to other plugins."""

    def get_data(self):
        return {"key": "value"}

class ConsumerPlugin(Plugin):
    """Consumes data from provider plugin."""

    def activate(self):
        # Get provider plugin
        provider = self.context.plugin_manager.get_plugin("provider_plugin")
        if provider and provider.is_active():
            data = provider.get_data()
            print(f"Got data: {data}")
```

## Hot Reload

Enable hot reload during development:

```python
# Enable hot reload
plugin_manager.enable_hot_reload("plugins/")

# Plugin files will be monitored for changes
# and automatically reloaded when modified

# Disable when done
plugin_manager.disable_hot_reload()
```

## Plugin Hooks

### Defining Hooks

```python
class ExtensiblePlugin(Plugin):
    """Plugin that provides extension points."""

    def __init__(self):
        super().__init__()
        self.hooks = {
            "before_process": [],
            "after_process": [],
            "on_error": []
        }

    def register_hook(self, hook_name, callback):
        """Register a hook callback."""
        if hook_name in self.hooks:
            self.hooks[hook_name].append(callback)

    def process_data(self, data):
        """Process data with hooks."""
        # Call before hooks
        for hook in self.hooks["before_process"]:
            data = hook(data)

        try:
            # Main processing
            result = self._do_process(data)

            # Call after hooks
            for hook in self.hooks["after_process"]:
                result = hook(result)

            return result

        except Exception as e:
            # Call error hooks
            for hook in self.hooks["on_error"]:
                hook(e)
            raise
```

### Using Hooks

```python
class ExtensionPlugin(Plugin):
    """Plugin that extends another plugin."""

    def activate(self):
        # Get extensible plugin
        base_plugin = self.context.plugin_manager.get_plugin("extensible_plugin")

        # Register hooks
        base_plugin.register_hook("before_process", self.transform_input)
        base_plugin.register_hook("after_process", self.transform_output)

    def transform_input(self, data):
        """Transform input data."""
        return {**data, "extended": True}

    def transform_output(self, result):
        """Transform output result."""
        return {**result, "processed_by": self.metadata.name}
```

## Best Practices

1. **Minimal Dependencies** - Keep plugin dependencies minimal
2. **Graceful Degradation** - Handle missing optional dependencies
3. **Clean Lifecycle** - Properly implement all lifecycle methods
4. **Error Handling** - Handle errors gracefully, don't crash the app
5. **Documentation** - Document plugin API and configuration
6. **Version Compatibility** - Use semantic versioning
7. **Resource Cleanup** - Clean up resources in deactivate/unload
8. **Testing** - Write tests for plugin functionality

## Complete Example

```python
from qtframework.core import Application, MainWindow
from qtframework.plugins import Plugin, PluginMetadata, PluginManager
from PySide6.QtWidgets import QAction, QMessageBox

# Define plugin
class HelloPlugin(Plugin):
    """Simple hello world plugin."""

    metadata = PluginMetadata(
        name="hello_plugin",
        display_name="Hello Plugin",
        version="1.0.0",
        author="Developer",
        description="Adds a hello world menu item"
    )

    def initialize(self, context):
        self.context = context
        self.main_window = None
        self.menu_action = None

    def activate(self):
        # Get main window
        self.main_window = self.context.get_service("main_window")

        # Add menu item
        menu_bar = self.main_window.menuBar()
        tools_menu = menu_bar.addMenu("Tools")

        self.menu_action = QAction("Say Hello", self.main_window)
        self.menu_action.triggered.connect(self.say_hello)
        tools_menu.addAction(self.menu_action)

    def deactivate(self):
        # Remove menu item
        if self.menu_action:
            menu_bar = self.main_window.menuBar()
            for menu in menu_bar.findChildren(QMenu):
                menu.removeAction(self.menu_action)

    def say_hello(self):
        """Show hello message."""
        QMessageBox.information(
            self.main_window,
            "Hello",
            "Hello from the plugin!"
        )

# Use plugin
app = Application()
window = MainWindow()

# Setup plugin manager
plugin_manager = PluginManager(app.context)
app.context.register_service("main_window", window)
app.context.register_service("plugin_manager", plugin_manager)

# Register and activate plugin
plugin_manager.register_plugin_class(HelloPlugin)
plugin_manager.load_plugin("hello_plugin")
plugin_manager.activate_plugin("hello_plugin")

window.show()
app.exec()
```

## Troubleshooting

### Plugin Not Loading

```python
# Check for errors
try:
    plugin_manager.load_plugin("my_plugin")
except Exception as e:
    print(f"Failed to load plugin: {e}")
    import traceback
    traceback.print_exc()
```

### Dependency Issues

```python
# Check dependencies
plugin = plugin_manager.get_plugin("my_plugin")
for dep in plugin.metadata.dependencies:
    if not plugin_manager.has_plugin(dep):
        print(f"Missing dependency: {dep}")
```

### Plugin Conflicts

```python
# List all active plugins
for name, plugin in plugin_manager.get_all_plugins().items():
    if plugin.is_active():
        print(f"{name} v{plugin.metadata.version}")
```
