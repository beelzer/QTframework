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
