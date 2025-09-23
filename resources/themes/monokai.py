"""Monokai theme - A dark theme inspired by the popular text editor color scheme."""

from qtframework.themes.base import (
    BorderRadius,
    ColorPalette,
    Shadows,
    Spacing,
    StandardTheme,
    Typography,
)


class MonokaiTheme(StandardTheme):
    """Monokai-inspired theme based on the popular text editor theme."""

    def __init__(self) -> None:
        """Initialize Monokai theme."""
        super().__init__(
            name="monokai",
            display_name="Monokai Theme",
            description="Dark theme inspired by the Monokai color scheme",
            author="Qt Framework Community",
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
                # Chart colors - Monokai specific
                chart_grid="#49483E",
                chart_axis="#75715E",
                chart_data_1="#66D9EF",  # Cyan
                chart_data_2="#A6E22E",  # Green
                chart_data_3="#FD971F",  # Orange
                chart_data_4="#F92672",  # Pink
                chart_data_5="#AE81FF",  # Purple
                chart_data_6="#F8F8F2",  # Light gray
                # Table colors - Monokai specific
                table_header_bg="#3E3D32",
                table_row_bg_alt="#2F2F2A",
                table_row_hover="#49483E",
                table_row_selected="#49483E",
                table_grid="#49483E",
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