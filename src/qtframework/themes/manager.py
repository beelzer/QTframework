"""Theme manager for handling multiple themes."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal

from qtframework.themes.base import StandardTheme, Theme
from qtframework.themes.presets import DarkTheme, LightTheme
from qtframework.utils.exceptions import ThemeError, SecurityError
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
                self._load_theme_file(theme_file)
            except ThemeError as e:
                logger.error(f"Theme loading failed: {e}")
            except SecurityError as e:
                logger.error(f"Security violation while loading theme: {e}")
            except Exception as e:
                logger.error(f"Unexpected error loading theme from {theme_file}: {e}")

    def _load_theme_file(self, theme_file: Path) -> None:
        """Load a single theme file with validation.

        Args:
            theme_file: Path to theme file

        Raises:
            ThemeError: If theme loading fails
            SecurityError: If security validation fails
        """
        # Security validation
        if not self._validate_theme_file_security(theme_file):
            raise SecurityError(
                f"Theme file failed security validation: {theme_file}",
                security_context="theme_loading",
                attempted_action="load_third_party_theme"
            )

        try:
            # Load the module
            module_name = f"theme_{theme_file.stem}"
            spec = importlib.util.spec_from_file_location(module_name, theme_file)

            if not spec or not spec.loader:
                raise ThemeError(
                    f"Could not create module spec for theme file: {theme_file}",
                    theme_path=str(theme_file)
                )

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find and register theme classes
            themes_found = 0
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, Theme) and
                    attr not in (Theme, StandardTheme)):

                    try:
                        theme_instance = attr()
                        self._validate_theme_instance(theme_instance)
                        self.register_theme(theme_instance)
                        logger.info(f"Loaded third-party theme: {theme_instance.display_name}")
                        themes_found += 1
                    except Exception as e:
                        logger.warning(f"Failed to instantiate theme {attr_name}: {e}")

            if themes_found == 0:
                logger.warning(f"No valid theme classes found in {theme_file}")

        except ImportError as e:
            raise ThemeError(
                f"Import error while loading theme: {e}",
                theme_path=str(theme_file)
            )
        except Exception as e:
            raise ThemeError(
                f"Failed to load theme from {theme_file}: {e}",
                theme_path=str(theme_file)
            )

    def _validate_theme_file_security(self, theme_file: Path) -> bool:
        """Validate theme file for security concerns.

        Args:
            theme_file: Path to theme file

        Returns:
            True if file passes security validation
        """
        # Check file size (prevent loading huge files)
        if theme_file.stat().st_size > 1024 * 1024:  # 1MB limit
            logger.warning(f"Theme file too large: {theme_file}")
            return False

        # Check file extension
        if theme_file.suffix != ".py":
            logger.warning(f"Invalid theme file extension: {theme_file}")
            return False

        # Basic content validation (prevent obvious malicious code)
        try:
            content = theme_file.read_text(encoding="utf-8")

            # Check for suspicious imports/operations
            suspicious_patterns = [
                "import os",
                "import sys",
                "import subprocess",
                "exec(",
                "eval(",
                "__import__",
                "open(",
                "file(",
            ]

            for pattern in suspicious_patterns:
                if pattern in content:
                    logger.warning(f"Suspicious pattern '{pattern}' found in theme file: {theme_file}")
                    return False

            return True
        except Exception as e:
            logger.error(f"Error reading theme file for security validation: {e}")
            return False

    def _validate_theme_instance(self, theme: Theme) -> None:
        """Validate theme instance during registration.

        Args:
            theme: Theme instance to validate

        Raises:
            ThemeError: If theme validation fails
        """
        # Check required attributes
        required_attrs = ["name", "display_name", "generate_stylesheet"]
        for attr in required_attrs:
            if not hasattr(theme, attr):
                raise ThemeError(
                    f"Theme missing required attribute: {attr}",
                    theme_name=getattr(theme, "name", "unknown")
                )

        # Validate theme name
        if not theme.name or not isinstance(theme.name, str):
            raise ThemeError("Theme must have a valid string name")

        # Check for name conflicts during registration
        if theme.name in self._themes:
            raise ThemeError(
                f"Theme name conflict: {theme.name} already exists",
                theme_name=theme.name
            )

        # Validate stylesheet generation
        self._validate_theme_structure(theme, theme.name)

    def _validate_theme_structure(self, theme: Theme, theme_name: str) -> None:
        """Validate theme structure and functionality.

        Args:
            theme: Theme instance to validate
            theme_name: Theme name for error reporting

        Raises:
            ThemeError: If theme structure validation fails
        """
        # Check required attributes
        required_attrs = ["name", "display_name", "generate_stylesheet"]
        for attr in required_attrs:
            if not hasattr(theme, attr):
                raise ThemeError(
                    f"Theme missing required attribute: {attr}",
                    theme_name=theme_name
                )

        # Validate theme name
        if not theme.name or not isinstance(theme.name, str):
            raise ThemeError(
                f"Theme must have a valid string name",
                theme_name=theme_name
            )

        # Validate stylesheet generation
        try:
            stylesheet = theme.generate_stylesheet()
            if not isinstance(stylesheet, str):
                raise ThemeError(
                    f"Theme stylesheet must be a string, got {type(stylesheet)}",
                    theme_name=theme_name
                )
        except Exception as e:
            raise ThemeError(
                f"Failed to generate stylesheet for theme {theme_name}: {e}",
                theme_name=theme_name
            )

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

        Raises:
            ThemeError: If theme setting fails
        """
        if not isinstance(theme_name, str):
            raise ThemeError(
                f"Theme name must be a string, got {type(theme_name)}",
                theme_name=str(theme_name)
            )

        if not theme_name:
            raise ThemeError("Theme name cannot be empty")

        if theme_name not in self._themes:
            available_themes = ", ".join(self._themes.keys())
            raise ThemeError(
                f"Theme '{theme_name}' not found. Available themes: {available_themes}",
                theme_name=theme_name
            )

        try:
            # Get the theme (we already know it exists from the check above)
            theme = self._themes[theme_name]

            # Only validate theme structure, not conflicts (it's already registered)
            self._validate_theme_structure(theme, theme_name)

            old_theme = self._current_theme
            self._current_theme = theme_name
            self.theme_changed.emit(theme_name)
            logger.info(f"Theme changed from '{old_theme}' to '{theme_name}'")
            return True

        except Exception as e:
            raise ThemeError(
                f"Failed to set theme '{theme_name}': {e}",
                theme_name=theme_name
            )

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

