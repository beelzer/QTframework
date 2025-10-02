"""Tests for Theme class."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml

from qtframework.themes.theme import Theme
from qtframework.themes.tokens import DesignTokens


class TestThemeCreation:
    """Test Theme creation."""

    def test_theme_creation_minimal(self) -> None:
        """Test creating theme with minimal parameters."""
        theme = Theme(name="test", display_name="Test Theme")

        assert theme.name == "test"
        assert theme.display_name == "Test Theme"
        assert theme.description == ""
        assert theme.author == ""
        assert theme.version == "1.0.0"
        assert isinstance(theme.tokens, DesignTokens)
        assert theme.custom_styles == {}

    def test_theme_creation_full(self) -> None:
        """Test creating theme with all parameters."""
        tokens = DesignTokens()
        custom_styles = {"QWidget": "background: white;"}

        theme = Theme(
            name="custom",
            display_name="Custom Theme",
            description="A custom theme",
            author="Test Author",
            version="2.0.0",
            tokens=tokens,
            custom_styles=custom_styles,
        )

        assert theme.name == "custom"
        assert theme.display_name == "Custom Theme"
        assert theme.description == "A custom theme"
        assert theme.author == "Test Author"
        assert theme.version == "2.0.0"
        assert theme.tokens == tokens
        assert theme.custom_styles == custom_styles

    def test_theme_default_tokens(self) -> None:
        """Test theme creates default tokens if none provided."""
        theme = Theme(name="test", display_name="Test")

        assert isinstance(theme.tokens, DesignTokens)
        assert theme.tokens.primitive is not None


class TestThemeGetToken:
    """Test Theme get_token functionality."""

    def test_get_token_valid_path(self) -> None:
        """Test getting token with valid path."""
        theme = Theme(name="test", display_name="Test")

        token = theme.get_token("primitive.primary_500")
        assert token == "#2196F3"

    def test_get_token_invalid_path(self) -> None:
        """Test getting token with invalid path."""
        theme = Theme(name="test", display_name="Test")

        token = theme.get_token("nonexistent.path")
        assert token is None

    def test_get_token_typography(self) -> None:
        """Test getting typography token."""
        theme = Theme(name="test", display_name="Test")

        token = theme.get_token("typography.font_size_md")
        assert token == "14"

    def test_get_token_spacing(self) -> None:
        """Test getting spacing token."""
        theme = Theme(name="test", display_name="Test")

        token = theme.get_token("spacing.space_8")
        assert token == "16"


class TestThemeGenerateStylesheet:
    """Test Theme stylesheet generation."""

    def test_generate_stylesheet_returns_string(self) -> None:
        """Test generate_stylesheet returns a string."""
        theme = Theme(name="test", display_name="Test")

        stylesheet = theme.generate_stylesheet()
        assert isinstance(stylesheet, str)

    def test_generate_stylesheet_not_empty(self) -> None:
        """Test generate_stylesheet returns non-empty string."""
        theme = Theme(name="test", display_name="Test")

        stylesheet = theme.generate_stylesheet()
        assert len(stylesheet) > 0

    def test_generate_stylesheet_with_custom_styles(self) -> None:
        """Test generate_stylesheet includes custom styles."""
        custom_styles = {"QWidget": "background: blue;"}
        theme = Theme(
            name="test",
            display_name="Test",
            custom_styles=custom_styles,
        )

        stylesheet = theme.generate_stylesheet()
        assert isinstance(stylesheet, str)


class TestThemeToDict:
    """Test Theme to_dict functionality."""

    def test_to_dict_minimal(self) -> None:
        """Test to_dict with minimal theme."""
        theme = Theme(name="test", display_name="Test Theme")

        data = theme.to_dict()

        assert data["name"] == "test"
        assert data["display_name"] == "Test Theme"
        assert data["description"] == ""
        assert data["author"] == ""
        assert data["version"] == "1.0.0"
        assert "tokens" in data
        assert data["custom_styles"] == {}

    def test_to_dict_full(self) -> None:
        """Test to_dict with full theme."""
        custom_styles = {"QWidget": "color: red;"}
        theme = Theme(
            name="full",
            display_name="Full Theme",
            description="A full theme",
            author="Author",
            version="3.0.0",
            custom_styles=custom_styles,
        )

        data = theme.to_dict()

        assert data["name"] == "full"
        assert data["display_name"] == "Full Theme"
        assert data["description"] == "A full theme"
        assert data["author"] == "Author"
        assert data["version"] == "3.0.0"
        assert data["custom_styles"] == custom_styles

    def test_to_dict_includes_tokens(self) -> None:
        """Test to_dict includes token data."""
        theme = Theme(name="test", display_name="Test")

        data = theme.to_dict()

        assert "tokens" in data
        assert isinstance(data["tokens"], dict)
        assert "primitive" in data["tokens"]


class TestThemeFromDict:
    """Test Theme from_dict functionality."""

    def test_from_dict_minimal(self) -> None:
        """Test creating theme from minimal dict."""
        data = {
            "name": "test",
            "display_name": "Test Theme",
        }

        theme = Theme.from_dict(data)

        assert theme.name == "test"
        assert theme.display_name == "Test Theme"

    def test_from_dict_full(self) -> None:
        """Test creating theme from full dict."""
        data = {
            "name": "full",
            "display_name": "Full Theme",
            "description": "Description",
            "author": "Author",
            "version": "2.0.0",
            "tokens": {},
            "custom_styles": {"QWidget": "color: blue;"},
        }

        theme = Theme.from_dict(data)

        assert theme.name == "full"
        assert theme.display_name == "Full Theme"
        assert theme.description == "Description"
        assert theme.author == "Author"
        assert theme.version == "2.0.0"
        assert theme.custom_styles == {"QWidget": "color: blue;"}

    def test_from_dict_with_tokens(self) -> None:
        """Test creating theme with token data."""
        data = {
            "name": "test",
            "display_name": "Test",
            "tokens": {
                "primitive": {"primary_500": "#FF0000"},
            },
        }

        theme = Theme.from_dict(data)

        assert theme.tokens.primitive.primary_500 == "#FF0000"

    def test_from_dict_round_trip(self) -> None:
        """Test round-trip conversion to/from dict."""
        original = Theme(
            name="round_trip",
            display_name="Round Trip",
            description="Test",
            author="Author",
            version="1.5.0",
        )

        data = original.to_dict()
        recreated = Theme.from_dict(data)

        assert recreated.name == original.name
        assert recreated.display_name == original.display_name
        assert recreated.description == original.description
        assert recreated.author == original.author
        assert recreated.version == original.version


class TestThemeYaml:
    """Test Theme YAML functionality."""

    def test_save_yaml(self) -> None:
        """Test saving theme to YAML."""
        theme = Theme(
            name="yaml_test",
            display_name="YAML Test",
            description="Test theme",
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            path = Path(f.name)

        try:
            theme.save_yaml(path)
            assert path.exists()

            with path.open() as f:
                data = yaml.safe_load(f)

            assert data["name"] == "yaml_test"
            assert data["display_name"] == "YAML Test"
        finally:
            path.unlink()

    def test_from_yaml(self) -> None:
        """Test loading theme from YAML."""
        data = {
            "name": "yaml_theme",
            "display_name": "YAML Theme",
            "description": "Loaded from YAML",
            "author": "Test",
            "version": "1.0.0",
        }

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            yaml.safe_dump(data, f)
            path = Path(f.name)

        try:
            theme = Theme.from_yaml(path)

            assert theme.name == "yaml_theme"
            assert theme.display_name == "YAML Theme"
            assert theme.description == "Loaded from YAML"
            assert theme.author == "Test"
        finally:
            path.unlink()

    def test_from_yaml_nonexistent_file(self) -> None:
        """Test loading from nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            Theme.from_yaml("/nonexistent/file.yaml")

    def test_yaml_round_trip(self) -> None:
        """Test round-trip save and load YAML."""
        original = Theme(
            name="round_trip",
            display_name="Round Trip Theme",
            description="Test",
            author="Author",
            version="2.0.0",
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            path = Path(f.name)

        try:
            original.save_yaml(path)
            loaded = Theme.from_yaml(path)

            assert loaded.name == original.name
            assert loaded.display_name == original.display_name
            assert loaded.description == original.description
            assert loaded.author == original.author
            assert loaded.version == original.version
        finally:
            path.unlink()

    def test_save_yaml_creates_directories(self) -> None:
        """Test save_yaml creates parent directories."""
        theme = Theme(name="test", display_name="Test")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "dirs" / "theme.yaml"

            theme.save_yaml(path)

            assert path.exists()
            assert path.parent.exists()


class TestThemeRepr:
    """Test Theme string representation."""

    def test_repr(self) -> None:
        """Test theme repr."""
        theme = Theme(name="test", display_name="Test Theme")

        repr_str = repr(theme)

        assert "Theme" in repr_str
        assert "test" in repr_str
        assert "Test Theme" in repr_str

    def test_repr_includes_name_and_display_name(self) -> None:
        """Test repr includes both names."""
        theme = Theme(name="internal", display_name="Display")

        repr_str = repr(theme)

        assert "internal" in repr_str
        assert "Display" in repr_str


class TestThemeIntegration:
    """Test Theme integration scenarios."""

    def test_theme_with_custom_tokens(self) -> None:
        """Test theme with custom token values."""
        tokens = DesignTokens()
        tokens.primitive.primary_500 = "#FF0000"

        theme = Theme(
            name="custom_tokens",
            display_name="Custom Tokens",
            tokens=tokens,
        )

        assert theme.get_token("primitive.primary_500") == "#FF0000"

    def test_multiple_themes(self) -> None:
        """Test creating multiple themes."""
        theme1 = Theme(name="theme1", display_name="Theme 1")
        theme2 = Theme(name="theme2", display_name="Theme 2")

        assert theme1.name != theme2.name
        assert theme1.tokens is not theme2.tokens

    def test_theme_modification(self) -> None:
        """Test modifying theme attributes."""
        theme = Theme(name="test", display_name="Test")

        theme.description = "New description"
        theme.author = "New author"
        theme.version = "2.0.0"

        assert theme.description == "New description"
        assert theme.author == "New author"
        assert theme.version == "2.0.0"
