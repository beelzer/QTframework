# Qt Framework Documentation

Welcome to the Qt Framework documentation! This framework provides modern, modular Qt application development tools.

```{toctree}
:caption: Getting Started
:maxdepth: 2

quickstart
installation
tutorials/index
```

```{toctree}
:caption: User Guide
:maxdepth: 2

guides/index
examples/index
```

```{toctree}
:caption: API Reference
:maxdepth: 3

api/index
```

```{toctree}
:caption: Development
:maxdepth: 2

contributing
changelog
```

## Welcome to Qt Framework

Qt Framework is a modern, modular application framework for building sophisticated desktop applications with Python and PySide6.

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} 🚀 Quick Start
:link: quickstart
:link-type: doc

Get started with Qt Framework in minutes
:::

:::{grid-item-card} 📖 User Guide
:link: guides/index
:link-type: doc

Learn the core concepts and features
:::

:::{grid-item-card} 🔧 API Reference
:link: api/index
:link-type: doc

Complete API documentation with examples
:::

:::{grid-item-card} 💡 Examples
:link: examples/index
:link-type: doc

Browse example applications and code snippets
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
