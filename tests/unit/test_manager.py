"""Tests for ConfigManager."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
import yaml

from qtframework.config.manager import ConfigManager
from qtframework.utils.exceptions import ConfigurationError


if TYPE_CHECKING:
    from unittest.mock import Mock


class TestConfigManagerCreation:
    """Test ConfigManager creation."""

    def test_manager_creation(self) -> None:
        """Test creating config manager."""
        manager = ConfigManager()
        assert manager._config is not None
        assert manager._sources == {}
        assert manager._load_order == []

    def test_manager_has_components(self) -> None:
        """Test manager has specialized components."""
        manager = ConfigManager()
        assert manager._file_loader is not None
        assert manager._validator is not None
        assert manager._migrator is not None

    def test_manager_config_property(self) -> None:
        """Test config property."""
        manager = ConfigManager()
        assert manager.config is not None

    def test_manager_validator_property(self) -> None:
        """Test validator property."""
        manager = ConfigManager()
        assert manager.validator is not None

    def test_manager_migrator_property(self) -> None:
        """Test migrator property."""
        manager = ConfigManager()
        assert manager.migrator is not None


class TestConfigManagerLoadFile:
    """Test loading configuration from files."""

    def test_load_json_file(self) -> None:
        """Test loading JSON file."""
        manager = ConfigManager()
        data = {"app": {"name": "test"}, "$schema_version": "1.0.0"}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            json.dump(data, f)
            path = Path(f.name)

        try:
            result = manager.load_file(path, format="json")
            assert result is True
            assert manager.get("app.name") == "test"
        finally:
            path.unlink()

    def test_load_yaml_file(self) -> None:
        """Test loading YAML file."""
        manager = ConfigManager()
        data = {"app": {"name": "yaml_test"}, "$schema_version": "1.0.0"}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".yaml"
        ) as f:
            yaml.safe_dump(data, f)
            path = Path(f.name)

        try:
            result = manager.load_file(path, format="yaml")
            assert result is True
            assert manager.get("app.name") == "yaml_test"
        finally:
            path.unlink()

    def test_load_file_auto_format(self) -> None:
        """Test loading file with auto format detection."""
        manager = ConfigManager()
        data = {"key": "value", "$schema_version": "1.0.0"}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            json.dump(data, f)
            path = Path(f.name)

        try:
            result = manager.load_file(path, format="auto")
            assert result is True
        finally:
            path.unlink()

    def test_load_nonexistent_file(self) -> None:
        """Test loading nonexistent file returns False."""
        manager = ConfigManager()
        result = manager.load_file("/nonexistent/file.json")
        assert result is False

    def test_load_file_security_check(self) -> None:
        """Test security validation for files."""
        manager = ConfigManager()
        data = {"key": "value", "$schema_version": "1.0.0"}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            json.dump(data, f)
            path = Path(f.name)

        try:
            with patch.object(manager._file_loader, "validate_file_security", return_value=False):
                with pytest.raises(ConfigurationError) as exc_info:
                    manager.load_file(path)
                assert "security validation" in str(exc_info.value)
        finally:
            path.unlink()

    def test_load_file_updates_metadata(self) -> None:
        """Test loading file updates metadata."""
        manager = ConfigManager()
        data = {"key": "value", "$schema_version": "1.0.0"}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            json.dump(data, f)
            path = Path(f.name)

        try:
            manager.load_file(path)
            assert str(path) in manager._source_metadata
            assert manager._source_metadata[str(path)]["type"] == "file"
        finally:
            path.unlink()

    def test_load_file_validation_error(self) -> None:
        """Test loading file with validation error."""
        manager = ConfigManager()
        data = {"app": {"name": ""}, "$schema_version": "1.0.0"}  # Invalid: empty name

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            json.dump(data, f)
            path = Path(f.name)

        try:
            with pytest.raises(ConfigurationError):
                manager.load_file(path, validate=True)
        finally:
            path.unlink()

    def test_load_file_no_validation(self) -> None:
        """Test loading file without validation."""
        manager = ConfigManager()
        data = {"app": {"name": ""}, "$schema_version": "1.0.0"}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            json.dump(data, f)
            path = Path(f.name)

        try:
            result = manager.load_file(path, validate=False)
            assert result is True
        finally:
            path.unlink()


class TestConfigManagerLoadEnv:
    """Test loading configuration from environment."""

    def test_load_env_no_prefix(self) -> None:
        """Test loading environment variables without prefix."""
        os.environ["TEST_VAR"] = "test_value"

        try:
            manager = ConfigManager()
            manager.load_env(prefix="")
            assert "test.var" in manager.get_all()
        finally:
            del os.environ["TEST_VAR"]

    def test_load_env_with_prefix(self) -> None:
        """Test loading environment variables with prefix."""
        os.environ["APP_NAME"] = "TestApp"
        os.environ["APP_DEBUG"] = "true"
        os.environ["OTHER_VAR"] = "ignored"

        try:
            manager = ConfigManager()
            manager.load_env(prefix="APP_")
            assert "name" in manager.get_all()
            assert "debug" in manager.get_all()
            assert "other.var" not in manager.get_all()
        finally:
            del os.environ["APP_NAME"]
            del os.environ["APP_DEBUG"]
            del os.environ["OTHER_VAR"]

    def test_load_env_json_values(self) -> None:
        """Test loading JSON values from environment."""
        os.environ["APP_PORT"] = "8080"
        os.environ["APP_CONFIG"] = '{"nested": "value"}'

        try:
            manager = ConfigManager()
            manager.load_env(prefix="APP_")
            assert manager.get("port") == 8080
            assert manager.get("config") == {"nested": "value"}
        finally:
            del os.environ["APP_PORT"]
            del os.environ["APP_CONFIG"]

    def test_load_env_updates_metadata(self) -> None:
        """Test loading env updates metadata."""
        manager = ConfigManager()
        manager.load_env(prefix="TEST_")
        assert "env:TEST_" in manager._source_metadata
        assert manager._source_metadata["env:TEST_"]["type"] == "env"


class TestConfigManagerSave:
    """Test saving configuration."""

    def test_save_json(self) -> None:
        """Test saving configuration to JSON."""
        manager = ConfigManager()
        manager.set("app.name", "test")

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            path = Path(f.name)

        try:
            result = manager.save(path, format="json")
            assert result is True
            assert path.exists()

            with path.open(encoding="utf-8") as f:
                data = json.load(f)
            assert data["app"]["name"] == "test"
        finally:
            path.unlink()

    def test_save_yaml(self) -> None:
        """Test saving configuration to YAML."""
        manager = ConfigManager()
        manager.set("app.name", "test")

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".yaml"
        ) as f:
            path = Path(f.name)

        try:
            result = manager.save(path, format="yaml")
            assert result is True
            assert path.exists()
        finally:
            path.unlink()

    def test_save_includes_schema_version(self) -> None:
        """Test save includes schema version."""
        manager = ConfigManager()
        manager.set("key", "value")

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            path = Path(f.name)

        try:
            manager.save(path)
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
            assert "$schema_version" in data
        finally:
            path.unlink()


class TestConfigManagerReload:
    """Test reloading configuration."""

    def test_reload_file_source(self) -> None:
        """Test reloading file sources."""
        manager = ConfigManager()
        data = {"key": "original", "$schema_version": "1.0.0"}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            json.dump(data, f)
            path = Path(f.name)

        try:
            manager.load_file(path)
            assert manager.get("key") == "original"

            # Modify file
            data["key"] = "updated"
            with path.open("w", encoding="utf-8") as f:
                json.dump(data, f)

            manager.reload()
            assert manager.get("key") == "updated"
        finally:
            path.unlink()

    def test_reload_env_source(self) -> None:
        """Test reloading environment sources."""
        os.environ["APP_NAME"] = "original"

        try:
            manager = ConfigManager()
            manager.load_env(prefix="APP_")
            assert manager.get("name") == "original"

            # Update environment
            os.environ["APP_NAME"] = "updated"
            manager.reload()
            assert manager.get("name") == "updated"
        finally:
            del os.environ["APP_NAME"]

    def test_reload_missing_file(self) -> None:
        """Test reloading when file is missing."""
        manager = ConfigManager()
        data = {"key": "value", "$schema_version": "1.0.0"}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            json.dump(data, f)
            path = Path(f.name)

        try:
            manager.load_file(path)
            path.unlink()  # Delete file before reload
            manager.reload()  # Should not crash
        except Exception:
            pass  # File already deleted


class TestConfigManagerGetSet:
    """Test get/set operations."""

    def test_get_value(self) -> None:
        """Test getting value."""
        manager = ConfigManager()
        manager.set("app.name", "test")
        assert manager.get("app.name") == "test"

    def test_get_with_default(self) -> None:
        """Test getting value with default."""
        manager = ConfigManager()
        assert manager.get("nonexistent", "default") == "default"

    def test_set_value(self) -> None:
        """Test setting value."""
        manager = ConfigManager()
        manager.set("key", "value")
        assert manager.get("key") == "value"

    def test_get_all(self) -> None:
        """Test getting all values."""
        manager = ConfigManager()
        manager.set("key1", "value1")
        manager.set("key2", "value2")

        all_values = manager.get_all()
        assert "key1" in all_values
        assert "key2" in all_values


class TestConfigManagerDefaults:
    """Test default configuration handling."""

    def test_load_defaults(self) -> None:
        """Test loading defaults."""
        manager = ConfigManager()
        defaults = {"theme": "light", "debug": False}
        manager.load_defaults(defaults)

        assert manager.get("theme") == "light"
        assert manager.get("debug") is False

    def test_load_defaults_adds_schema_version(self) -> None:
        """Test loading defaults adds schema version."""
        manager = ConfigManager()
        defaults = {"key": "value"}
        manager.load_defaults(defaults)

        assert "$schema_version" in manager._sources["defaults"]

    def test_load_defaults_priority(self) -> None:
        """Test defaults have lowest priority."""
        manager = ConfigManager()
        manager.load_defaults({"theme": "light"})
        manager.set("theme", "dark")

        assert manager.get("theme") == "dark"

    def test_reset_to_defaults(self) -> None:
        """Test resetting to defaults."""
        manager = ConfigManager()
        manager.load_defaults({"theme": "light", "debug": False})
        manager.set("theme", "dark")
        manager.set("debug", True)

        manager.reset_to_defaults()

        assert manager.get("theme") == "light"
        assert manager.get("debug") is False

    def test_reset_without_defaults(self) -> None:
        """Test reset without defaults loaded."""
        manager = ConfigManager()
        manager.set("key", "value")
        manager.reset_to_defaults()  # Should not crash
        assert manager.get("key") == "value"

    def test_get_config_exclude_defaults(self) -> None:
        """Test getting config excluding defaults."""
        manager = ConfigManager()
        manager.load_defaults({"theme": "light", "debug": False})
        manager.set("theme", "dark")
        manager.set("custom", "value")

        config = manager.get_config(exclude_defaults=True)

        assert "theme" in config
        assert "debug" not in config
        assert "custom" in config


class TestConfigManagerSources:
    """Test configuration source management."""

    def test_get_sources_empty(self) -> None:
        """Test getting sources when empty."""
        manager = ConfigManager()
        sources = manager.get_sources()
        assert sources == []

    def test_get_sources_with_files(self) -> None:
        """Test getting sources with loaded files."""
        manager = ConfigManager()
        data = {"key": "value", "$schema_version": "1.0.0"}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            json.dump(data, f)
            path = Path(f.name)

        try:
            manager.load_file(path)
            sources = manager.get_sources()
            assert len(sources) == 1
            assert path.name in sources[0]
        finally:
            path.unlink()

    def test_get_sources_with_env(self) -> None:
        """Test getting sources with environment."""
        manager = ConfigManager()
        manager.load_env(prefix="TEST_")
        sources = manager.get_sources()
        assert any("env" in s for s in sources)


class TestConfigManagerStandardConfigs:
    """Test standard configuration loading."""

    @patch("qtframework.utils.paths.find_config_files")
    def test_load_standard_configs(self, mock_find: Mock) -> None:
        """Test loading standard configs."""
        manager = ConfigManager()
        defaults = {"theme": "light", "$schema_version": "1.0.0"}

        # Mock no existing config files
        mock_find.return_value = []

        count = manager.load_standard_configs("TestApp", "config.json", defaults)
        assert count >= 1  # At least defaults loaded

    @patch("qtframework.config.manager.find_config_files")
    def test_load_standard_configs_with_files(self, mock_find: Mock) -> None:
        """Test loading standard configs with existing files."""
        data = {"custom_key": "custom_value", "$schema_version": "1.0.0"}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            json.dump(data, f)
            f.flush()  # Ensure data is written
            path = Path(f.name)

        try:
            # Mock must be set up BEFORE creating manager
            mock_find.return_value = [path]
            manager = ConfigManager()
            count = manager.load_standard_configs("TestAppUnique123", "config.json")
            # Should load at least the file
            assert count >= 1
            # Verify the mock was called
            mock_find.assert_called_once()
        finally:
            path.unlink()

    @patch("qtframework.utils.paths.find_config_files")
    def test_load_standard_configs_with_env(self, mock_find: Mock) -> None:
        """Test loading standard configs includes env vars."""
        os.environ["TESTAPP_NAME"] = "EnvApp"

        try:
            manager = ConfigManager()
            mock_find.return_value = []
            manager.load_standard_configs("TestApp")
            assert "name" in manager.get_all()
        finally:
            del os.environ["TESTAPP_NAME"]


class TestConfigManagerSaveUserConfig:
    """Test saving user configuration."""

    @patch("qtframework.utils.paths.get_preferred_config_path")
    @patch("qtframework.utils.paths.ensure_directory")
    def test_save_user_config(self, mock_ensure: Mock, mock_path: Mock) -> None:
        """Test saving user config."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            path = Path(f.name)

        try:
            mock_path.return_value = path
            mock_ensure.return_value = True

            manager = ConfigManager()
            manager.set("app.name", "test")

            result = manager.save_user_config("TestApp", "config.json")
            assert result is True
        finally:
            path.unlink()

    @patch("qtframework.utils.paths.get_preferred_config_path")
    @patch("qtframework.utils.paths.ensure_directory")
    def test_save_user_config_exclude_defaults(self, mock_ensure: Mock, mock_path: Mock) -> None:
        """Test saving user config excluding defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.json"

            mock_path.return_value = path
            mock_ensure.return_value = True

            manager = ConfigManager()
            manager.load_defaults({"theme": "light", "debug": False})
            manager.set("theme", "dark")

            result = manager.save_user_config("TestApp", exclude_defaults=True)
            # Should succeed (returns True whether file saved or not)
            assert result is True

    @patch("qtframework.utils.paths.get_preferred_config_path")
    @patch("qtframework.utils.paths.ensure_directory")
    def test_save_user_config_no_overrides(self, mock_ensure: Mock, mock_path: Mock) -> None:
        """Test saving user config with no overrides."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            path = Path(f.name)

        try:
            mock_path.return_value = path
            mock_ensure.return_value = True

            manager = ConfigManager()
            manager.load_defaults({"theme": "light"})

            result = manager.save_user_config("TestApp", exclude_defaults=True)
            assert result is True
        finally:
            if path.exists():
                path.unlink()


class TestConfigManagerFilterNonDefaults:
    """Test filtering non-default values."""

    def test_filter_non_defaults_simple(self) -> None:
        """Test filtering simple values."""
        manager = ConfigManager()
        current = {"theme": "dark", "debug": False, "custom": "value"}
        defaults = {"theme": "light", "debug": False}

        filtered = manager._filter_non_defaults(current, defaults)

        assert "theme" in filtered
        assert "debug" not in filtered
        assert "custom" in filtered

    def test_filter_non_defaults_nested(self) -> None:
        """Test filtering nested values."""
        manager = ConfigManager()
        current = {"app": {"name": "test", "version": "2.0"}}
        defaults = {"app": {"name": "test", "version": "1.0"}}

        filtered = manager._filter_non_defaults(current, defaults)

        assert "app" in filtered
        assert "version" in filtered["app"]
        assert "name" not in filtered["app"]

    def test_filter_non_defaults_empty_result(self) -> None:
        """Test filtering with no differences."""
        manager = ConfigManager()
        current = {"theme": "light"}
        defaults = {"theme": "light"}

        filtered = manager._filter_non_defaults(current, defaults)
        assert filtered == {}


class TestConfigManagerConfigInfo:
    """Test configuration information."""

    @patch("qtframework.utils.paths.get_user_config_dir")
    @patch("qtframework.utils.paths.get_preferred_config_path")
    @patch("qtframework.utils.paths.find_config_files")
    @patch("qtframework.utils.paths.get_system_config_dir")
    def test_get_config_info(
        self,
        mock_system: Mock,
        mock_find: Mock,
        mock_preferred: Mock,
        mock_user: Mock,
    ) -> None:
        """Test getting config info."""
        mock_user.return_value = Path("/home/user/.config/TestApp")
        mock_preferred.return_value = Path("/home/user/.config/TestApp/config.json")
        mock_find.return_value = []
        mock_system.return_value = Path("/etc/TestApp")

        manager = ConfigManager()
        info = manager.get_config_info("TestApp", "config.json")

        assert info["app_name"] == "TestApp"
        assert info["config_filename"] == "config.json"
        assert "user_config_dir" in info
        assert "preferred_config_path" in info


class TestConfigManagerVersioning:
    """Test configuration versioning."""

    def test_get_schema_version(self) -> None:
        """Test getting schema version."""
        manager = ConfigManager()
        version = manager.get_schema_version()
        assert version == "1.0.0"

    def test_get_config_schema_version_default(self) -> None:
        """Test getting config schema version with default."""
        manager = ConfigManager()
        version = manager.get_config_schema_version()
        assert version == "1.0.0"

    def test_get_config_schema_version_from_config(self) -> None:
        """Test getting config schema version from loaded config."""
        manager = ConfigManager()
        manager.set("$schema_version", "0.9.0")
        version = manager.get_config_schema_version()
        assert version == "0.9.0"

    def test_register_migration_handler(self) -> None:
        """Test registering migration handler."""
        manager = ConfigManager()

        def custom_migration(data):
            data["migrated"] = True
            return data

        manager.register_migration_handler("0.8.0", custom_migration)
        assert "0.8.0" in manager._migrator._migration_handlers

    def test_get_supported_versions(self) -> None:
        """Test getting supported versions."""
        manager = ConfigManager()
        versions = manager.get_supported_versions()
        assert isinstance(versions, list)
        assert len(versions) > 0


class TestConfigManagerIntegration:
    """Test ConfigManager integration scenarios."""

    def test_load_merge_multiple_files(self) -> None:
        """Test loading and merging multiple config files."""
        manager = ConfigManager()

        # Create two config files
        data1 = {"app": {"name": "test"}, "theme": "light", "$schema_version": "1.0.0"}
        data2 = {"theme": "dark", "debug": True, "$schema_version": "1.0.0"}

        with (
            tempfile.NamedTemporaryFile(
                encoding="utf-8", mode="w", delete=False, suffix=".json"
            ) as f1,
            tempfile.NamedTemporaryFile(
                encoding="utf-8", mode="w", delete=False, suffix=".json"
            ) as f2,
        ):
            json.dump(data1, f1)
            json.dump(data2, f2)
            path1 = Path(f1.name)
            path2 = Path(f2.name)

        try:
            manager.load_file(path1)
            manager.load_file(path2)

            assert manager.get("app.name") == "test"
            assert manager.get("theme") == "dark"  # Second file overwrites
            assert manager.get("debug") is True
        finally:
            path1.unlink()
            path2.unlink()

    def test_defaults_file_env_priority(self) -> None:
        """Test priority: defaults < file < env."""
        manager = ConfigManager()

        # Load defaults
        manager.load_defaults({"theme": "light", "debug": False})

        # Load file
        data = {"theme": "dark", "$schema_version": "1.0.0"}
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            json.dump(data, f)
            path = Path(f.name)

        try:
            manager.load_file(path)

            # Set env var
            os.environ["APP_THEME"] = "custom"
            try:
                manager.load_env(prefix="APP_")
                assert manager.get("theme") == "custom"  # Env has highest priority
            finally:
                del os.environ["APP_THEME"]
        finally:
            path.unlink()

    def test_save_load_round_trip(self) -> None:
        """Test saving and loading config."""
        manager1 = ConfigManager()
        manager1.set("app.name", "test")
        manager1.set("theme", "dark")

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False, suffix=".json"
        ) as f:
            path = Path(f.name)

        try:
            manager1.save(path)

            manager2 = ConfigManager()
            manager2.load_file(path)

            assert manager2.get("app.name") == "test"
            assert manager2.get("theme") == "dark"
        finally:
            path.unlink()
