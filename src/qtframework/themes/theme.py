"""Modern theme class using design tokens."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from qtframework.themes.stylesheet_generator import StylesheetGenerator
from qtframework.themes.tokens import DesignTokens


class Theme:
    """Modern theme class using design tokens."""

    def __init__(
        self,
        name: str,
        display_name: str,
        description: str = "",
        author: str = "",
        version: str = "1.0.0",
        tokens: DesignTokens | None = None,
        custom_styles: dict[str, str] | None = None,
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
        """
        self.name = name
        self.display_name = display_name
        self.description = description
        self.author = author
        self.version = version
        self.tokens = tokens or DesignTokens()
        self.custom_styles = custom_styles or {}
        self._stylesheet_generator = StylesheetGenerator()

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
        """
        path = Path(yaml_path)
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    def save_yaml(self, yaml_path: Path | str) -> None:
        """Save theme to YAML file.

        Args:
            yaml_path: Path to save YAML file
        """
        path = Path(yaml_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)

    def __repr__(self) -> str:
        """String representation."""
        return f"Theme(name='{self.name}', display_name='{self.display_name}')"
