"""Modern theming system for Qt Framework.

This module provides a comprehensive theming system based on design tokens,
supporting built-in themes, custom themes, and runtime theme switching.

Theming Architecture:
    The theming system uses a layered token approach::

        Design Tokens (abstract values)
              ↓
        Semantic Tokens (role-based)
              ↓
        Component Tokens (widget-specific)
              ↓
        Generated Stylesheet (Qt CSS)

    Token Hierarchy:
    - **Primitive Tokens**: Base colors, font sizes
    - **Semantic Tokens**: bg_primary, action_primary (role-based)
    - **Component Tokens**: button_bg, input_border (widget-specific)

Quick Start:
    Using built-in themes::

        from qtframework.themes import ThemeManager
        from PySide6.QtWidgets import QApplication

        app = QApplication([])
        theme_manager = ThemeManager()

        # Apply light theme
        theme_manager.set_theme("light")
        app.setStyleSheet(theme_manager.get_stylesheet())

        # Switch to dark theme
        theme_manager.set_theme("dark")
        app.setStyleSheet(theme_manager.get_stylesheet())

        # Listen for theme changes
        theme_manager.theme_changed.connect(
            lambda name: app.setStyleSheet(theme_manager.get_stylesheet())
        )

    Creating custom themes::

        from qtframework.themes import Theme, DesignTokens, SemanticColors

        # Load from YAML file
        custom_theme = Theme.from_yaml("my_theme.yaml")
        theme_manager.register_theme(custom_theme)

        # Or create programmatically
        tokens = DesignTokens()
        tokens.semantic = SemanticColors(
            bg_primary="#FFFFFF", fg_primary="#000000", action_primary="#007AFF"
        )

        theme = Theme(name="custom", display_name="Custom Theme", tokens=tokens)
        theme_manager.register_theme(theme)
        theme_manager.set_theme("custom")

Configuration Patterns:
    YAML theme structure::

        # my_theme.yaml
        name: "ocean"
        display_name: "Ocean Theme"
        description: "A calming ocean theme"
        author: "Your Name"
        version: "1.0.0"

        tokens:
          semantic:
            bg_primary: "#F0F8FF"
            fg_primary: "#1A1A1A"
            action_primary: "#0077BE"
            action_secondary: "#00A8E8"

          spacing:
            xs: 4
            sm: 8
            md: 16
            lg: 24

          typography:
            font_family: "Segoe UI"
            font_size_base: 14
            font_weight_regular: 400
            font_weight_bold: 600

          border_radius:
            sm: 4
            md: 8
            lg: 16

See Also:
    :class:`ThemeManager`: Main theme management class
    :class:`Theme`: Individual theme definition
    :class:`DesignTokens`: Token container
    :mod:`qtframework.widgets`: Widgets that use themes
"""

from __future__ import annotations

from qtframework.themes.builtin_themes import (
    BUILTIN_THEMES,
    create_dark_theme,
    create_high_contrast_theme,
    create_light_theme,
)
from qtframework.themes.theme import Theme
from qtframework.themes.theme_manager import ThemeManager
from qtframework.themes.tokens import (
    BorderRadius,
    ComponentColors,
    DesignTokens,
    PrimitiveColors,
    SemanticColors,
    Shadows,
    Spacing,
    Transitions,
    Typography,
)


__all__ = [
    "BUILTIN_THEMES",
    "BorderRadius",
    "ComponentColors",
    # Token classes
    "DesignTokens",
    "PrimitiveColors",
    "SemanticColors",
    "Shadows",
    "Spacing",
    # Core classes
    "Theme",
    "ThemeManager",
    "Transitions",
    "Typography",
    "create_dark_theme",
    "create_high_contrast_theme",
    # Built-in themes
    "create_light_theme",
]
