"""Configuration schema migration and versioning."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qtframework.utils.exceptions import ConfigurationError
from qtframework.utils.logger import get_logger


if TYPE_CHECKING:
    from collections.abc import Callable


logger = get_logger(__name__)


class ConfigMigrator:
    """Handles configuration schema versioning and migrations."""

    def __init__(self, current_version: str = "1.0.0") -> None:
        """Initialize configuration migrator.

        Args:
            current_version: Current schema version
        """
        self._current_version = current_version
        self._migration_handlers: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {}
        self._setup_default_migrations()

    def _setup_default_migrations(self) -> None:
        """Setup default schema migration handlers."""

        def migrate_0_9_to_1_0(data: dict[str, Any]) -> dict[str, Any]:
            """Migrate config from version 0.9.x to 1.0.0."""
            # Example: rename old key names
            if "ui" in data and "colour" in data["ui"]:
                data["ui"]["theme"] = data["ui"].pop("colour")

            # Add new required fields with defaults
            if "performance" not in data:
                data["performance"] = {"cache_size": 100, "max_threads": 4, "lazy_loading": True}

            return data

        # Register migration handlers
        self._migration_handlers["0.9.0"] = migrate_0_9_to_1_0
        self._migration_handlers["0.9.1"] = migrate_0_9_to_1_0

    def register_handler(
        self, from_version: str, migration_func: Callable[[dict[str, Any]], dict[str, Any]]
    ) -> None:
        """Register a custom migration handler for a specific version.

        Args:
            from_version: Source version to migrate from
            migration_func: Function that takes config dict and returns migrated dict
        """
        self._migration_handlers[from_version] = migration_func
        logger.info("Registered migration handler for version %s", from_version)

    def validate_and_migrate(self, data: dict[str, Any], source: str) -> dict[str, Any]:
        """Validate and migrate config schema if needed.

        Args:
            data: Configuration data
            source: Data source identifier

        Returns:
            Migrated configuration data

        Raises:
            ConfigurationError: If schema validation fails
        """
        schema_version = data.get(
            "$schema_version", "0.9.0"
        )  # Default to old version if not specified

        # If schema version matches current, no migration needed
        if schema_version == self._current_version:
            logger.debug("Config schema version %s is current for %s", schema_version, source)
            return data

        # Check if migration is possible
        if schema_version in self._migration_handlers:
            logger.info(
                f"Migrating config from schema version {schema_version} to {self._current_version} for {source}"
            )
            try:
                migrated_data = self._migration_handlers[schema_version](data)
                migrated_data["$schema_version"] = self._current_version
                return migrated_data
            except Exception as e:
                raise ConfigurationError(
                    f"Failed to migrate config schema from {schema_version} to {self._current_version}: {e}",
                    source=source,
                )

        # Check if schema version is newer than supported
        if self._compare_versions(schema_version, self._current_version) > 0:
            logger.warning(
                f"Config schema version {schema_version} is newer than supported {self._current_version} for {source}"
            )
            # Allow loading but warn about potential compatibility issues
            return data

        # Check if schema version is too old and unsupported
        if self._compare_versions(schema_version, "0.8.0") < 0:
            raise ConfigurationError(
                f"Config schema version {schema_version} is too old and unsupported (minimum: 0.8.0)",
                source=source,
            )

        # If we get here, it's an unknown version - allow but warn
        logger.warning(
            "Unknown config schema version %s for %s, proceeding without migration",
            schema_version,
            source,
        )
        return data

    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two semantic version strings.

        Args:
            version1: First version string
            version2: Second version string

        Returns:
            -1 if version1 < version2, 0 if equal, 1 if version1 > version2
        """
        try:
            v1 = self._parse_version(version1)
            v2 = self._parse_version(version2)

            if v1 < v2:
                return -1
            if v1 > v2:
                return 1
            return 0
        except (ValueError, IndexError) as e:
            logger.warning(
                "Failed to parse version strings '%s' and '%s': %s", version1, version2, e
            )
            return 0  # Treat as equal if parsing fails

    def _parse_version(self, version: str) -> tuple[int, int, int]:
        """Parse a version string into tuple for comparison.

        Args:
            version: Version string to parse

        Returns:
            Tuple of (major, minor, patch) version numbers
        """
        try:
            parts = version.split(".")
            return (int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
        except (ValueError, IndexError):
            return (0, 0, 0)

    def get_current_version(self) -> str:
        """Get the current schema version.

        Returns:
            Current schema version string
        """
        return self._current_version

    def get_supported_versions(self) -> list[str]:
        """Get list of supported configuration versions.

        Returns:
            List of version strings that can be migrated
        """
        versions = [self._current_version]
        versions.extend(self._migration_handlers.keys())
        return sorted(set(versions), key=self._parse_version, reverse=True)
