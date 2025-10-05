"""Modern theme manager with JSON/YAML support.

This module provides a comprehensive theme management system that supports
built-in themes, custom theme loading from YAML files, and programmatic
theme creation.

Example:
    Create and register a custom theme::

        from qtframework.themes.theme_manager import ThemeManager
        from qtframework.themes.theme import Theme
        from qtframework.themes.tokens import DesignTokens, SemanticColors
        from pathlib import Path

        # Initialize theme manager
        theme_manager = ThemeManager(themes_dir=Path("my_themes"))

        # Use built-in themes
        theme_manager.set_theme("light")
        theme_manager.set_theme("dark")

        # Create a custom theme programmatically
        custom_theme = theme_manager.create_theme_from_colors(
            name="ocean",
            primary_color="#0077BE",
            background_color="#F0F8FF",
            is_dark=False,
            display_name="Ocean Theme",
            description="A calming blue ocean theme",
        )

        # Register the custom theme
        theme_manager.register_theme(custom_theme)
        theme_manager.set_theme("ocean")

        # Apply theme to application
        app = QApplication.instance()
        stylesheet = theme_manager.get_stylesheet()
        app.setStyleSheet(stylesheet)

        # Listen for theme changes
        theme_manager.theme_changed.connect(
            lambda name: print(f"Theme changed to: {name}")
        )

        # Export theme for sharing
        theme_manager.export_theme("ocean", "ocean_theme.yaml")

See Also:
    :class:`Theme`: Theme class with design tokens
    :mod:`qtframework.themes.tokens`: Design token system
    :class:`qtframework.core.application`: Application class that integrates themes
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

from qtframework.themes.builtin_themes import BUILTIN_THEMES
from qtframework.themes.theme import Theme
from qtframework.utils.logger import get_logger
from qtframework.utils.resources import ResourceManager


logger = get_logger(__name__)


class ThemeManager(QObject):
    """Modern theme manager for handling application themes."""

    theme_changed = Signal(str)  # Emits theme name when changed

    def __init__(
        self,
        themes_dir: Path | None = None,
        font_scale: int = 100,
        resource_manager: ResourceManager | None = None,
    ) -> None:
        """Initialize theme manager.

        Args:
            themes_dir: Directory to load custom themes from (default: resources/themes)
            font_scale: Font scale percentage (50-200, default 100)
            resource_manager: Optional resource manager for themes and icons
        """
        super().__init__()
        self._themes: dict[str, Theme] = {}
        self._current_theme_name: str = "light"
        self._requested_theme_name: str = "light"  # Track what user requested (e.g., 'auto')
        self._resource_manager = resource_manager or ResourceManager()
        self._themes_dir = themes_dir or self._get_default_themes_dir()
        self._font_scale: int = font_scale

        # Load built-in themes
        self._load_builtin_themes()

        # Load custom themes
        self._load_custom_themes()

    def _get_default_themes_dir(self) -> Path:
        """Get default themes directory from resource manager.

        Returns:
            Path to themes directory
        """
        # Use resource manager to find themes directory
        search_paths = self._resource_manager.get_search_paths("themes")
        if search_paths:
            return search_paths[0]
        return Path("resources/themes")

    def _load_builtin_themes(self) -> None:
        """Load all built-in themes."""
        for theme_name, theme_factory in BUILTIN_THEMES.items():
            try:
                theme = theme_factory()
                # Inject resource manager into theme's stylesheet generator
                theme._stylesheet_generator = theme._stylesheet_generator.__class__(
                    self._resource_manager
                )
                self._themes[theme_name] = theme
                logger.debug("Loaded built-in theme: %s", theme_name)
            except Exception as e:
                logger.exception("Failed to load built-in theme '%s': %s", theme_name, e)

    def _load_custom_themes(self) -> None:
        """Load custom themes from all search paths.

        Loads themes from all paths in the resource manager's theme search paths,
        allowing applications to provide their own themes that override framework themes.
        """
        # Get all theme search paths from resource manager
        search_paths = self._resource_manager.get_search_paths("themes")

        if not search_paths:
            logger.debug("No theme search paths configured")
            return

        # Load themes from all search paths (later paths can override earlier ones)
        for themes_dir in search_paths:
            if not themes_dir.exists():
                logger.debug(f"Themes directory does not exist: {themes_dir}")
                continue

            # Load YAML themes only
            for theme_file in themes_dir.glob("*.yaml"):
                self._load_theme_file(theme_file)

    def _load_theme_file(self, theme_file: Path) -> None:
        """Load a theme from a YAML file.

        Args:
            theme_file: Path to the theme file

        Raises:
            ValueError: If theme file format is invalid
            yaml.YAMLError: If YAML parsing fails
            FileNotFoundError: If theme file does not exist
        """
        try:
            if theme_file.suffix != ".yaml":
                logger.warning("Theme files must use .yaml extension: %s", theme_file)
                return

            theme = Theme.from_yaml(theme_file)

            # Check for name conflicts - custom themes override built-in themes
            if theme.name in self._themes:
                logger.info(
                    f"Custom theme '{theme.name}' from {theme_file} overrides built-in theme"
                )

            # Inject resource manager into theme's stylesheet generator
            theme._stylesheet_generator = theme._stylesheet_generator.__class__(
                self._resource_manager
            )

            self._themes[theme.name] = theme
            logger.info(f"Loaded custom theme '{theme.name}' from {theme_file}")

        except Exception as e:
            logger.exception("Failed to load theme from %s: %s", theme_file, e)

    def register_theme(self, theme: Theme, override: bool = True) -> bool:
        """Register a theme programmatically.

        Args:
            theme: Theme to register
            override: If True, override existing theme with same name (default: True)

        Returns:
            True if registered successfully
        """
        if theme.name in self._themes:
            if not override:
                logger.warning(f"Theme '{theme.name}' already exists")
                return False
            logger.info(f"Theme '{theme.name}' will override existing theme")

        # Inject resource manager into theme's stylesheet generator
        theme._stylesheet_generator = theme._stylesheet_generator.__class__(self._resource_manager)

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

    def detect_system_theme(self) -> str:
        """Detect the system's light/dark mode preference.

        Returns:
            'dark' if system is in dark mode, 'light' otherwise
        """
        app = QApplication.instance()
        if app and isinstance(app, QApplication):
            palette = app.palette()
            # Check if window background is darker than text color
            bg_color = palette.color(QPalette.ColorRole.Window)
            # Calculate luminance (perceived brightness)
            luminance = (
                0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue()
            ) / 255
            # If luminance is less than 0.5, it's a dark theme
            if luminance < 0.5:
                logger.debug("Detected system dark mode")
                return "dark"
        logger.debug("Detected system light mode")
        return "light"

    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme.

        Args:
            theme_name: Name of the theme to activate (use 'auto' for system theme detection)

        Returns:
            True if theme was set successfully
        """
        # Handle auto theme - detect system preference
        actual_theme_name = theme_name
        if theme_name == "auto":
            actual_theme_name = self.detect_system_theme()
            logger.info("Auto theme: detected system preference as '%s'", actual_theme_name)

        if actual_theme_name not in self._themes:
            logger.error("Theme '%s' not found", actual_theme_name)
            return False

        # Check if both the requested theme and actual theme are unchanged
        if (
            actual_theme_name == self._current_theme_name
            and theme_name == self._requested_theme_name
        ):
            logger.debug("Theme '%s' is already active", actual_theme_name)
            return True

        old_theme = self._current_theme_name
        self._current_theme_name = actual_theme_name
        self._requested_theme_name = theme_name  # Store what user requested
        logger.info(
            "Theme changed from '%s' to '%s' (requested: '%s')",
            old_theme,
            actual_theme_name,
            theme_name,
        )

        # Emit signal for theme change with the actual theme (not 'auto')
        self.theme_changed.emit(actual_theme_name)
        return True

    def set_font_scale(self, scale_percent: int) -> None:
        """Set the font scale percentage.

        Args:
            scale_percent: Font scale percentage (50-200)
        """
        self._font_scale = scale_percent
        logger.debug("Font scale set to %d%%", scale_percent)

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
            # Apply font scaling to a copy of the theme's tokens
            from copy import deepcopy

            tokens = deepcopy(theme.tokens)
            tokens.apply_font_scale(self._font_scale)

            # Generate stylesheet with scaled tokens
            return theme._stylesheet_generator.generate(tokens, theme.custom_styles)
        except Exception as e:
            logger.exception("Failed to generate stylesheet for theme '%s': %s", theme_name, e)
            return ""

    def list_themes(self) -> list[str]:
        """List all available theme names.

        Returns:
            List of theme names with 'auto' first
        """
        themes = list(self._themes.keys())
        # Always put 'auto' first in the list
        if "auto" not in themes:
            themes.insert(0, "auto")
        return themes

    def get_theme_info(self, theme_name: str) -> dict[str, str] | None:
        """Get information about a theme.

        Args:
            theme_name: Name of the theme

        Returns:
            Theme information dictionary or None
        """
        # Handle 'auto' theme specially
        if theme_name == "auto":
            return {
                "name": "auto",
                "display_name": "Auto (System)",
                "description": "Automatically match system light/dark mode preference",
                "author": "Qt Framework",
                "version": "1.0.0",
            }

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
