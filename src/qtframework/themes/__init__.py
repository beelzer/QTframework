"""Modern theming system for Qt Framework."""

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
    # Core classes
    "Theme",
    "ThemeManager",
    # Token classes
    "DesignTokens",
    "PrimitiveColors",
    "SemanticColors",
    "ComponentColors",
    "Typography",
    "Spacing",
    "BorderRadius",
    "Shadows",
    "Transitions",
    # Built-in themes
    "create_light_theme",
    "create_dark_theme",
    "create_high_contrast_theme",
    "BUILTIN_THEMES",
]
