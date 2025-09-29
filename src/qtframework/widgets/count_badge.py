"""Count/Notification badge widget for displaying numbers and counts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QLabel

from .badge import BadgeVariant


if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


class CountBadge(QLabel):
    """A compact badge widget optimized for displaying counts and notifications.

    Count badges are more compact than regular badges, with a circular or pill
    shape that's optimized for showing numbers. They're commonly used for:
    - Notification counts
    - Unread message indicators
    - Shopping cart item counts
    - Alert counts
    """

    def __init__(
        self,
        count: int = 0,
        variant: BadgeVariant | str = BadgeVariant.DANGER,
        parent: QWidget | None = None,
        max_count: int = 99,
    ) -> None:
        """Initialize the count badge.

        Args:
            count: The count to display
            variant: The badge variant (color scheme)
            parent: Parent widget
            max_count: Maximum count to display (shows "max+" for higher values)
        """
        super().__init__(parent)

        # Convert string to enum if needed
        if isinstance(variant, str):
            try:
                variant = BadgeVariant(variant)
            except ValueError:
                variant = BadgeVariant.DANGER

        self._variant = variant
        self._count = count
        self._max_count = max_count
        self._setup_widget()
        self._update_count_display()
        self._apply_variant_style()
        self._connect_theme_signals()

    def _setup_widget(self) -> None:
        """Setup the widget properties."""
        # Set alignment
        self.setAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]

        # Make font bold and slightly smaller than default
        font = self.font()
        font.setPointSize(max(10, font.pointSize() - 1))  # Slightly smaller than regular badges
        font.setBold(True)
        self.setFont(font)

        # Set minimum size for circular appearance
        self.setMinimumSize(QSize(20, 20))

    def _update_count_display(self) -> None:
        """Update the displayed count text."""
        if self._count <= 0:
            self.setText("")
            self.hide()
        else:
            self.show()
            if self._count > self._max_count:
                self.setText(f"{self._max_count}+")
            else:
                self.setText(str(self._count))

    def _get_theme_colors(self) -> dict[str, str]:
        """Get colors for the current variant from the theme.

        Returns:
            Dictionary with 'bg', 'fg', and 'border' colors
        """
        # Try to get theme manager
        try:
            app = QApplication.instance()
            if app and hasattr(app, "theme_manager"):
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

                    variant_name = variant_map.get(self._variant, "danger")

                    # Get colors from theme
                    bg = getattr(components, f"badge_{variant_name}_bg", None)
                    fg = getattr(components, f"badge_{variant_name}_fg", None)
                    border = getattr(components, f"badge_{variant_name}_border", None)

                    if bg and fg and border:
                        return {"bg": bg, "fg": fg, "border": border}
        except Exception:  # noqa: S110  # nosec B110
            pass

        # Return fallback colors
        return self._get_fallback_colors()

    def _get_fallback_colors(self) -> dict[str, str]:
        """Get fallback colors from theme's semantic tokens or defaults.

        Returns:
            Dictionary with 'bg', 'fg', and 'border' colors
        """
        try:
            app = QApplication.instance()
            if app and hasattr(app, "theme_manager"):
                theme = app.theme_manager.get_current_theme()
                if theme and theme.tokens:
                    tokens = theme.tokens

                    # For count badges, use more vibrant colors by default
                    fallback_map = {
                        BadgeVariant.DEFAULT: {
                            "bg": tokens.semantic.feedback_error,
                            "fg": tokens.semantic.fg_on_accent or tokens.primitive.white,
                            "border": tokens.semantic.feedback_error,
                        },
                        BadgeVariant.PRIMARY: {
                            "bg": tokens.semantic.action_primary,
                            "fg": tokens.semantic.fg_on_accent or tokens.primitive.white,
                            "border": tokens.semantic.action_primary,
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
                        BadgeVariant.SECONDARY: {
                            "bg": tokens.primitive.gray_500,
                            "fg": tokens.primitive.white,
                            "border": tokens.primitive.gray_600,
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

                    colors = fallback_map.get(self._variant, fallback_map[BadgeVariant.DANGER])

                    # Filter out None values and return if we have all colors
                    if colors["bg"] and colors["fg"] and colors["border"]:
                        return colors
        except Exception:  # noqa: S110  # nosec B110
            pass

        # Last resort: use minimal theme-aware colors
        palette = self.palette()
        return {
            "bg": palette.color(QPalette.Highlight).name(),  # type: ignore[attr-defined]
            "fg": palette.color(QPalette.HighlightedText).name(),  # type: ignore[attr-defined]
            "border": palette.color(QPalette.Highlight).name(),  # type: ignore[attr-defined]
        }

    def _apply_variant_style(self) -> None:
        """Apply styling for count badges - more compact and circular."""
        colors = self._get_theme_colors()

        # Calculate dimensions based on content
        text_len = len(self.text())
        if text_len <= 1:
            # Single digit - make it circular
            size = 20
            padding = "2px 0px"
            min_width = f"{size}px"
            border_radius = f"{size // 2}px"
        elif text_len == 2:
            # Two digits - slightly wider
            padding = "2px 4px"
            min_width = "24px"
            border_radius = "10px"
        else:
            # Three+ digits (99+) - pill shaped
            padding = "2px 6px"
            min_width = "32px"
            border_radius = "12px"

        # Apply the style - more compact than regular badges
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {colors["bg"]};
                color: {colors["fg"]};
                border: 1px solid {colors["border"]};
                border-radius: {border_radius};
                padding: {padding};
                min-width: {min_width};
                min-height: 20px;
                max-height: 20px;
                font-weight: bold;
                font-size: 12px;
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
                value = BadgeVariant.DANGER

        self._variant = value
        self._apply_variant_style()

    @property
    def count(self) -> int:
        """Get the current count."""
        return self._count

    @count.setter
    def count(self, value: int) -> None:
        """Set the count to display.

        Args:
            value: The count to display
        """
        self._count = value
        self._update_count_display()
        self._apply_variant_style()  # Reapply style for size adjustment

    def increment(self, by: int = 1) -> None:
        """Increment the count.

        Args:
            by: Amount to increment by
        """
        self.count = self._count + by

    def decrement(self, by: int = 1) -> None:
        """Decrement the count.

        Args:
            by: Amount to decrement by
        """
        self.count = max(0, self._count - by)

    def clear(self) -> None:
        """Clear the count (set to 0 and hide)."""
        self.count = 0

    def refresh_style(self) -> None:
        """Refresh the badge style from the current theme."""
        self._apply_variant_style()

    def _connect_theme_signals(self) -> None:
        """Connect to theme manager signals for automatic style updates."""
        try:
            app = QApplication.instance()
            if app and hasattr(app, "theme_manager"):
                app.theme_manager.theme_changed.connect(self._on_theme_changed)
        except Exception:  # noqa: S110  # nosec B110
            pass

    def _on_theme_changed(self, theme_name: str) -> None:
        """Handle theme change event.

        Args:
            theme_name: Name of the new theme
        """
        self.refresh_style()
