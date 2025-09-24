# Qt Framework Modern Theming System

## Overview

The Qt Framework now features a modern, token-based theming system inspired by design systems like Material Design and modern web frameworks. This system provides:

- **Design Tokens**: Hierarchical color and style tokens (primitive → semantic → component)
- **Single-File Themes**: JSON or YAML theme definitions
- **Built-in Themes**: Light, Dark, and High Contrast themes
- **Dynamic Theme Switching**: Runtime theme changes without restart
- **Named Variables**: No hard-coded colors, everything uses semantic tokens

## Architecture

### Token Hierarchy

1. **Primitive Tokens**: Raw design values (colors, sizes, etc.)

   - Color scales (gray, primary, secondary, success, warning, error, info)
   - Base values for typography, spacing, borders, shadows

2. **Semantic Tokens**: Meaning-based references to primitive tokens

   - Background colors (primary, secondary, tertiary, elevated)
   - Foreground/text colors (primary, secondary, tertiary)
   - Interactive states (hover, selected, disabled, focus)
   - Feedback colors (success, warning, error, info)

3. **Component Tokens**: Widget-specific tokens
   - Button colors and states
   - Input field styling
   - Table colors (header, rows, borders)
   - Menu styling
   - Scrollbar appearance

## Creating Themes

### JSON Theme Format

```json
{
  "name": "my_theme",
  "display_name": "My Custom Theme",
  "description": "A custom theme for my application",
  "author": "Your Name",
  "version": "1.0.0",
  "tokens": {
    "primitive": {
      "primary_500": "#2196F3",
      "gray_100": "#F5F5F5"
    },
    "semantic": {
      "bg_primary": "#FFFFFF",
      "fg_primary": "#212121",
      "action_primary": "#2196F3"
    },
    "components": {
      "button_primary_bg": "#2196F3",
      "button_primary_fg": "#FFFFFF"
    },
    "typography": {
      "font_family_default": "'Segoe UI', sans-serif",
      "font_size_md": 14
    }
  },
  "custom_styles": {
    "MyCustomWidget": "background: red;"
  }
}
```

### YAML Theme Format

```yaml
name: my_theme
display_name: My Custom Theme
description: A custom theme for my application
author: Your Name
version: 1.0.0

tokens:
  primitive:
    primary_500: "#2196F3"
    gray_100: "#F5F5F5"

  semantic:
    bg_primary: "#FFFFFF"
    fg_primary: "#212121"
    action_primary: "#2196F3"

  components:
    button_primary_bg: "#2196F3"
    button_primary_fg: "#FFFFFF"

  typography:
    font_family_default: "'Segoe UI', sans-serif"
    font_size_md: 14

custom_styles: {}
```

## Using the Theme System

### Basic Usage

```python
from qtframework.themes import ThemeManager

# Initialize theme manager
theme_manager = ThemeManager()

# List available themes
themes = theme_manager.list_themes()
print(f"Available themes: {themes}")

# Set a theme
theme_manager.set_theme("dark")

# Get stylesheet for application
stylesheet = theme_manager.get_stylesheet()
app.setStyleSheet(stylesheet)

# Listen for theme changes
theme_manager.theme_changed.connect(on_theme_changed)
```

### Programmatic Theme Creation

```python
from qtframework.themes import Theme, DesignTokens, SemanticColors

# Create custom tokens
tokens = DesignTokens()
tokens.semantic = SemanticColors(
    bg_primary="#1E1E1E",
    fg_primary="#E0E0E0",
    action_primary="#42A5F5"
)

# Create theme
custom_theme = Theme(
    name="custom",
    display_name="Custom Theme",
    tokens=tokens
)

# Register with manager
theme_manager.register_theme(custom_theme)
```

### Widget Styling

The theme system supports various widget properties for enhanced styling:

#### Button Variants

```python
button = QPushButton("Click me")
button.setProperty("variant", "primary")  # primary, secondary, success, warning, danger, info, ghost, outline
```

#### Typography

```python
label = QLabel("Heading")
label.setProperty("heading", "h1")  # h1, h2, h3

label = QLabel("Secondary text")
label.setProperty("secondary", "true")
```

#### Cards/Frames

```python
frame = QFrame()
frame.setProperty("card", "true")  # Applies card styling
```

## File Structure

```
resources/themes/
├── monokai.yaml        # Monokai theme
├── solarized_dark.yaml # Solarized Dark theme
└── custom_theme.yaml   # Your custom themes

src/qtframework/themes/
├── __init__.py              # Public API
├── tokens.py                # Token definitions
├── theme.py                 # Theme class
├── theme_manager.py         # Theme manager
├── stylesheet_generator.py  # Stylesheet generation
└── builtin_themes.py        # Built-in theme definitions
```

## Token Reference

### Color Scales

Each color has 11 shades (50-950):

- `gray_*`: Neutral colors
- `primary_*`: Main brand color
- `secondary_*`: Accent color
- `success_*`: Positive feedback
- `warning_*`: Caution feedback
- `error_*`: Negative feedback
- `info_*`: Informational

### Semantic Colors

- `bg_primary`: Main background
- `bg_secondary`: Surface/card background
- `bg_tertiary`: Subtle backgrounds
- `fg_primary`: Main text color
- `fg_secondary`: Subtle text
- `action_primary`: Primary actions
- `state_hover`: Hover state
- `state_selected`: Selected state
- `border_default`: Standard borders
- `border_focus`: Focused element borders

### Typography Tokens

- `font_family_default`: Main font stack
- `font_size_*`: xs, sm, md, lg, xl, 2xl, 3xl, 4xl, 5xl
- `font_weight_*`: thin, light, normal, medium, semibold, bold, black
- `line_height_*`: tight, normal, relaxed, loose

### Spacing Tokens

- `space_*`: 0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32

### Border Radius Tokens

- `radius_*`: none, sm, md, lg, xl, 2xl, 3xl, full

## Best Practices

1. **Use Semantic Tokens**: Always reference semantic tokens rather than primitive colors
2. **Single Source of Truth**: Define colors once in primitive tokens
3. **Consistent Naming**: Follow the established naming conventions
4. **Theme Testing**: Test themes with all widget types
5. **Accessibility**: Ensure sufficient contrast ratios
6. **Version Control**: Version your theme files

## Migration from Old System

If you were using the old theming system:

1. Convert `ColorPalette` to new token structure
2. Replace `StandardTheme` with new `Theme` class
3. Update theme file format to JSON/YAML
4. Use `ThemeManager` instead of old manager
5. Update widget property names if needed

## Examples

See `examples/theme_demo.py` for a complete demonstration of the theming system with all widget types and theme switching.
