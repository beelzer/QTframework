# ConfigEditorWidget

A generic, reusable widget for editing configuration values with automatic UI generation based on field descriptors.

## Features

- **Automatic UI Generation**: Define fields declaratively, widget generates appropriate inputs
- **Multiple Field Types**: String, int, float, bool, and choice (dropdown) fields
- **Grouping**: Organize fields into collapsible groups
- **Dynamic Choices**: Support for static or dynamic (callback-based) dropdown options
- **Change Callbacks**: Execute custom logic when specific fields change
- **JSON View**: Optional live JSON view of current configuration
- **File Operations**: Built-in load/save with file dialogs supporting JSON, YAML, INI, and ENV formats
- **Signals**: Emits signals when config is changed, loaded, or saved

## Basic Usage

```python
from qtframework.config import ConfigManager
from qtframework.widgets import ConfigEditorWidget, ConfigFieldDescriptor

# Create config manager
config = ConfigManager()

# Define fields
fields = [
    ConfigFieldDescriptor(
        key="app.name",
        label="Application Name",
        field_type="string",
        default="My App",
        group="Application"
    ),
    ConfigFieldDescriptor(
        key="ui.theme",
        label="Theme",
        field_type="choice",
        choices=["light", "dark", "monokai"],
        default="light",
        group="User Interface"
    ),
    ConfigFieldDescriptor(
        key="ui.font_size",
        label="Font Size",
        field_type="int",
        default=12,
        min_value=8,
        max_value=72,
        group="User Interface"
    ),
]

# Create editor widget
editor = ConfigEditorWidget(
    config_manager=config,
    fields=fields,
    show_json_view=True,
    show_file_buttons=True
)

# Connect to signals
editor.config_changed.connect(lambda: print("Config changed!"))
```

## Field Types

### String Field

```python
ConfigFieldDescriptor(
    key="app.name",
    label="Application Name",
    field_type="string",
    default="My App"
)
```

### Integer Field

```python
ConfigFieldDescriptor(
    key="performance.threads",
    label="Worker Threads",
    field_type="int",
    default=4,
    min_value=1,
    max_value=64
)
```

### Float Field

```python
ConfigFieldDescriptor(
    key="graphics.scale",
    label="UI Scale",
    field_type="float",
    default=1.0,
    min_value=0.5,
    max_value=2.0
)
```

### Boolean Field

```python
ConfigFieldDescriptor(
    key="app.debug",
    label="Debug Mode",
    field_type="bool",
    default=False
)
```

### Choice Field (Static)

```python
ConfigFieldDescriptor(
    key="ui.language",
    label="Language",
    field_type="choice",
    choices=["en_US", "es_ES", "fr_FR"],
    default="en_US"
)
```

### Choice Field (Dynamic)

```python
def get_themes():
    return theme_manager.list_themes()

ConfigFieldDescriptor(
    key="ui.theme",
    label="Theme",
    field_type="choice",
    choices_callback=get_themes,  # Dynamic choices
    default="light"
)
```

## Change Callbacks

Execute custom logic when a field changes:

```python
def on_theme_changed(new_theme: str):
    theme_manager.set_theme(new_theme)
    print(f"Theme changed to: {new_theme}")

ConfigFieldDescriptor(
    key="ui.theme",
    label="Theme",
    field_type="choice",
    choices=["light", "dark"],
    on_change=on_theme_changed  # Called when applied
)
```

## Grouping Fields

Organize related fields into groups:

```python
fields = [
    # Application group
    ConfigFieldDescriptor(
        key="app.name",
        label="Name",
        field_type="string",
        group="Application Settings"
    ),
    ConfigFieldDescriptor(
        key="app.version",
        label="Version",
        field_type="string",
        group="Application Settings"
    ),

    # UI group
    ConfigFieldDescriptor(
        key="ui.theme",
        label="Theme",
        field_type="choice",
        choices=["light", "dark"],
        group="User Interface"
    ),
]
```

## Signals

```python
# Config changed (after apply_changes)
editor.config_changed.connect(on_config_changed)

# Config loaded from file
editor.config_loaded.connect(lambda path: print(f"Loaded: {path}"))

# Config saved to file
editor.config_saved.connect(lambda path: print(f"Saved: {path}"))
```

## Methods

### refresh_values()

Reload field values from current config state:

```python
editor.refresh_values()
```

### apply_changes()

Apply widget values to config manager:

```python
editor.apply_changes()
```

### get_value(key)

Get current widget value (not yet applied):

```python
current_theme = editor.get_value("ui.theme")
```

### set_value(key, value)

Set widget value directly:

```python
editor.set_value("ui.theme", "dark")
```

## Complete Example

See `examples/features/app/pages/config_editor.py` for a complete working example that demonstrates:

- Multiple field types
- Dynamic choices from theme manager
- Change callbacks for theme switching
- Integration with application config manager
- Grouped fields by category

## Constructor Options

```python
ConfigEditorWidget(
    config_manager: ConfigManager,  # Required: config manager instance
    fields: list[ConfigFieldDescriptor],  # Required: field definitions
    show_json_view: bool = True,  # Show JSON view section
    show_file_buttons: bool = True,  # Show load/save buttons
    parent: QWidget | None = None
)
```

## Best Practices

1. **Define all fields upfront** - Dynamic field addition requires UI rebuild
2. **Use groups** - Organize related settings together
3. **Set appropriate min/max** - Constrain numeric fields to valid ranges
4. **Use callbacks** - Apply changes immediately when they affect app state
5. **Connect signals** - React to config changes in other parts of your app

## Comparison to Manual Implementation

**Before (280 lines):**

```python
# Manually create each widget
self.app_name_edit = QLineEdit()
self.theme_combo = QComboBox()
# ... many more widgets
# Manually create layouts
# Manually wire up signals
# Manually implement refresh/apply logic
```

**After (~50 lines):**

```python
fields = [
    ConfigFieldDescriptor(key="app.name", label="Name", field_type="string"),
    ConfigFieldDescriptor(key="ui.theme", label="Theme", field_type="choice",
                         choices_callback=get_themes),
]
editor = ConfigEditorWidget(config_manager, fields)
```

The generic widget reduces boilerplate by 80%+ while providing a consistent, themeable UI.
