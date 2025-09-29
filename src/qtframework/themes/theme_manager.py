"""Modern theme manager with JSON/YAML support."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal

from qtframework.themes.builtin_themes import BUILTIN_THEMES
from qtframework.themes.theme import Theme
from qtframework.utils.logger import get_logger


logger = get_logger(__name__)


class ThemeManager(QObject):
    """Modern theme manager for handling application themes."""

    theme_changed = Signal(str)  # Emits theme name when changed

    def __init__(self, themes_dir: Path | None = None) -> None:
        """Initialize theme manager.

        Args:
            themes_dir: Directory to load custom themes from (default: resources/themes)
        """
        super().__init__()
        self._themes: dict[str, Theme] = {}
        self._current_theme_name: str = "light"
        self._themes_dir = themes_dir or Path("resources/themes")

        # Load built-in themes
        self._load_builtin_themes()

        # Load custom themes
        self._load_custom_themes()

    def _load_builtin_themes(self) -> None:
        """Load all built-in themes."""
        for theme_name, theme_factory in BUILTIN_THEMES.items():
            try:
                theme = theme_factory()
                self._themes[theme_name] = theme
                logger.debug("Loaded built-in theme: %s", theme_name)
            except Exception as e:
                logger.exception("Failed to load built-in theme '%s': %s", theme_name, e)

    def _load_custom_themes(self) -> None:
        """Load custom themes from the themes directory."""
        if not self._themes_dir.exists():
            logger.debug(f"Themes directory does not exist: {self._themes_dir}")
            return

        # Load YAML themes only
        for theme_file in self._themes_dir.glob("*.yaml"):
            self._load_theme_file(theme_file)

    def _load_theme_file(self, theme_file: Path) -> None:
        """Load a theme from a YAML file.

        Args:
            theme_file: Path to the theme file
        """
        try:
            if theme_file.suffix != ".yaml":
                logger.warning("Theme files must use .yaml extension: %s", theme_file)
                return

            theme = Theme.from_yaml(theme_file)

            # Check for name conflicts
            if theme.name in self._themes:
                logger.warning(
                    f"Theme '{theme.name}' from {theme_file} conflicts with existing theme. "
                    f"Using existing theme."
                )
                return

            self._themes[theme.name] = theme
            logger.info(f"Loaded custom theme '{theme.name}' from {theme_file}")

        except Exception as e:
            logger.exception("Failed to load theme from %s: %s", theme_file, e)

    def register_theme(self, theme: Theme) -> bool:
        """Register a theme programmatically.

        Args:
            theme: Theme to register

        Returns:
            True if registered successfully
        """
        if theme.name in self._themes:
            logger.warning(f"Theme '{theme.name}' already exists")
            return False

        self._themes[theme.name] = theme
        logger.debug(f"Registered theme: {theme.name}")
        return True

    def unregister_theme(self, theme_name: str) -> bool:
        """Unregister a theme.

        Args:
            theme_name: Name of the theme to unregister

        Returns:
            True if unregistered successfully
        """
        if theme_name not in self._themes:
            logger.warning("Theme '%s' not found", theme_name)
            return False

        if theme_name == self._current_theme_name:
            logger.error("Cannot unregister the current theme")
            return False

        del self._themes[theme_name]
        logger.debug("Unregistered theme: %s", theme_name)
        return True

    def get_theme(self, theme_name: str | None = None) -> Theme | None:
        """Get a theme by name.

        Args:
            theme_name: Theme name, or None for current theme

        Returns:
            Theme instance or None if not found
        """
        name = theme_name or self._current_theme_name
        return self._themes.get(name)

    def get_current_theme(self) -> Theme:
        """Get the current active theme.

        Returns:
            Current theme instance
        """
        theme = self._themes.get(self._current_theme_name)
        if not theme:
            # Fallback to light theme if current theme is missing
            logger.error(
                f"Current theme '{self._current_theme_name}' not found, falling back to 'light'"
            )
            self._current_theme_name = "light"
            theme = self._themes.get("light")
            if not theme:
                # Create a default light theme if even that's missing
                from qtframework.themes.builtin_themes import create_light_theme

                theme = create_light_theme()
                self._themes["light"] = theme
        return theme

    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme.

        Args:
            theme_name: Name of the theme to activate

        Returns:
            True if theme was set successfully
        """
        if theme_name not in self._themes:
            logger.error("Theme '%s' not found", theme_name)
            return False

        if theme_name == self._current_theme_name:
            logger.debug("Theme '%s' is already active", theme_name)
            return True

        old_theme = self._current_theme_name
        self._current_theme_name = theme_name
        logger.info("Theme changed from '%s' to '%s'", old_theme, theme_name)

        # Emit signal for theme change
        self.theme_changed.emit(theme_name)
        return True

    def get_stylesheet(self, theme_name: str | None = None) -> str:
        """Get the stylesheet for a theme.

        Args:
            theme_name: Theme name, or None for current theme

        Returns:
            Generated Qt stylesheet string
        """
        theme = self.get_theme(theme_name)
        if not theme:
            logger.error("Theme '%s' not found", theme_name)
            return ""

        try:
            return theme.generate_stylesheet()
        except Exception as e:
            logger.exception("Failed to generate stylesheet for theme '%s': %s", theme_name, e)
            return ""

    def list_themes(self) -> list[str]:
        """List all available theme names.

        Returns:
            List of theme names
        """
        return list(self._themes.keys())

    def get_theme_info(self, theme_name: str) -> dict[str, str] | None:
        """Get information about a theme.

        Args:
            theme_name: Name of the theme

        Returns:
            Theme information dictionary or None
        """
        theme = self.get_theme(theme_name)
        if not theme:
            return None

        return {
            "name": theme.name,
            "display_name": theme.display_name,
            "description": theme.description,
            "author": theme.author,
            "version": theme.version,
        }

    def export_theme(self, theme_name: str, export_path: str | Path, format: str = "json") -> bool:
        """Export a theme to a file.

        Args:
            theme_name: Name of the theme to export
            export_path: Path to export the theme to
            format: Export format ('yaml' or 'yml' only)

        Returns:
            True if exported successfully
        """
        theme = self.get_theme(theme_name)
        if not theme:
            logger.error("Theme '%s' not found", theme_name)
            return False

        export_path = Path(export_path)

        try:
            if format not in {"yaml", "yml"}:
                logger.error("Only YAML export is supported. Got: %s", format)
                return False

            theme.save_yaml(export_path)

            logger.info("Exported theme '%s' to %s", theme_name, export_path)
            return True

        except Exception as e:
            logger.exception("Failed to export theme '%s': %s", theme_name, e)
            return False

    def reload_themes(self) -> None:
        """Reload all custom themes from disk."""
        # Remove all custom themes (keep built-in ones)
        custom_themes = [name for name in self._themes if name not in BUILTIN_THEMES]

        for theme_name in custom_themes:
            del self._themes[theme_name]

        # Reload custom themes
        self._load_custom_themes()
        logger.info("Reloaded custom themes")

    def create_theme_from_colors(
        self, name: str, primary_color: str, background_color: str, is_dark: bool = False, **kwargs
    ) -> Theme:
        """Create a simple theme from basic color values.

        Args:
            name: Theme name
            primary_color: Primary accent color
            background_color: Background color
            is_dark: Whether this is a dark theme
            **kwargs: Additional theme properties

        Returns:
            New theme instance
        """
        from qtframework.themes.tokens import DesignTokens, SemanticColors

        # Create tokens with basic colors
        tokens = DesignTokens()

        # Set semantic colors based on provided values
        if is_dark:
            tokens.semantic = SemanticColors(
                bg_primary=background_color,
                fg_primary="#FFFFFF",
                action_primary=primary_color,
                # ... other colors would be derived
            )
        else:
            tokens.semantic = SemanticColors(
                bg_primary=background_color,
                fg_primary="#000000",
                action_primary=primary_color,
                # ... other colors would be derived
            )

        return Theme(
            name=name,
            display_name=kwargs.get("display_name", name.title()),
            description=kwargs.get("description", f"Custom theme: {name}"),
            author=kwargs.get("author", "User"),
            version=kwargs.get("version", "1.0.0"),
            tokens=tokens,
        )
