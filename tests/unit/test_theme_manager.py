"""Tests for ThemeManager."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

from qtframework.themes.theme import Theme
from qtframework.themes.theme_manager import ThemeManager
from qtframework.themes.tokens import DesignTokens


if TYPE_CHECKING:
    from pytest_qt.qtbot import QtBot


class TestThemeManagerCreation:
    """Test ThemeManager creation."""

    def test_theme_manager_creation_minimal(self) -> None:
        """Test creating theme manager with minimal parameters."""
        manager = ThemeManager()
        assert manager is not None

    def test_theme_manager_creation_with_themes_dir(self) -> None:
        """Test creating theme manager with custom themes directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            themes_dir = Path(tmpdir)
            manager = ThemeManager(themes_dir=themes_dir)
            assert manager is not None

    def test_theme_manager_creation_with_font_scale(self) -> None:
        """Test creating theme manager with custom font scale."""
        manager = ThemeManager(font_scale=150)
        assert manager is not None

    def test_theme_manager_loads_builtin_themes(self) -> None:
        """Test theme manager loads built-in themes."""
        manager = ThemeManager()
        themes = manager.list_themes()

        # Should have auto + built-in themes
        assert "auto" in themes
        assert "light" in themes
        assert "dark" in themes


class TestThemeManagerBuiltinThemes:
    """Test ThemeManager built-in theme loading."""

    def test_load_builtin_themes_success(self) -> None:
        """Test loading built-in themes."""
        manager = ThemeManager()

        # Light theme should be loaded
        light_theme = manager.get_theme("light")
        assert light_theme is not None
        assert light_theme.name == "light"

        # Dark theme should be loaded
        dark_theme = manager.get_theme("dark")
        assert dark_theme is not None
        assert dark_theme.name == "dark"

    def test_load_builtin_theme_error_handling(self) -> None:
        """Test error handling when loading built-in theme fails."""
        with patch("qtframework.themes.theme_manager.BUILTIN_THEMES") as mock_themes:
            # Make theme factory raise exception
            def failing_factory():
                raise ValueError("Theme creation failed")

            mock_themes.items.return_value = [("bad_theme", failing_factory)]

            manager = ThemeManager()
            # Should handle error gracefully
            assert "bad_theme" not in manager.list_themes()


class TestThemeManagerCustomThemes:
    """Test ThemeManager custom theme loading."""

    def test_load_custom_themes_directory_not_exists(self) -> None:
        """Test loading custom themes when directory doesn't exist."""
        nonexistent_dir = Path("/nonexistent/themes")
        manager = ThemeManager(themes_dir=nonexistent_dir)
        # Should handle gracefully
        assert manager is not None

    def test_load_theme_file_yaml(self) -> None:
        """Test loading theme from YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            themes_dir = Path(tmpdir)
            theme_file = themes_dir / "custom.yaml"

            # Create a minimal YAML theme file
            theme_data = """
name: custom
display_name: Custom Theme
description: A custom test theme
author: Test
version: 1.0.0
tokens:
  semantic:
    bg_primary: "#FFFFFF"
    fg_primary: "#000000"
    action_primary: "#0066CC"
"""
            theme_file.write_text(theme_data)

            manager = ThemeManager(themes_dir=themes_dir)

            # Custom theme should be loaded
            custom_theme = manager.get_theme("custom")
            assert custom_theme is not None
            assert custom_theme.name == "custom"

    def test_load_theme_file_non_yaml_extension(self) -> None:
        """Test that non-YAML files are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            themes_dir = Path(tmpdir)
            theme_file = themes_dir / "custom.json"
            theme_file.write_text('{"name": "custom"}')

            manager = ThemeManager(themes_dir=themes_dir)

            # JSON file should be skipped
            assert manager.get_theme("custom") is None

    def test_load_theme_file_name_conflict(self) -> None:
        """Test loading theme with name conflict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            themes_dir = Path(tmpdir)
            theme_file = themes_dir / "light.yaml"

            # Create theme with same name as built-in
            theme_data = """
name: light
display_name: Custom Light
description: A custom light theme
author: Test
version: 1.0.0
tokens:
  semantic:
    bg_primary: "#FFFFFF"
"""
            theme_file.write_text(theme_data)

            manager = ThemeManager(themes_dir=themes_dir)

            # Custom theme should override built-in theme
            light_theme = manager.get_theme("light")
            assert light_theme.display_name == "Custom Light"
            assert light_theme.description == "A custom light theme"

    def test_load_theme_file_invalid_yaml(self) -> None:
        """Test loading invalid YAML theme file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            themes_dir = Path(tmpdir)
            theme_file = themes_dir / "invalid.yaml"
            theme_file.write_text("invalid: yaml: content:")

            manager = ThemeManager(themes_dir=themes_dir)

            # Should handle error gracefully
            assert manager.get_theme("invalid") is None


class TestThemeManagerRegistration:
    """Test ThemeManager theme registration."""

    def test_register_theme_success(self) -> None:
        """Test registering a theme successfully."""
        manager = ThemeManager()
        theme = Theme(name="custom", display_name="Custom", tokens=DesignTokens())

        result = manager.register_theme(theme)
        assert result is True
        assert manager.get_theme("custom") is not None

    def test_register_theme_name_conflict(self) -> None:
        """Test registering theme with existing name."""
        manager = ThemeManager()
        theme = Theme(name="light", display_name="Custom Light", tokens=DesignTokens())

        # Default behavior: override existing theme
        result = manager.register_theme(theme)
        assert result is True
        assert manager.get_theme("light").display_name == "Custom Light"

        # With override=False: don't override
        theme2 = Theme(name="light", display_name="Another Light", tokens=DesignTokens())
        result = manager.register_theme(theme2, override=False)
        assert result is False
        assert (
            manager.get_theme("light").display_name == "Custom Light"
        )  # Still the first custom one

    def test_unregister_theme_success(self) -> None:
        """Test unregistering a theme successfully."""
        manager = ThemeManager()
        theme = Theme(name="custom", display_name="Custom", tokens=DesignTokens())
        manager.register_theme(theme)

        result = manager.unregister_theme("custom")
        assert result is True
        assert manager.get_theme("custom") is None

    def test_unregister_theme_not_found(self) -> None:
        """Test unregistering nonexistent theme."""
        manager = ThemeManager()

        result = manager.unregister_theme("nonexistent")
        assert result is False

    def test_unregister_current_theme_fails(self) -> None:
        """Test unregistering current theme fails."""
        manager = ThemeManager()
        manager.set_theme("light")

        result = manager.unregister_theme("light")
        assert result is False
        assert manager.get_theme("light") is not None


class TestThemeManagerGetTheme:
    """Test ThemeManager get_theme functionality."""

    def test_get_theme_by_name(self) -> None:
        """Test getting theme by name."""
        manager = ThemeManager()
        theme = manager.get_theme("light")
        assert theme is not None
        assert theme.name == "light"

    def test_get_theme_current(self) -> None:
        """Test getting current theme."""
        manager = ThemeManager()
        manager.set_theme("dark")
        theme = manager.get_theme()
        assert theme is not None
        assert theme.name == "dark"

    def test_get_theme_nonexistent(self) -> None:
        """Test getting nonexistent theme."""
        manager = ThemeManager()
        theme = manager.get_theme("nonexistent")
        assert theme is None

    def test_get_current_theme(self) -> None:
        """Test getting current theme."""
        manager = ThemeManager()
        manager.set_theme("dark")
        theme = manager.get_current_theme()
        assert theme is not None
        assert theme.name == "dark"

    def test_get_current_theme_fallback(self) -> None:
        """Test getting current theme with fallback."""
        manager = ThemeManager()
        manager._current_theme_name = "nonexistent"

        # Should fallback to light
        theme = manager.get_current_theme()
        assert theme is not None
        assert theme.name == "light"

    def test_get_current_theme_creates_default(self) -> None:
        """Test getting current theme creates default if missing."""
        manager = ThemeManager()
        manager._themes.clear()
        manager._current_theme_name = "light"

        # Should create default light theme
        theme = manager.get_current_theme()
        assert theme is not None
        assert theme.name == "light"


class TestThemeManagerSetTheme:
    """Test ThemeManager set_theme functionality."""

    def test_set_theme_success(self, qtbot: QtBot) -> None:
        """Test setting theme successfully."""
        manager = ThemeManager()

        with qtbot.waitSignal(manager.theme_changed, timeout=1000) as blocker:
            result = manager.set_theme("dark")

        assert result is True
        assert blocker.args[0] == "dark"
        assert manager._current_theme_name == "dark"

    def test_set_theme_not_found(self) -> None:
        """Test setting nonexistent theme."""
        manager = ThemeManager()

        result = manager.set_theme("nonexistent")
        assert result is False

    def test_set_theme_already_active(self) -> None:
        """Test setting already active theme."""
        manager = ThemeManager()
        manager.set_theme("dark")

        # Setting same theme again
        result = manager.set_theme("dark")
        assert result is True

    def test_set_theme_auto_detection(self, qtbot: QtBot) -> None:
        """Test setting theme to auto."""
        manager = ThemeManager()

        with (
            patch.object(manager, "detect_system_theme", return_value="dark"),
            qtbot.waitSignal(manager.theme_changed, timeout=1000) as blocker,
        ):
            result = manager.set_theme("auto")

        assert result is True
        # Signal should emit the actual theme, not 'auto'
        assert blocker.args[0] == "dark"
        assert manager._current_theme_name == "dark"
        assert manager._requested_theme_name == "auto"


class TestThemeManagerSystemTheme:
    """Test ThemeManager system theme detection."""

    def test_detect_system_theme_dark(self, qapp) -> None:
        """Test detecting dark system theme."""
        manager = ThemeManager()

        # Create a mock color object with low RGB values (dark)
        mock_color = Mock()
        mock_color.red.return_value = 30
        mock_color.green.return_value = 30
        mock_color.blue.return_value = 30

        # Patch the palette to return our mock color
        with patch.object(qapp, "palette") as mock_palette:
            mock_palette.return_value.color.return_value = mock_color

            result = manager.detect_system_theme()
            assert result == "dark"

    def test_detect_system_theme_light(self) -> None:
        """Test detecting light system theme."""
        manager = ThemeManager()

        # Mock the entire palette.color() call to return a light color
        mock_color = Mock()
        mock_color.red.return_value = 240
        mock_color.green.return_value = 240
        mock_color.blue.return_value = 240

        with patch("PySide6.QtWidgets.QApplication.instance") as mock_instance:
            mock_app = Mock()
            mock_palette = Mock()
            mock_palette.color.return_value = mock_color
            mock_app.palette.return_value = mock_palette
            mock_instance.return_value = mock_app

            result = manager.detect_system_theme()
            assert result == "light"


class TestThemeManagerStylesheet:
    """Test ThemeManager stylesheet generation."""

    def test_get_stylesheet_current(self) -> None:
        """Test getting stylesheet for current theme."""
        manager = ThemeManager()
        manager.set_theme("light")

        stylesheet = manager.get_stylesheet()
        assert isinstance(stylesheet, str)
        assert len(stylesheet) > 0

    def test_get_stylesheet_specific_theme(self) -> None:
        """Test getting stylesheet for specific theme."""
        manager = ThemeManager()

        stylesheet = manager.get_stylesheet("dark")
        assert isinstance(stylesheet, str)
        assert len(stylesheet) > 0

    def test_get_stylesheet_nonexistent(self) -> None:
        """Test getting stylesheet for nonexistent theme."""
        manager = ThemeManager()

        stylesheet = manager.get_stylesheet("nonexistent")
        assert stylesheet == ""

    def test_get_stylesheet_with_font_scale(self) -> None:
        """Test getting stylesheet with font scale."""
        manager = ThemeManager(font_scale=150)

        stylesheet = manager.get_stylesheet("light")
        assert isinstance(stylesheet, str)
        assert len(stylesheet) > 0

    def test_get_stylesheet_error_handling(self) -> None:
        """Test stylesheet generation error handling."""
        manager = ThemeManager()
        theme = manager.get_theme("light")

        with patch.object(theme._stylesheet_generator, "generate", side_effect=ValueError("Error")):
            stylesheet = manager.get_stylesheet("light")
            assert stylesheet == ""


class TestThemeManagerFontScale:
    """Test ThemeManager font scale functionality."""

    def test_set_font_scale(self) -> None:
        """Test setting font scale."""
        manager = ThemeManager()
        manager.set_font_scale(125)
        assert manager._font_scale == 125

    def test_set_font_scale_extremes(self) -> None:
        """Test setting font scale to extreme values."""
        manager = ThemeManager()

        manager.set_font_scale(50)
        assert manager._font_scale == 50

        manager.set_font_scale(200)
        assert manager._font_scale == 200


class TestThemeManagerListThemes:
    """Test ThemeManager list_themes functionality."""

    def test_list_themes(self) -> None:
        """Test listing all themes."""
        manager = ThemeManager()
        themes = manager.list_themes()

        assert isinstance(themes, list)
        assert "auto" in themes
        assert "light" in themes
        assert "dark" in themes

    def test_list_themes_auto_first(self) -> None:
        """Test that auto is first in the list."""
        manager = ThemeManager()
        themes = manager.list_themes()

        assert themes[0] == "auto"

    def test_list_themes_with_custom(self) -> None:
        """Test listing themes with custom theme."""
        manager = ThemeManager()
        theme = Theme(name="custom", display_name="Custom", tokens=DesignTokens())
        manager.register_theme(theme)

        themes = manager.list_themes()
        assert "custom" in themes


class TestThemeManagerThemeInfo:
    """Test ThemeManager get_theme_info functionality."""

    def test_get_theme_info_builtin(self) -> None:
        """Test getting info for built-in theme."""
        manager = ThemeManager()
        info = manager.get_theme_info("light")

        assert info is not None
        assert info["name"] == "light"
        assert "display_name" in info
        assert "description" in info
        assert "author" in info
        assert "version" in info

    def test_get_theme_info_auto(self) -> None:
        """Test getting info for auto theme."""
        manager = ThemeManager()
        info = manager.get_theme_info("auto")

        assert info is not None
        assert info["name"] == "auto"
        assert info["display_name"] == "Auto (System)"
        assert "system" in info["description"].lower()

    def test_get_theme_info_nonexistent(self) -> None:
        """Test getting info for nonexistent theme."""
        manager = ThemeManager()
        info = manager.get_theme_info("nonexistent")

        assert info is None


class TestThemeManagerExport:
    """Test ThemeManager export_theme functionality."""

    def test_export_theme_yaml(self) -> None:
        """Test exporting theme to YAML."""
        manager = ThemeManager()

        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = Path(tmpdir) / "exported.yaml"
            result = manager.export_theme("light", export_path, format="yaml")

            assert result is True
            assert export_path.exists()

    def test_export_theme_yml_extension(self) -> None:
        """Test exporting theme with yml format."""
        manager = ThemeManager()

        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = Path(tmpdir) / "exported.yml"
            result = manager.export_theme("light", export_path, format="yml")

            assert result is True
            assert export_path.exists()

    def test_export_theme_invalid_format(self) -> None:
        """Test exporting theme with invalid format."""
        manager = ThemeManager()

        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = Path(tmpdir) / "exported.json"
            result = manager.export_theme("light", export_path, format="json")

            assert result is False

    def test_export_theme_not_found(self) -> None:
        """Test exporting nonexistent theme."""
        manager = ThemeManager()

        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = Path(tmpdir) / "exported.yaml"
            result = manager.export_theme("nonexistent", export_path)

            assert result is False

    def test_export_theme_error_handling(self) -> None:
        """Test export error handling."""
        manager = ThemeManager()
        theme = manager.get_theme("light")

        with patch.object(theme, "save_yaml", side_effect=ValueError("Save error")):
            result = manager.export_theme("light", "test.yaml")
            assert result is False


class TestThemeManagerReload:
    """Test ThemeManager reload_themes functionality."""

    def test_reload_themes(self) -> None:
        """Test reloading themes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            themes_dir = Path(tmpdir)
            manager = ThemeManager(themes_dir=themes_dir)

            # Add custom theme
            theme = Theme(name="custom", display_name="Custom", tokens=DesignTokens())
            manager.register_theme(theme)

            assert manager.get_theme("custom") is not None

            # Reload themes
            manager.reload_themes()

            # Custom programmatic theme should be removed
            assert manager.get_theme("custom") is None

            # Built-in themes should still be there
            assert manager.get_theme("light") is not None

    def test_reload_themes_loads_new_files(self) -> None:
        """Test reload loads new theme files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            themes_dir = Path(tmpdir)
            manager = ThemeManager(themes_dir=themes_dir)

            # Create theme file after initialization
            theme_file = themes_dir / "new_theme.yaml"
            theme_data = """
name: new_theme
display_name: New Theme
description: A new theme
author: Test
version: 1.0.0
tokens:
  semantic:
    bg_primary: "#FFFFFF"
"""
            theme_file.write_text(theme_data)

            # Reload themes
            manager.reload_themes()

            # New theme should be loaded
            assert manager.get_theme("new_theme") is not None


class TestThemeManagerCreateTheme:
    """Test ThemeManager create_theme_from_colors functionality."""

    def test_create_theme_from_colors_light(self) -> None:
        """Test creating light theme from colors."""
        manager = ThemeManager()

        theme = manager.create_theme_from_colors(
            name="custom_light",
            primary_color="#0066CC",
            background_color="#FFFFFF",
            is_dark=False,
        )

        assert theme is not None
        assert theme.name == "custom_light"
        assert theme.tokens.semantic.bg_primary == "#FFFFFF"
        assert theme.tokens.semantic.action_primary == "#0066CC"
        assert theme.tokens.semantic.fg_primary == "#000000"

    def test_create_theme_from_colors_dark(self) -> None:
        """Test creating dark theme from colors."""
        manager = ThemeManager()

        theme = manager.create_theme_from_colors(
            name="custom_dark",
            primary_color="#66B2FF",
            background_color="#1E1E1E",
            is_dark=True,
        )

        assert theme is not None
        assert theme.name == "custom_dark"
        assert theme.tokens.semantic.bg_primary == "#1E1E1E"
        assert theme.tokens.semantic.action_primary == "#66B2FF"
        assert theme.tokens.semantic.fg_primary == "#FFFFFF"

    def test_create_theme_from_colors_with_metadata(self) -> None:
        """Test creating theme with metadata."""
        manager = ThemeManager()

        theme = manager.create_theme_from_colors(
            name="ocean",
            primary_color="#0077BE",
            background_color="#F0F8FF",
            is_dark=False,
            display_name="Ocean Theme",
            description="A calming ocean theme",
            author="Test Author",
            version="2.0.0",
        )

        assert theme.display_name == "Ocean Theme"
        assert theme.description == "A calming ocean theme"
        assert theme.author == "Test Author"
        assert theme.version == "2.0.0"


class TestThemeManagerIntegration:
    """Test ThemeManager integration scenarios."""

    def test_full_lifecycle(self, qtbot: QtBot) -> None:
        """Test full theme manager lifecycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            themes_dir = Path(tmpdir)
            manager = ThemeManager(themes_dir=themes_dir, font_scale=125)

            # List themes
            themes = manager.list_themes()
            assert len(themes) > 0

            # Set theme
            with qtbot.waitSignal(manager.theme_changed, timeout=1000):
                manager.set_theme("dark")

            # Get stylesheet
            stylesheet = manager.get_stylesheet()
            assert len(stylesheet) > 0

            # Create custom theme
            custom_theme = manager.create_theme_from_colors(
                name="test",
                primary_color="#FF0000",
                background_color="#FFFFFF",
                is_dark=False,
            )

            # Register theme
            assert manager.register_theme(custom_theme) is True

            # Export theme
            export_path = themes_dir / "test.yaml"
            result = manager.export_theme("test", export_path, format="yaml")
            assert result is True
            assert export_path.exists()

            # Unregister theme
            manager.set_theme("light")  # Switch away from test theme
            assert manager.unregister_theme("test") is True

    def test_auto_theme_workflow(self, qtbot: QtBot) -> None:
        """Test auto theme workflow."""
        manager = ThemeManager()

        with patch.object(manager, "detect_system_theme", return_value="dark"):
            with qtbot.waitSignal(manager.theme_changed, timeout=1000) as blocker:
                manager.set_theme("auto")

            # Should emit actual theme name
            assert blocker.args[0] == "dark"

            # Get info should work for auto
            info = manager.get_theme_info("auto")
            assert info is not None
            assert info["name"] == "auto"
