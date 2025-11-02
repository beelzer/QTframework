"""Modern theme class using design tokens.

This module defines the Theme class which represents a complete visual theme
for the application using a design token system.

Example:
    Create and use a theme from YAML::

        from qtframework.themes.theme import Theme
        from pathlib import Path

        # Define theme in YAML file (my_theme.yaml):
        # name: "custom"
        # display_name: "Custom Theme"
        # description: "A custom application theme"
        # author: "Your Name"
        # version: "1.0.0"
        # tokens:
        #   semantic:
        #     bg_primary: "#FFFFFF"
        #     fg_primary: "#000000"
        #     action_primary: "#007AFF"
        #     action_secondary: "#5856D6"
        #   spacing:
        #     xs: 4
        #     sm: 8
        #     md: 16
        #     lg: 24
        #   typography:
        #     font_family: "Segoe UI"
        #     font_size_base: 14

        # Load theme from YAML
        theme = Theme.from_yaml("my_theme.yaml")

        # Generate stylesheet
        stylesheet = theme.generate_stylesheet()
        app.setStyleSheet(stylesheet)

        # Access individual tokens
        primary_bg = theme.get_token("semantic.bg_primary")
        base_spacing = theme.get_token("spacing.md")

        # Export theme
        theme.save_yaml("exported_theme.yaml")

See Also:
    :class:`ThemeManager`: Manager for handling multiple themes
    :mod:`qtframework.themes.tokens`: Design token definitions
    :class:`StylesheetGenerator`: Generates Qt stylesheets from tokens
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from qtframework.themes.font_loader import FontLoader
from qtframework.themes.stylesheet_generator import StylesheetGenerator
from qtframework.themes.tokens import DesignTokens


if TYPE_CHECKING:
    from qtframework.utils.resources import ResourceManager


class Theme:
    """Modern theme class using design tokens.

    Represents a complete application theme with design tokens for colors,
    spacing, typography, and other visual properties. Themes can be loaded
    from YAML files or created programmatically.

    Attributes:
        name: Internal theme identifier
        display_name: Human-readable theme name
        description: Theme description
        author: Theme author
        version: Theme version string
        tokens: Design tokens defining the theme's visual properties
        custom_styles: Additional custom CSS-like rules
    """

    def __init__(
        self,
        name: str,
        display_name: str,
        description: str = "",
        author: str = "",
        version: str = "1.0.0",
        *,
        tokens: DesignTokens | None = None,
        custom_styles: dict[str, str] | None = None,
        resource_manager: ResourceManager | None = None,
    ) -> None:
        """Initialize theme.

        Args:
            name: Internal theme identifier
            display_name: Human-readable theme name
            description: Theme description
            author: Theme author
            version: Theme version
            tokens: Design tokens for the theme
            custom_styles: Additional custom CSS rules
            resource_manager: Optional resource manager for resolving resource paths
        """
        self.name = name
        self.display_name = display_name
        self.description = description
        self.author = author
        self.version = version
        self.tokens = tokens or DesignTokens()
        self.custom_styles = custom_styles or {}
        self._stylesheet_generator = StylesheetGenerator(resource_manager)

    def generate_stylesheet(self) -> str:
        """Generate Qt stylesheet from theme tokens.

        Returns:
            Complete Qt stylesheet string
        """
        return self._stylesheet_generator.generate(self.tokens, self.custom_styles)

    def get_token(self, token_path: str) -> str | None:
        """Get a token value by its path.

        Args:
            token_path: Dot-separated path to token

        Returns:
            Token value or None
        """
        return self.tokens.resolve_token(token_path)

    def to_dict(self) -> dict[str, Any]:
        """Export theme as dictionary.

        Returns:
            Theme configuration dictionary
        """
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "author": self.author,
            "version": self.version,
            "tokens": self.tokens.to_dict(),
            "custom_styles": self.custom_styles,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Theme:
        """Create theme from dictionary.

        Args:
            data: Theme configuration dictionary

        Returns:
            Theme instance
        """
        tokens = DesignTokens.from_dict(data.get("tokens", {}))

        # Resolve semantic color references
        tokens.resolve_semantic_colors()

        return cls(
            name=data["name"],
            display_name=data["display_name"],
            description=data.get("description", ""),
            author=data.get("author", ""),
            version=data.get("version", "1.0.0"),
            tokens=tokens,
            custom_styles=data.get("custom_styles", {}),
        )

    @classmethod
    def from_yaml(cls, yaml_path: Path | str) -> Theme:
        """Load theme from YAML file.

        Args:
            yaml_path: Path to YAML theme file

        Returns:
            Theme instance

        Raises:
            FileNotFoundError: If YAML file does not exist
            yaml.YAMLError: If YAML parsing fails
            KeyError: If required theme fields are missing
            ValueError: If theme data is invalid
        """
        path = Path(yaml_path)
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Create theme from YAML data
        theme = cls.from_dict(data)

        # Load custom fonts for this theme (if theme directory has fonts/)
        theme_dir = path.parent / path.stem
        cls._load_theme_fonts(theme_dir)

        return theme

    def save_yaml(self, yaml_path: Path | str) -> None:
        """Save theme to YAML file.

        Args:
            yaml_path: Path to save YAML file
        """
        path = Path(yaml_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)

    @staticmethod
    def _load_theme_fonts(theme_dir: Path) -> None:
        """Load custom fonts for a theme.

        Args:
            theme_dir: Path to the theme directory (e.g., pserver_manager/themes/runescape)
        """
        print(f"\n[Font Loader] Checking for fonts in: {theme_dir}")
        if not theme_dir.exists():
            print(f"   [Warning] Directory does not exist: {theme_dir}")
            return

        try:
            loaded_fonts = FontLoader.load_theme_fonts(theme_dir)
            if loaded_fonts:
                print(f"   [Success] Loaded {len(loaded_fonts)} custom fonts")
            else:
                print(f"   [Info] No custom fonts found")
        except Exception as e:
            print(f"   [Error] Font loading failed: {e}")

    def __repr__(self) -> str:
        """String representation."""
        return f"Theme(name='{self.name}', display_name='{self.display_name}')"
