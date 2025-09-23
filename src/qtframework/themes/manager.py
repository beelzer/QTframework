"""Theme manager for handling multiple themes."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal

from qtframework.themes.base import StandardTheme, Theme
from qtframework.themes.presets import DarkTheme, LightTheme
from qtframework.utils.logger import get_logger

logger = get_logger(__name__)


class ThemeManager(QObject):
    """Manager for handling application themes."""

    theme_changed = Signal(str)

    def __init__(self) -> None:
        """Initialize theme manager."""
        super().__init__()
        self._themes: dict[str, Theme] = {}
        self._current_theme: str = "light"

        self._load_default_themes()

    def _load_default_themes(self) -> None:
        """Load default built-in themes."""
        self.register_theme(LightTheme())
        self.register_theme(DarkTheme())

        # Load third-party themes from resources/themes
        self._load_third_party_themes()

        logger.info(f"Loaded {len(self._themes)} themes")

    def _load_third_party_themes(self) -> None:
        """Load third-party themes from resources/themes directory."""
        themes_dir = Path("resources/themes")
        if not themes_dir.exists():
            return

        for theme_file in themes_dir.glob("*.py"):
            if theme_file.name == "__init__.py":
                continue

            try:
                # Load the module
                module_name = f"theme_{theme_file.stem}"
                spec = importlib.util.spec_from_file_location(module_name, theme_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)

                    # Find and register theme classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and
                            issubclass(attr, Theme) and
                            attr not in (Theme, StandardTheme)):
                            theme_instance = attr()
                            self.register_theme(theme_instance)
                            logger.info(f"Loaded third-party theme: {theme_instance.display_name}")

            except Exception as e:
                logger.error(f"Failed to load theme from {theme_file}: {e}")

    def register_theme(self, theme: Theme) -> None:
        """Register a theme.

        Args:
            theme: Theme to register
        """
        self._themes[theme.name] = theme
        logger.debug(f"Registered theme: {theme.display_name}")

    def unregister_theme(self, theme_name: str) -> None:
        """Unregister a theme.

        Args:
            theme_name: Name of theme to unregister
        """
        if theme_name in self._themes:
            del self._themes[theme_name]
            logger.debug(f"Unregistered theme: {theme_name}")

    def get_theme(self, theme_name: str | None = None) -> Theme | None:
        """Get a theme by name.

        Args:
            theme_name: Theme name, or None for current theme

        Returns:
            Theme instance or None if not found
        """
        name = theme_name or self._current_theme
        return self._themes.get(name)

    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme.

        Args:
            theme_name: Name of theme to set

        Returns:
            True if theme was set successfully
        """
        if theme_name not in self._themes:
            logger.error(f"Theme not found: {theme_name}")
            return False

        self._current_theme = theme_name
        self.theme_changed.emit(theme_name)
        logger.info(f"Theme set to: {theme_name}")
        return True

    def get_current_theme_name(self) -> str:
        """Get current theme name.

        Returns:
            Current theme name
        """
        return self._current_theme

    def get_stylesheet(self, theme_name: str | None = None) -> str:
        """Get stylesheet for a theme.

        Args:
            theme_name: Theme name, or None for current theme

        Returns:
            Qt stylesheet string
        """
        theme = self.get_theme(theme_name)
        if theme:
            return theme.generate_stylesheet()
        return ""

    def list_themes(self) -> list[str]:
        """List all available theme names.

        Returns:
            List of theme names
        """
        return list(self._themes.keys())

    def get_theme_info(self, theme_name: str) -> dict[str, Any] | None:
        """Get theme information.

        Args:
            theme_name: Theme name

        Returns:
            Theme info dictionary or None
        """
        theme = self.get_theme(theme_name)
        if theme:
            return {
                "name": theme.name,
                "display_name": theme.display_name,
                "description": theme.description,
                "author": theme.author,
                "version": theme.version,
            }
        return None

