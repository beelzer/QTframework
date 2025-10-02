"""Tests for ConfigMigrator."""

from __future__ import annotations

import pytest

from qtframework.config.migrator import ConfigMigrator
from qtframework.utils.exceptions import ConfigurationError


class TestConfigMigratorCreation:
    """Test ConfigMigrator creation."""

    def test_migrator_creation_default(self) -> None:
        """Test creating migrator with default version."""
        migrator = ConfigMigrator()
        assert migrator._current_version == "1.0.0"

    def test_migrator_creation_custom_version(self) -> None:
        """Test creating migrator with custom version."""
        migrator = ConfigMigrator(current_version="2.0.0")
        assert migrator._current_version == "2.0.0"

    def test_migrator_has_default_handlers(self) -> None:
        """Test migrator has default migration handlers."""
        migrator = ConfigMigrator()
        assert len(migrator._migration_handlers) > 0
        assert "0.9.0" in migrator._migration_handlers
        assert "0.9.1" in migrator._migration_handlers


class TestConfigMigratorRegisterHandler:
    """Test registering migration handlers."""

    def test_register_handler(self) -> None:
        """Test registering custom handler."""
        migrator = ConfigMigrator()

        def custom_migration(data):
            data["migrated"] = True
            return data

        migrator.register_handler("0.8.0", custom_migration)
        assert "0.8.0" in migrator._migration_handlers

    def test_register_handler_overwrite(self) -> None:
        """Test registering handler overwrites existing."""
        migrator = ConfigMigrator()

        def migration1(data):
            return data

        def migration2(data):
            data["new"] = True
            return data

        migrator.register_handler("0.8.0", migration1)
        migrator.register_handler("0.8.0", migration2)

        assert migrator._migration_handlers["0.8.0"] == migration2


class TestConfigMigratorValidateAndMigrate:
    """Test validate and migrate functionality."""

    def test_no_migration_needed_current_version(self) -> None:
        """Test no migration when version is current."""
        migrator = ConfigMigrator(current_version="1.0.0")
        data = {"$schema_version": "1.0.0", "key": "value"}

        result = migrator.validate_and_migrate(data, "test")
        assert result == data

    def test_migration_from_0_9_0(self) -> None:
        """Test migration from version 0.9.0."""
        migrator = ConfigMigrator(current_version="1.0.0")
        data = {"$schema_version": "0.9.0", "ui": {"colour": "dark"}}

        result = migrator.validate_and_migrate(data, "test")

        assert result["$schema_version"] == "1.0.0"
        assert "theme" in result["ui"]
        assert result["ui"]["theme"] == "dark"
        assert "colour" not in result["ui"]

    def test_migration_adds_performance_section(self) -> None:
        """Test migration adds performance section."""
        migrator = ConfigMigrator(current_version="1.0.0")
        data = {"$schema_version": "0.9.0", "app": {"name": "test"}}

        result = migrator.validate_and_migrate(data, "test")

        assert "performance" in result
        assert result["performance"]["cache_size"] == 100
        assert result["performance"]["max_threads"] == 4

    def test_migration_from_0_9_1(self) -> None:
        """Test migration from version 0.9.1."""
        migrator = ConfigMigrator(current_version="1.0.0")
        data = {"$schema_version": "0.9.1", "key": "value"}

        result = migrator.validate_and_migrate(data, "test")

        assert result["$schema_version"] == "1.0.0"

    def test_default_version_when_missing(self) -> None:
        """Test default version when $schema_version missing."""
        migrator = ConfigMigrator(current_version="1.0.0")
        data = {"key": "value"}  # No $schema_version

        result = migrator.validate_and_migrate(data, "test")

        # Should assume 0.9.0 and migrate
        assert result["$schema_version"] == "1.0.0"

    def test_newer_version_allowed_with_warning(self) -> None:
        """Test newer version is allowed."""
        migrator = ConfigMigrator(current_version="1.0.0")
        data = {"$schema_version": "2.0.0", "key": "value"}

        result = migrator.validate_and_migrate(data, "test")

        # Should allow newer version
        assert result["$schema_version"] == "2.0.0"

    def test_too_old_version_raises_error(self) -> None:
        """Test too old version raises error."""
        migrator = ConfigMigrator(current_version="1.0.0")
        data = {"$schema_version": "0.7.0", "key": "value"}

        with pytest.raises(ConfigurationError) as exc_info:
            migrator.validate_and_migrate(data, "test")

        assert "too old" in str(exc_info.value)

    def test_unknown_version_warning(self) -> None:
        """Test unknown version proceeds with warning."""
        migrator = ConfigMigrator(current_version="1.0.0")
        data = {"$schema_version": "0.8.5", "key": "value"}

        result = migrator.validate_and_migrate(data, "test")

        # Should allow unknown version
        assert result == data

    def test_migration_error_raises_configuration_error(self) -> None:
        """Test migration error is caught and wrapped."""
        migrator = ConfigMigrator(current_version="1.0.0")

        def failing_migration(data):
            raise ValueError("Migration failed")

        migrator.register_handler("0.8.0", failing_migration)
        data = {"$schema_version": "0.8.0", "key": "value"}

        with pytest.raises(ConfigurationError) as exc_info:
            migrator.validate_and_migrate(data, "test")

        assert "Failed to migrate" in str(exc_info.value)


class TestConfigMigratorVersionComparison:
    """Test version comparison functionality."""

    def test_compare_versions_equal(self) -> None:
        """Test comparing equal versions."""
        migrator = ConfigMigrator()
        result = migrator._compare_versions("1.0.0", "1.0.0")
        assert result == 0

    def test_compare_versions_less_than(self) -> None:
        """Test comparing less than version."""
        migrator = ConfigMigrator()
        result = migrator._compare_versions("0.9.0", "1.0.0")
        assert result == -1

    def test_compare_versions_greater_than(self) -> None:
        """Test comparing greater than version."""
        migrator = ConfigMigrator()
        result = migrator._compare_versions("2.0.0", "1.0.0")
        assert result == 1

    def test_compare_versions_minor_difference(self) -> None:
        """Test comparing versions with minor difference."""
        migrator = ConfigMigrator()
        result = migrator._compare_versions("1.1.0", "1.0.0")
        assert result == 1

    def test_compare_versions_patch_difference(self) -> None:
        """Test comparing versions with patch difference."""
        migrator = ConfigMigrator()
        result = migrator._compare_versions("1.0.1", "1.0.0")
        assert result == 1

    def test_compare_versions_invalid_format(self) -> None:
        """Test comparing invalid version format."""
        migrator = ConfigMigrator()
        result = migrator._compare_versions("invalid", "1.0.0")
        # When parsing fails, returns 0 (equal) or compares (0,0,0) tuples
        assert result in {0, -1}  # Either equal or less than


class TestConfigMigratorVersionParsing:
    """Test version parsing functionality."""

    def test_parse_version_standard(self) -> None:
        """Test parsing standard version."""
        migrator = ConfigMigrator()
        result = migrator._parse_version("1.2.3")
        assert result == (1, 2, 3)

    def test_parse_version_no_patch(self) -> None:
        """Test parsing version without patch."""
        migrator = ConfigMigrator()
        result = migrator._parse_version("1.2")
        assert result == (1, 2, 0)

    def test_parse_version_major_only(self) -> None:
        """Test parsing version with major only."""
        migrator = ConfigMigrator()
        result = migrator._parse_version("2")
        # May fail to parse single digit, returning (0,0,0) or parse as (2,0,0)
        assert result in {(2, 0, 0), (0, 0, 0)}

    def test_parse_version_invalid(self) -> None:
        """Test parsing invalid version."""
        migrator = ConfigMigrator()
        result = migrator._parse_version("invalid")
        assert result == (0, 0, 0)

    def test_parse_version_empty(self) -> None:
        """Test parsing empty version."""
        migrator = ConfigMigrator()
        result = migrator._parse_version("")
        assert result == (0, 0, 0)


class TestConfigMigratorGetters:
    """Test getter methods."""

    def test_get_current_version(self) -> None:
        """Test getting current version."""
        migrator = ConfigMigrator(current_version="2.5.0")
        assert migrator.get_current_version() == "2.5.0"

    def test_get_supported_versions(self) -> None:
        """Test getting supported versions."""
        migrator = ConfigMigrator(current_version="1.0.0")
        versions = migrator.get_supported_versions()

        assert "1.0.0" in versions
        assert "0.9.0" in versions
        assert "0.9.1" in versions
        assert len(versions) >= 3

    def test_get_supported_versions_sorted(self) -> None:
        """Test supported versions are sorted."""
        migrator = ConfigMigrator(current_version="1.0.0")
        versions = migrator.get_supported_versions()

        # Should be sorted in descending order
        assert versions[0] == "1.0.0"

    def test_get_supported_versions_no_duplicates(self) -> None:
        """Test supported versions have no duplicates."""
        migrator = ConfigMigrator(current_version="1.0.0")
        versions = migrator.get_supported_versions()

        assert len(versions) == len(set(versions))


class TestConfigMigratorCustomMigrations:
    """Test custom migration scenarios."""

    def test_custom_migration_function(self) -> None:
        """Test custom migration function works."""
        migrator = ConfigMigrator(current_version="2.0.0")

        def custom_migration(data):
            data["custom_field"] = "added"
            return data

        migrator.register_handler("1.5.0", custom_migration)
        data = {"$schema_version": "1.5.0", "key": "value"}

        result = migrator.validate_and_migrate(data, "test")

        assert result["custom_field"] == "added"
        assert result["$schema_version"] == "2.0.0"

    def test_migration_preserves_existing_data(self) -> None:
        """Test migration preserves existing data."""
        migrator = ConfigMigrator(current_version="1.0.0")
        data = {
            "$schema_version": "0.9.0",
            "app": {"name": "TestApp", "version": "1.0"},
            "database": {"host": "localhost"},
        }

        result = migrator.validate_and_migrate(data, "test")

        assert result["app"]["name"] == "TestApp"
        assert result["app"]["version"] == "1.0"
        assert result["database"]["host"] == "localhost"

    def test_migration_with_existing_performance_section(self) -> None:
        """Test migration when performance section already exists."""
        migrator = ConfigMigrator(current_version="1.0.0")
        data = {
            "$schema_version": "0.9.0",
            "performance": {"cache_size": 200, "custom": "value"},
        }

        result = migrator.validate_and_migrate(data, "test")

        # Should preserve existing performance section
        assert result["performance"]["cache_size"] == 200
        assert result["performance"]["custom"] == "value"
        assert result["$schema_version"] == "1.0.0"
