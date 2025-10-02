# Theming Guide

Qt Framework includes a powerful, flexible theming system based on design tokens. This guide covers how to use built-in themes, customize them, and create your own.

## Overview

The theming system uses a token-based architecture with three layers:

1. **Primitive Tokens** - Raw color values (e.g., `primary_500: #2196F3`)
2. **Semantic Tokens** - Meaning-based references (e.g., `bg_primary`, `fg_primary`)
3. **Component Tokens** - Component-specific styles (e.g., `button_primary_bg`)

This architecture ensures consistency and makes it easy to create cohesive themes.

## Using Built-in Themes

Qt Framework comes with three built-in themes:

### Light Theme

```python
from qtframework.core import Application
from qtframework.themes import ThemeManager

app = Application()
theme_manager = ThemeManager()

# Load and apply light theme
theme_manager.load_theme("light")
theme_manager.apply_theme(app)
```

### Dark Theme

```python
from qtframework.core import Application
from qtframework.themes import ThemeManager

app = Application()
theme_manager = ThemeManager()

# Load and apply dark theme
theme_manager.load_theme("dark")
theme_manager.apply_theme(app)
```

### High Contrast Theme

For accessibility, use the high contrast theme:

```python
theme_manager.load_theme("high_contrast")
theme_manager.apply_theme(app)
```

## Accessing Theme Colors

### From Theme Tokens

```python
from qtframework.themes.builtin_themes import create_light_theme

theme = create_light_theme()

# Access primitive colors
primary_color = theme.tokens.primitive.primary_500  # "#2196F3"

# Access semantic colors
bg_color = theme.tokens.semantic.bg_primary  # "#FFFFFF"
text_color = theme.tokens.semantic.fg_primary  # "#212121"

# Access component colors
button_bg = theme.tokens.components.button_primary_bg
```

## Creating Custom Themes

### Method 1: Modify Existing Theme

```python
from qtframework.themes.builtin_themes import create_light_theme

# Start with light theme
theme = create_light_theme()

# Customize colors
theme.tokens.primitive.primary_500 = "#FF5722"  # Change primary color
theme.tokens.semantic.action_primary = "#FF5722"

# Apply the customized theme
theme_manager.apply_theme_object(theme)
```

### Method 2: Create from Scratch

```python
from qtframework.themes import Theme
from qtframework.themes.tokens import (
    DesignTokens,
    PrimitiveColors,
    SemanticColors,
    ComponentColors,
)

# Create custom tokens
tokens = DesignTokens()

# Set primitive colors
tokens.primitive = PrimitiveColors(
    primary_500="#9C27B0",  # Purple
    primary_600="#7B1FA2",
    # ... other colors
)

# Set semantic colors
tokens.semantic = SemanticColors(
    bg_primary="#FFFFFF",
    fg_primary="#212121",
    action_primary=tokens.primitive.primary_500,
    # ... other semantic tokens
)

# Set component colors
tokens.components = ComponentColors(
    button_primary_bg=tokens.primitive.primary_500,
    button_primary_fg="#FFFFFF",
    # ... other component tokens
)

# Create theme
custom_theme = Theme(
    name="purple",
    display_name="Purple Theme",
    description="A custom purple theme",
    author="Your Name",
    version="1.0.0",
    tokens=tokens,
)

# Apply it
theme_manager.apply_theme_object(custom_theme)
```

### Method 3: Load from YAML

Create a theme file `my_theme.yaml`:

```yaml
name: ocean
display_name: Ocean Theme
description: A calming ocean-inspired theme
author: Your Name
version: 1.0.0

tokens:
  primitive:
    primary_500: "#006064"
    primary_600: "#00838F"
    # ... other colors

  semantic:
    bg_primary: "#FFFFFF"
    fg_primary: "#212121"
    action_primary: "{primitive.primary_500}"

  components:
    button_primary_bg: "{semantic.action_primary}"
    button_primary_fg: "#FFFFFF"
```

Load and apply:

```python
from qtframework.themes import Theme

theme = Theme.from_yaml("my_theme.yaml")
theme_manager.apply_theme_object(theme)
```

## Hot Reload During Development

Enable theme hot-reload for rapid development:

```python
# Enable hot reload (watches theme files for changes)
theme_manager.enable_hot_reload("path/to/themes")

# Disable when done
theme_manager.disable_hot_reload()
```

## Theme Switching at Runtime

Allow users to switch themes:

```python
from PySide6.QtWidgets import QComboBox

def create_theme_switcher():
    combo = QComboBox()
    combo.addItems(["light", "dark", "high_contrast"])

    def on_theme_changed(theme_name):
        theme_manager.load_theme(theme_name)
        theme_manager.apply_theme(app)

    combo.currentTextChanged.connect(on_theme_changed)
    return combo
```

## Design Token Reference

### Color Scales

Each color has a scale from 50 (lightest) to 950 (darkest):

- **Gray Scale**: `gray_50` through `gray_950`
- **Primary**: `primary_50` through `primary_950`
- **Secondary**: `secondary_50` through `secondary_950`
- **Success**: `success_50` through `success_950`
- **Warning**: `warning_50` through `warning_950`
- **Error**: `error_50` through `error_950`
- **Info**: `info_50` through `info_950`

### Semantic Tokens

#### Backgrounds

- `bg_primary` - Main background
- `bg_secondary` - Secondary surfaces
- `bg_tertiary` - Tertiary surfaces
- `bg_elevated` - Cards, dialogs
- `bg_overlay` - Modal overlays

#### Foreground/Text

- `fg_primary` - Primary text
- `fg_secondary` - Secondary text
- `fg_tertiary` - Disabled text
- `fg_on_accent` - Text on accent colors
- `fg_on_dark` - Text on dark backgrounds
- `fg_on_light` - Text on light backgrounds

#### Actions

- `action_primary` - Primary action color
- `action_primary_hover` - Primary hover state
- `action_primary_active` - Primary active state
- `action_secondary` - Secondary action color
- `action_secondary_hover` - Secondary hover state
- `action_secondary_active` - Secondary active state

#### Feedback

- `feedback_success` - Success messages
- `feedback_warning` - Warning messages
- `feedback_error` - Error messages
- `feedback_info` - Info messages

#### Borders

- `border_default` - Default borders
- `border_subtle` - Subtle borders
- `border_strong` - Strong borders
- `border_focus` - Focus indicators

### Typography Tokens

```python
# Font families
theme.tokens.typography.font_family_default
theme.tokens.typography.font_family_mono
theme.tokens.typography.font_family_code

# Font sizes
theme.tokens.typography.font_size_xs   # 11pt
theme.tokens.typography.font_size_sm   # 12pt
theme.tokens.typography.font_size_md   # 14pt
theme.tokens.typography.font_size_lg   # 16pt
theme.tokens.typography.font_size_xl   # 18pt

# Font weights
theme.tokens.typography.font_weight_normal
theme.tokens.typography.font_weight_medium
theme.tokens.typography.font_weight_bold
```

### Spacing Tokens

```python
theme.tokens.spacing.space_2   # 4px
theme.tokens.spacing.space_4   # 8px
theme.tokens.spacing.space_6   # 12px
theme.tokens.spacing.space_8   # 16px
theme.tokens.spacing.space_12  # 24px
```

## Font Scaling

The theme system supports dynamic font scaling to improve accessibility. You can scale all typography tokens proportionally using a percentage value:

```python
# Initialize theme manager with font scaling
theme_manager = ThemeManager(font_scale=125)  # 125% larger fonts

# Or update font scale dynamically
theme_manager.set_font_scale(150)  # 150% larger fonts

# Regenerate stylesheet with new scale
app.setStyleSheet(theme_manager.get_stylesheet())
```

**Font Scale Range**: 50% to 200%

- `100` = Normal size (default)
- `125` = 25% larger (recommended for accessibility)
- `150` = 50% larger
- `75` = 25% smaller

Font scaling maintains the visual hierarchy by scaling all typography tokens (xs, sm, md, lg, xl, etc.) proportionally.

### Configuration Integration

You can integrate font scaling with your configuration system:

```yaml
# config.yaml
ui:
  font_scale: 125 # 125% font size
```

```python
# Load and apply font scale from config
config_manager = ConfigManager()
font_scale = config_manager.get("ui.font_scale", 100)
theme_manager = ThemeManager(font_scale=font_scale)
```

## Best Practices

1. **Use Semantic Tokens** - Prefer semantic tokens over primitive colors in your widgets
2. **Consistent Scales** - Stick to the predefined color scale increments
3. **Test Both Themes** - Always test your app in both light and dark themes
4. **Accessibility** - Ensure sufficient contrast ratios (WCAG AA: 4.5:1 for text)
5. **Document Custom Tokens** - If adding custom component tokens, document their purpose
6. **Support Font Scaling** - Allow users to adjust font scale for accessibility (50-200%)

## Advanced: Custom Stylesheet Generation

The theme system generates Qt stylesheets automatically. For custom styling:

```python
theme = create_light_theme()

# Add custom stylesheet rules
theme.custom_styles = {
    "MyCustomWidget": """
        background-color: {semantic.bg_primary};
        color: {semantic.fg_primary};
        border: 1px solid {semantic.border_default};
        border-radius: {borders.radius_md}px;
    """
}

# Tokens in {curly braces} are automatically resolved
stylesheet = theme.generate_stylesheet()
app.setStyleSheet(stylesheet)
```

## Troubleshooting

### Theme not applying

Make sure you're applying the theme after creating the application:

```python
app = Application()
theme_manager.apply_theme(app)  # Must be after app creation
```

### Colors look wrong

Check that semantic tokens are properly resolved:

```python
theme.tokens.resolve_semantic_colors()
```

### Custom theme not loading

Verify your YAML syntax and ensure all required fields are present:

```python
try:
    theme = Theme.from_yaml("my_theme.yaml")
except Exception as e:
    print(f"Theme loading error: {e}")
```
