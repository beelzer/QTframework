"""Theme manager for handling multiple themes."""

from __future__ import annotations

import json
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
        self._custom_theme_dir: Path | None = None

        self._load_default_themes()

    def _load_default_themes(self) -> None:
        """Load default built-in themes."""
        from qtframework.themes.presets import MonokaiTheme

        self.register_theme(LightTheme())
        self.register_theme(DarkTheme())
        self.register_theme(MonokaiTheme())

        logger.info(f"Loaded {len(self._themes)} default themes")

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

    def load_theme_from_file(self, file_path: Path | str) -> bool:
        """Load a theme from a JSON file.

        Args:
            file_path: Path to theme file

        Returns:
            True if theme was loaded successfully
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"Theme file not found: {file_path}")
            return False

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # Use JsonTheme for JSON-loaded themes
            from qtframework.themes.json_theme import JsonTheme
            theme = JsonTheme.from_dict(data)
            self.register_theme(theme)
            logger.info(f"Loaded theme from: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load theme from {file_path}: {e}")
            return False

    def save_theme_to_file(self, theme_name: str, file_path: Path | str) -> bool:
        """Save a theme to a JSON file.

        Args:
            theme_name: Name of theme to save
            file_path: Path to save file

        Returns:
            True if theme was saved successfully
        """
        theme = self.get_theme(theme_name)
        if not theme:
            logger.error(f"Theme not found: {theme_name}")
            return False

        file_path = Path(file_path)
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(theme.to_dict(), f, indent=2)

            logger.info(f"Saved theme to: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save theme to {file_path}: {e}")
            return False

    def load_themes_from_directory(self, directory: Path | str) -> int:
        """Load all theme files from a directory.

        Args:
            directory: Directory path

        Returns:
            Number of themes loaded
        """
        directory = Path(directory)
        if not directory.exists():
            logger.error(f"Directory not found: {directory}")
            return 0

        count = 0
        for file_path in directory.glob("*.json"):
            if self.load_theme_from_file(file_path):
                count += 1

        logger.info(f"Loaded {count} themes from {directory}")
        return count

    def set_custom_theme_directory(self, directory: Path | str) -> None:
        """Set custom theme directory.

        Args:
            directory: Directory path
        """
        self._custom_theme_dir = Path(directory)
        if self._custom_theme_dir.exists():
            self.load_themes_from_directory(self._custom_theme_dir)
