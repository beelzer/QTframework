"""Built-in theme presets."""

from __future__ import annotations

from qtframework.themes.base import (
    BorderRadius,
    ColorPalette,
    Shadows,
    Spacing,
    StandardTheme,
    Typography,
)


class LightTheme(StandardTheme):
    """Default light theme."""

    def __init__(self) -> None:
        """Initialize light theme."""
        super().__init__(
            name="light",
            display_name="Light Theme",
            description="Clean and modern light theme",
            author="Qt Framework",
            version="1.0.0",
            colors=ColorPalette(
                primary="#2196F3",
                primary_dark="#1976D2",
                primary_light="#42A5F5",
                secondary="#FFC107",
                secondary_dark="#FFA000",
                secondary_light="#FFD54F",
                background="#FFFFFF",
                surface="#F5F5F5",
                error="#F44336",
                warning="#FF9800",
                info="#2196F3",
                success="#4CAF50",
                text_primary="#212121",
                text_secondary="#757575",
                text_disabled="#BDBDBD",
                border="#E0E0E0",
                hover="#F0F0F0",
                selected="#E3F2FD",
            ),
            typography=Typography(
                font_family="Segoe UI, -apple-system, BlinkMacSystemFont, Arial, sans-serif",
                font_size_base=14,
            ),
            spacing=Spacing(),
            borders=BorderRadius(),
            shadows=Shadows(),
        )


class DarkTheme(StandardTheme):
    """Default dark theme."""

    def __init__(self) -> None:
        """Initialize dark theme."""
        super().__init__(
            name="dark",
            display_name="Dark Theme",
            description="Modern dark theme for reduced eye strain",
            author="Qt Framework",
            version="1.0.0",
            colors=ColorPalette(
                primary="#42A5F5",
                primary_dark="#2196F3",
                primary_light="#64B5F6",
                secondary="#FFD54F",
                secondary_dark="#FFC107",
                secondary_light="#FFE082",
                background="#1E1E1E",
                surface="#2D2D2D",
                error="#EF5350",
                warning="#FFA726",
                info="#42A5F5",
                success="#66BB6A",
                text_primary="#FFFFFF",
                text_secondary="#B0B0B0",
                text_disabled="#666666",
                border="#404040",
                hover="#3A3A3A",
                selected="#1A237E",
            ),
            typography=Typography(
                font_family="Segoe UI, -apple-system, BlinkMacSystemFont, Arial, sans-serif",
                font_size_base=14,
            ),
            spacing=Spacing(),
            borders=BorderRadius(),
            shadows=Shadows(
                sm="0 1px 3px rgba(0,0,0,0.3)",
                md="0 3px 6px rgba(0,0,0,0.4)",
                lg="0 10px 20px rgba(0,0,0,0.5)",
                xl="0 14px 28px rgba(0,0,0,0.6)",
            ),
        )


class MonokaiTheme(StandardTheme):
    """Monokai-inspired theme based on the popular text editor theme."""

    def __init__(self) -> None:
        """Initialize Monokai theme."""
        super().__init__(
            name="monokai",
            display_name="Monokai Theme",
            description="Dark theme inspired by the Monokai color scheme",
            author="Qt Framework",
            version="1.0.0",
            colors=ColorPalette(
                primary="#66D9EF",  # Cyan (Monokai blue)
                primary_dark="#49B8CC",
                primary_light="#83E0F2",
                secondary="#A6E22E",  # Green (Monokai green)
                secondary_dark="#85C21F",
                secondary_light="#B7E94E",
                background="#272822",  # Monokai background
                surface="#3E3D32",  # Slightly lighter surface
                error="#F92672",  # Pink/Magenta (Monokai red)
                warning="#FD971F",  # Orange
                info="#66D9EF",  # Cyan
                success="#A6E22E",  # Green
                text_primary="#F8F8F2",  # Monokai foreground
                text_secondary="#75715E",  # Brown/Gray (comments)
                text_disabled="#49483E",
                border="#75715E",
                hover="#49483E",
                selected="#49483E",
            ),
            typography=Typography(
                font_family="Consolas, 'Courier New', monospace",
                font_size_base=14,
            ),
            spacing=Spacing(),
            borders=BorderRadius(),
            shadows=Shadows(
                sm="0 1px 3px rgba(0,0,0,0.4)",
                md="0 3px 6px rgba(0,0,0,0.5)",
                lg="0 10px 20px rgba(0,0,0,0.6)",
                xl="0 14px 28px rgba(0,0,0,0.7)",
            ),
        )
