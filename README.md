# Qt Framework

A comprehensive, enterprise-grade Qt application framework for Python with advanced features for building professional desktop applications.

## 🚀 Core Features

### Foundation

- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Advanced Theming**: Built-in theme manager with runtime switching
- **Type Safety**: Full type hints and mypy strict mode support
- **Modern Python**: Built for Python 3.13+ with latest best practices

### Advanced Capabilities

- **🔌 Plugin System**: Extensible plugin architecture for modular features
- **📊 State Management**: Redux-like state management with middleware support
- **🔔 Notifications**: Toast-style notification system with animations
- **🧭 Navigation/Routing**: SPA-style routing with guards and history
- **⚙️ Configuration**: Multi-source config management (JSON, YAML, ENV)
- **🎨 Advanced Widgets**: Charts, tables, dialogs, and more
- **🌍 i18n Support**: Built-in internationalization
- **💾 Database ORM**: SQLAlchemy integration
- **🧪 Testing Utilities**: Fixtures and helpers for unit testing
- **📦 Data Binding**: Reactive components with two-way binding

## Installation

```bash
# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"
```

## Quick Start

### Run the Demo

See all framework features in action:

```bash
# Using uv (recommended)
uv run python examples/demo_app/main.py

# Or with standard Python
python examples/demo_app/main.py
```

### Simple Example

```python
from qtframework import Application, BaseWindow
from qtframework.widgets import Button
from qtframework.layouts import FlexLayout

class MyWindow(BaseWindow):
    def __init__(self, application=None):
        super().__init__(application, title="My App")
        self._setup_ui()

    def _setup_ui(self):
        super()._setup_ui()

        # Add your UI components here
        button = Button("Click Me")
        layout = FlexLayout()
        layout.add_widget(button)

if __name__ == "__main__":
    Application.create_and_run(MyWindow, app_name="MyApp")
```

## Project Structure

```
qtframework/
├── src/qtframework/
│   ├── core/              # Core application components
│   ├── widgets/           # Reusable widget library
│   │   └── advanced/      # Advanced widgets (charts, tables, etc.)
│   ├── layouts/           # Layout managers and patterns
│   ├── themes/            # Theming system
│   ├── plugins/           # Plugin system
│   ├── state/             # State management (Redux-like)
│   ├── navigation/        # Routing and navigation
│   ├── config/            # Configuration management
│   ├── services/          # Application services
│   ├── models/            # Data models
│   ├── controllers/       # Controllers
│   └── utils/             # Utility functions
├── examples/              # Example applications
│   └── demo_app/          # Complete framework demo
├── tests/                 # Test suite
├── docs/                  # Documentation
└── resources/             # Assets and themes
```

## Development

```bash
# Run demo application
uv run python examples/demo_app/main.py

# Run linting
ruff check src/

# Run type checking
mypy src/

# Run tests
pytest
```

## Components

### Core Components

- `Application`: Enhanced QApplication with context and theme management
- `BaseWindow`: Base window class with framework integration
- `Context`: Application-wide state management

### State Management

```python
from qtframework.state import Store, Action, combine_reducers

# Create store with reducers
store = Store(root_reducer, middleware=[logger_middleware()])

# Dispatch actions
store.dispatch(Action(type="INCREMENT"))

# Subscribe to changes
store.subscribe(lambda state: print(state))
```

### Plugin System

```python
from qtframework.plugins import Plugin, PluginManager

class MyPlugin(Plugin):
    def initialize(self): return True
    def activate(self): return True
    def deactivate(self): return True

manager = PluginManager()
manager.load_plugin("my_plugin")
```

### Navigation/Routing

```python
from qtframework.navigation import Router, Route

router = Router([
    Route("/home", HomeComponent, name="home"),
    Route("/settings/:id", SettingsComponent),
])

router.navigate("/home")
router.navigate_by_name("home")
```

### Notification System

```python
from qtframework.widgets.advanced.notifications import NotificationManager

notifications = NotificationManager(parent_widget)
notifications.success("Success", "Operation completed!")
notifications.error("Error", "Something went wrong")
```

### Configuration Management

```python
from qtframework.config import Config, ConfigManager

config = Config({"app": {"name": "MyApp"}})
config.get("app.name")  # "MyApp"
config.set("app.version", "1.0.0")
config.watch("app.theme", lambda v: print(f"Theme changed: {v}"))
```

### Widgets

- **Basic**: Button, Input, PasswordInput, SearchInput, TextArea, Card
- **Advanced**: DataTable, TreeTable, Charts, Dialogs, Notifications
- **Layouts**: FlexLayout, GridLayout, SidebarLayout, CardLayout

### Themes

- Built-in light and dark themes
- Theme manager for runtime switching
- JSON-based custom theme support
- Complete widget styling

## License

MIT License - see LICENSE file for details
