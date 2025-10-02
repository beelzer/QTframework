# Qt Framework Documentation

Welcome to the Qt Framework documentation! This framework provides modern, modular Qt application development tools.

```{toctree}
:caption: Getting Started
:maxdepth: 2

quickstart
```

```{toctree}
:caption: User Guides
:maxdepth: 2

guides/theming
guides/state_management
guides/navigation
guides/internationalization
guides/plugins
```

```{toctree}
:caption: Widgets
:maxdepth: 2

widgets/config_editor
```

```{toctree}
:caption: API Reference
:maxdepth: 3

api/index
```

## Welcome to Qt Framework

Qt Framework is a modern, modular application framework for building sophisticated desktop applications with Python and PySide6.

::::{grid} 1 1 2 3
:gutter: 3

:::{grid-item-card} 🚀 Quick Start
:link: quickstart
:link-type: doc

Get started with Qt Framework in minutes
:::

:::{grid-item-card} 🎨 Theming Guide
:link: guides/theming
:link-type: doc

Learn about the token-based theming system
:::

:::{grid-item-card} 🔄 State Management
:link: guides/state_management
:link-type: doc

Redux-inspired state management patterns
:::

:::{grid-item-card} 🧭 Navigation
:link: guides/navigation
:link-type: doc

Routing and page navigation system
:::

:::{grid-item-card} 🌍 Internationalization
:link: guides/internationalization
:link-type: doc

Multi-language support with Babel
:::

:::{grid-item-card} 🔌 Plugins
:link: guides/plugins
:link-type: doc

Build extensible applications with plugins
:::

:::{grid-item-card} 🧩 Widgets
:link: widgets/config_editor
:link-type: doc

Reusable widget components
:::

:::{grid-item-card} 🔧 API Reference
:link: api/index
:link-type: doc

Complete API documentation
:::
::::

## Key Features

- **Modern Architecture** - Built on PySide6 with modern Python patterns
- **Modular Design** - Extensible plugin system for custom components
- **Type Safety** - Full type hints and runtime validation with Pydantic
- **Theming** - Beautiful, customizable themes with hot-reload support
- **i18n Support** - Built-in internationalization with Babel
- **Database Ready** - SQLAlchemy integration with migration support
- **Developer Friendly** - Live reload, comprehensive logging, and debugging tools

## Installation

```bash
pip install qt-framework
```

Or with development dependencies:

```bash
pip install "qt-framework[dev]"
```

## Quick Example

```python
from qtframework import Application, MainWindow

app = Application()
window = MainWindow(title="My App")
window.show()
app.exec()
```

## Requirements

- Python 3.13+
- PySide6 6.8+
- Windows, macOS, or Linux

## License

MIT License - see [LICENSE](https://github.com/beelzer/qt-framework/blob/main/LICENSE) for details.
