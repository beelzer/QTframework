# Qt Framework

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![Coverage](https://img.shields.io/badge/coverage-85%25-yellowgreen.svg)](https://beelzer.github.io/QTframework/coverage/)
[![PySide6](https://img.shields.io/badge/Qt-PySide6-41CD52.svg)](https://wiki.qt.io/Qt_for_Python)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://beelzer.github.io/QTframework/)

A modern, feature-rich application framework built on PySide6 (Qt6) for creating professional desktop applications with Python.

## ✨ Features

- 🎨 **Modern UI Components** - Comprehensive widget library with Material Design inspiration
- 🌗 **Advanced Theming** - YAML-based themes with hot-reload and dark/light mode support
- 🌍 **Internationalization** - Complete i18n with Babel integration and live updates
- 📊 **State Management** - Redux-like store with time-travel debugging
- 🎯 **Type Safe** - Full type hints and mypy validation
- 🔌 **Plugin System** - Extensible architecture with hot-loading capabilities
- ✅ **Validation Framework** - Built-in validators with i18n error messages
- 📐 **Flexible Layouts** - Flow layouts, sidebars, cards, and custom arrangements

## 🚀 Quick Start

### Installation

```bash
# Using pip
pip install qt-framework

# Using uv (recommended)
uv pip install qt-framework
```

### Basic Application

```python
from qtframework import Application, BaseWindow

class MainWindow(BaseWindow):
    def __init__(self, application=None):
        super().__init__(application, title="My App")
        # Your UI setup here

# Create and run
Application.create_and_run(
    MainWindow,
    app_name="MyApp",
    org_name="MyCompany"
)
```

### Using Themes

```python
from qtframework import Application

app = Application()
app.theme_manager.set_theme("dark")  # or "light", "high_contrast"
```

### State Management

```python
from qtframework.state import Store, Action

def reducer(state, action):
    if action.type == "INCREMENT":
        return {**state, "count": state["count"] + 1}
    return state

store = Store(reducer=reducer, initial_state={"count": 0})
store.dispatch(Action(type="INCREMENT"))
print(store.state)  # {"count": 1}
```

## 📚 Documentation

**[Read the full documentation →](https://beelzer.github.io/QTframework/)**

- [User Guide](https://beelzer.github.io/QTframework/user-guide/)
- [API Reference](https://beelzer.github.io/QTframework/api/)
- [Examples](https://beelzer.github.io/QTframework/examples/)
- [Contributing Guide](https://beelzer.github.io/QTframework/contributing/)

## 🏗️ Development

```bash
# Clone repository
git clone https://github.com/beelzer/QTframework.git
cd QTframework

# Install with development dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run example application
python examples/features/main.py
```

### Code Quality

```bash
ruff format      # Format code
ruff check       # Lint code
mypy src         # Type check
pytest           # Run tests
```

## 🎯 Core Components

| Component            | Description                                         |
| -------------------- | --------------------------------------------------- |
| **Application**      | Enhanced QApplication with theme/context management |
| **BaseWindow**       | Framework-integrated QMainWindow base class         |
| **Store**            | Redux-like state management with middleware         |
| **ThemeManager**     | YAML-based theming with hot-reload                  |
| **BabelI18nManager** | Complete internationalization with CLDR support     |
| **PluginManager**    | Dynamic plugin loading and lifecycle management     |
| **Validation**       | Input validation with custom validators             |

## 🧩 Widget Library

- **Basic**: Labels, Buttons, Inputs, Checkboxes, Badges
- **Advanced**: DataTable, SearchableList, Charts, Notifications
- **Dialogs**: ColorPicker, DateTimePicker, FileDialog
- **Layouts**: FlowLayout, CardLayout, SidebarLayout

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with [PySide6](https://wiki.qt.io/Qt_for_Python) and inspired by modern web frameworks like React and Redux.

---

**[Documentation](https://beelzer.github.io/QTframework/)** • **[Examples](examples/)** • **[Issues](https://github.com/beelzer/QTframework/issues)**
