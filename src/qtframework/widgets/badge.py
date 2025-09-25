"""Badge widget for displaying status indicators and labels."""

from __future__ import annotations

from enum import Enum

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QLabel, QWidget


class BadgeVariant(Enum):
    """Badge variant types."""

    DEFAULT = "default"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"
    LIGHT = "light"
    DARK = "dark"


class Badge(QLabel):
    """A badge widget for displaying status indicators, counts, or labels.

    Badges are small labels that can be used to show status, counts, or
    categorization. They are fully theme-aware and get their colors from
    the current theme's badge color tokens.
    """

    def __init__(
        self,
        text: str = "",
        variant: BadgeVariant | str = BadgeVariant.DEFAULT,
        parent: QWidget | None = None,
    ):
        """Initialize the badge.

        Args:
            text: The badge text
            variant: The badge variant (color scheme)
            parent: Parent widget
        """
        super().__init__(text, parent)

        # Convert string to enum if needed
        if isinstance(variant, str):
            try:
                variant = BadgeVariant(variant)
            except ValueError:
                variant = BadgeVariant.DEFAULT

        self._variant = variant
        self._setup_widget()
        self._apply_variant_style()
        self._connect_theme_signals()

    def _setup_widget(self) -> None:
        """Setup the widget properties."""
        # Set alignment
        self.setAlignment(Qt.AlignCenter)

        # Set size policy to fit content
        self.setScaledContents(False)

        # Add some padding through margins
        self.setMargin(0)

        # Make font slightly smaller and bold
        font = self.font()
        font.setPointSize(font.pointSize() - 1)
        font.setBold(True)
        self.setFont(font)

    def _get_theme_colors(self) -> dict[str, str]:
        """Get colors for the current variant from the theme.

        Returns:
            Dictionary with 'bg', 'fg', and 'border' colors
        """
        # Try to get theme manager
        try:
            app = QApplication.instance()
            if hasattr(app, "theme_manager"):
                theme = app.theme_manager.get_current_theme()
                if theme and theme.tokens and theme.tokens.components:
                    components = theme.tokens.components

                    # Map variant to theme token names
                    variant_map = {
                        BadgeVariant.DEFAULT: "default",
                        BadgeVariant.PRIMARY: "primary",
                        BadgeVariant.SECONDARY: "secondary",
                        BadgeVariant.SUCCESS: "success",
                        BadgeVariant.WARNING: "warning",
                        BadgeVariant.DANGER: "danger",
                        BadgeVariant.INFO: "info",
                        BadgeVariant.LIGHT: "light",
                        BadgeVariant.DARK: "dark",
                    }

                    variant_name = variant_map.get(self._variant, "default")

                    # Get colors from theme
                    bg = getattr(components, f"badge_{variant_name}_bg", None)
                    fg = getattr(components, f"badge_{variant_name}_fg", None)
                    border = getattr(components, f"badge_{variant_name}_border", None)

                    if bg and fg and border:
                        return {"bg": bg, "fg": fg, "border": border}
        except Exception:  # noqa: S110  # nosec B110
            pass

        # Return fallback colors from theme's semantic tokens if badge colors not defined
        return self._get_fallback_colors()

    def _get_fallback_colors(self) -> dict[str, str]:
        """Get fallback colors from theme's semantic tokens or defaults.

        Returns:
            Dictionary with 'bg', 'fg', and 'border' colors
        """
        try:
            app = QApplication.instance()
            if hasattr(app, "theme_manager"):
                theme = app.theme_manager.get_current_theme()
                if theme and theme.tokens:
                    tokens = theme.tokens

                    # Use semantic tokens as fallback
                    fallback_map = {
                        BadgeVariant.DEFAULT: {
                            "bg": tokens.semantic.bg_tertiary,
                            "fg": tokens.semantic.fg_primary,
                            "border": tokens.semantic.border_default,
                        },
                        BadgeVariant.PRIMARY: {
                            "bg": tokens.semantic.action_primary,
                            "fg": tokens.semantic.fg_on_accent or tokens.primitive.white,
                            "border": tokens.semantic.action_primary,
                        },
                        BadgeVariant.SECONDARY: {
                            "bg": tokens.primitive.gray_500,
                            "fg": tokens.primitive.white,
                            "border": tokens.primitive.gray_600,
                        },
                        BadgeVariant.SUCCESS: {
                            "bg": tokens.semantic.feedback_success,
                            "fg": tokens.semantic.fg_on_accent or tokens.primitive.white,
                            "border": tokens.semantic.feedback_success,
                        },
                        BadgeVariant.WARNING: {
                            "bg": tokens.semantic.feedback_warning,
                            "fg": tokens.primitive.black,
                            "border": tokens.semantic.feedback_warning,
                        },
                        BadgeVariant.DANGER: {
                            "bg": tokens.semantic.feedback_error,
                            "fg": tokens.semantic.fg_on_accent or tokens.primitive.white,
                            "border": tokens.semantic.feedback_error,
                        },
                        BadgeVariant.INFO: {
                            "bg": tokens.semantic.feedback_info,
                            "fg": tokens.primitive.black,
                            "border": tokens.semantic.feedback_info,
                        },
                        BadgeVariant.LIGHT: {
                            "bg": tokens.primitive.gray_100,
                            "fg": tokens.semantic.fg_primary,
                            "border": tokens.semantic.border_subtle,
                        },
                        BadgeVariant.DARK: {
                            "bg": tokens.primitive.gray_900,
                            "fg": tokens.primitive.white,
                            "border": tokens.primitive.gray_900,
                        },
                    }

                    colors = fallback_map.get(self._variant, fallback_map[BadgeVariant.DEFAULT])

                    # Filter out None values and return if we have all colors
                    if colors["bg"] and colors["fg"] and colors["border"]:
                        return colors
        except Exception:  # noqa: S110  # nosec B110
            pass

        # Last resort: use minimal theme-aware colors
        return self._get_minimal_colors()

    def _get_minimal_colors(self) -> dict[str, str]:
        """Get minimal colors when theme is not available.

        Uses only palette colors from Qt, no hardcoded hex values.

        Returns:
            Dictionary with 'bg', 'fg', and 'border' colors
        """
        palette = self.palette()

        # Use palette colors - no hardcoded values!
        if self._variant == BadgeVariant.LIGHT:
            return {
                "bg": palette.color(QPalette.Window).name(),
                "fg": palette.color(QPalette.WindowText).name(),
                "border": palette.color(QPalette.Mid).name(),
            }
        if self._variant == BadgeVariant.DARK:
            return {
                "bg": palette.color(QPalette.Shadow).name(),
                "fg": palette.color(QPalette.BrightText).name(),
                "border": palette.color(QPalette.Dark).name(),
            }
        # For all other variants, use button colors as a reasonable default
        return {
            "bg": palette.color(QPalette.Button).name(),
            "fg": palette.color(QPalette.ButtonText).name(),
            "border": palette.color(QPalette.Mid).name(),
        }

    def _apply_variant_style(self) -> None:
        """Apply styling based on the variant using theme colors only."""
        colors = self._get_theme_colors()

        # Apply the style
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {colors["bg"]};
                color: {colors["fg"]};
                border: 1px solid {colors["border"]};
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
            }}
        """)

    @property
    def variant(self) -> BadgeVariant:
        """Get the current variant."""
        return self._variant

    @variant.setter
    def variant(self, value: BadgeVariant | str) -> None:
        """Set the badge variant.

        Args:
            value: The variant to set
        """
        if isinstance(value, str):
            try:
                value = BadgeVariant(value)
            except ValueError:
                value = BadgeVariant.DEFAULT

        self._variant = value
        self._apply_variant_style()

    def set_count(self, count: int) -> None:
        """Set the badge to display a count.

        Args:
            count: The count to display
        """
        if count > 999:
            self.setText("999+")
        elif count > 99:
            self.setText(f"{count}")
        else:
            self.setText(str(count))

    def set_rounded(self, rounded: bool = True) -> None:
        """Set whether the badge should be fully rounded (pill-shaped).

        Args:
            rounded: Whether to make the badge pill-shaped
        """
        if rounded:
            # Make it pill-shaped
            self.setStyleSheet(
                self.styleSheet().replace("border-radius: 4px", "border-radius: 12px")
            )
        else:
            # Make it slightly rounded
            self.setStyleSheet(
                self.styleSheet().replace("border-radius: 12px", "border-radius: 4px")
            )

    def refresh_style(self) -> None:
        """Refresh the badge style from the current theme.

        This should be called when the theme changes.
        """
        self._apply_variant_style()

    def _connect_theme_signals(self) -> None:
        """Connect to theme manager signals for automatic style updates."""
        try:
            app = QApplication.instance()
            if hasattr(app, "theme_manager"):
                app.theme_manager.theme_changed.connect(self._on_theme_changed)
        except Exception:  # noqa: S110  # nosec B110
            pass

    def _on_theme_changed(self, theme_name: str) -> None:
        """Handle theme change event.

        Args:
            theme_name: Name of the new theme
        """
        self.refresh_style()
