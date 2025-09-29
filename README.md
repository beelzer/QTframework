# Qt Framework

A modern, feature-rich application framework built on PySide6 (Qt6) for creating professional desktop applications with Python.

## Features

### Core Components

- **Modern UI Components**: Comprehensive widget library with Material Design inspired components
- **Advanced Widgets**: Docking system, property panels, flow layouts, and custom controls
- **Theme System**: YAML-based theming with hot-reload, dark/light mode support
- **Internationalization (i18n)**: Complete multi-language support with Babel integration
- **Layout System**: Flexible layouts including FlowLayout for responsive designs
- **Data Binding**: Reactive data binding system with model management
- **Validation Framework**: Comprehensive input validation with custom validators
- **Event System**: Centralized event management with logging and debugging
- **Settings Management**: Persistent application and user settings

### Widget Library

#### Basic Widgets

- Labels, Buttons, Inputs
- Checkboxes, Radio buttons
- Sliders, Progress bars
- Spinners, Badges

#### Advanced Widgets

- **DockWidget**: Dockable panels with float/dock functionality
- **PropertiesPanel**: Dynamic property editor with type-specific controls
- **SearchableList**: List with integrated search functionality
- **DataTable**: Advanced table with sorting, filtering, and pagination
- **CodeEditor**: Syntax highlighting code editor
- **DateTimePicker**: Combined date and time selection
- **ColorPicker**: Professional color selection dialog
- **FileDialog**: Enhanced file selection with preview

### Internationalization

- **Babel Integration**: Full Unicode support with CLDR pluralization rules
- **Hot-reload**: Live translation updates without restart
- **Language Selector**: Built-in language switching widget
- **Format Localization**: Dates, numbers, currency formatting
- **Translatable Widgets**: Auto-updating UI components
- **Context Support**: Translation contexts for disambiguation

### Theme System

- **YAML Configuration**: Human-readable theme files
- **Live Reload**: Instant theme updates during development
- **Comprehensive Styling**: Colors, fonts, spacing, borders
- **Component Variants**: Primary, secondary, success, warning, error styles
- **Dark/Light Modes**: Built-in theme variants
- **Custom Properties**: Extensible theme system

## Installation

### Using pip

```bash
pip install qtframework
```

### Using uv (recommended)

```bash
uv pip install qtframework
```

### Development Installation

```bash
git clone https://github.com/yourusername/qtframework.git
cd qtframework
uv venv
uv pip install -e ".[dev]"
```

## Quick Start

### Basic Application

```python
import sys
from PySide6.QtWidgets import QApplication
from qtframework import QtWindow, ThemeManager

app = QApplication(sys.argv)

# Initialize theme
theme_manager = ThemeManager()
theme_manager.load_theme("modern_dark")

# Create main window
window = QtWindow(title="My App")
window.show()

sys.exit(app.exec())
```

### Using i18n

```python
from qtframework.i18n import get_i18n_manager, t

# Initialize i18n
manager = get_i18n_manager()
manager.set_locale("fr_FR")

# Use translations
print(t("Hello, World!"))  # Bonjour, le monde!
```

### Custom Widgets

```python
from qtframework.widgets import Badge, CountBadge, SearchableList

# Create a badge
badge = Badge("New", variant="success")

# Create a count badge
count_badge = CountBadge(count=42, variant="primary")

# Create searchable list
items = ["Python", "JavaScript", "Rust", "Go"]
search_list = SearchableList(items)
```

## Development

### Project Structure

```
qtframework/
├── src/
│   └── qtframework/
│       ├── core/          # Core functionality
│       ├── widgets/        # Widget library
│       ├── layouts/        # Layout managers
│       ├── themes/         # Theme system
│       ├── i18n/          # Internationalization
│       └── utils/         # Utilities
├── examples/
│   └── features/          # Feature demonstrations
├── tests/                 # Test suite
└── themes/               # Theme files
```

### Running Examples

```bash
cd examples/features
python main.py
```

### Testing

```bash
pytest
```

### Code Quality

```bash
# Format code
ruff format

# Lint code
ruff check

# Type checking
mypy src/qtframework
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

## i18n Management

### Adding Translations

```bash
# Extract translatable strings
python scripts/i18n_manager.py extract

# Initialize new locale
python scripts/i18n_manager.py init fr_FR

# Update existing translations
python scripts/i18n_manager.py update

# Compile translations (automatic with pre-commit)
python scripts/i18n_manager.py compile
```

### Translation Workflow

1. Mark strings for translation using `t()` or `_()`
2. Extract strings: `make i18n-extract`
3. Edit `.po` files with translations
4. Translations compile automatically on save (pre-commit hook)

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our repository.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `uv pip install -e ".[dev]"`
4. Install pre-commit hooks: `pre-commit install`
5. Make your changes
6. Run tests: `pytest`
7. Submit a pull request

## Build System

```bash
# Show all available commands
make help

# Common tasks
make install     # Install dependencies
make run         # Run the demo application
make test        # Run tests
make docs        # Build documentation
make check       # Run linting and type checking
```

**Windows users:** Install make via Chocolatey (`choco install make`) or Scoop (`scoop install make`).

## License

MIT License - see LICENSE file for details.

## Requirements

- Python 3.10+
- PySide6 (Qt6)
- PyYAML (themes)
- Babel (i18n)
- watchdog (hot-reload)

## Acknowledgments

Built with PySide6 and inspired by modern UI frameworks.
