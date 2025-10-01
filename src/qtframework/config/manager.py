"""Configuration manager for handling multiple config sources."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from qtframework.config.config import Config
from qtframework.config.file_loader import ConfigFileLoader
from qtframework.config.migrator import ConfigMigrator
from qtframework.config.validator import ConfigValidator
from qtframework.utils.exceptions import ConfigurationError
from qtframework.utils.logger import get_logger
from qtframework.utils.paths import (
    ensure_directory,
    find_config_files,
    get_preferred_config_path,
    get_user_config_dir,
)


logger = get_logger(__name__)


class ConfigManager:
    """Manager for handling configuration from multiple sources.

    Orchestrates file loading, validation, and migration through specialized components.
    """

    def __init__(self) -> None:
        """Initialize config manager."""
        self._config = Config()
        self._sources: dict[str, Any] = {}
        self._source_metadata: dict[str, dict[str, Any]] = {}
        self._load_order: list[str] = []

        # Delegate to specialized components
        self._file_loader = ConfigFileLoader()
        self._validator = ConfigValidator()
        self._migrator = ConfigMigrator()

    @property
    def config(self) -> Config:
        """Get configuration object."""
        return self._config

    @property
    def validator(self) -> ConfigValidator:
        """Get the configuration validator."""
        return self._validator

    @property
    def migrator(self) -> ConfigMigrator:
        """Get the configuration migrator."""
        return self._migrator

    def load_file(self, path: Path | str, format: str = "auto", validate: bool = True) -> bool:
        """Load configuration from file.

        Args:
            path: File path
            format: File format (auto, json, yaml, ini, env)
            validate: Whether to validate configuration values

        Returns:
            True if loaded successfully

        Raises:
            ConfigurationError: If configuration loading or validation fails
        """
        path = Path(path)
        if not path.exists():
            logger.warning("Configuration file not found: %s", path)
            return False

        # Validate file security
        if not self._file_loader.validate_file_security(path):
            raise ConfigurationError(
                f"Configuration file failed security validation: {path}", source=str(path)
            )

        resolved_format = (
            format if format != "auto" else (path.suffix[1:] if path.suffix else "json")
        )

        try:
            data = self._file_loader.load(path, resolved_format)

            # Validate and migrate schema if needed
            data = self._migrator.validate_and_migrate(data, str(path))

            if validate:
                self._validator.validate(data, str(path))

            source_key = str(path)
            self._config.merge(data)
            self._sources[source_key] = data
            self._source_metadata[source_key] = {
                "type": "file",
                "label": path.name,
                "path": str(path),
                "format": resolved_format,
                "validate": validate,
            }
            if source_key not in self._load_order:
                self._load_order.append(source_key)
            logger.info("Loaded config from: %s", path)
            return True

        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError(f"Failed to load config from {path}: {e}", source=str(path))

    def _collect_env_data(self, prefix: str = "") -> dict[str, Any]:
        """Collect environment configuration values."""
        import json
        import os

        env_data: dict[str, Any] = {}
        for key, value in os.environ.items():
            if prefix and not key.startswith(prefix):
                continue

            config_key = key[len(prefix) :] if prefix else key
            config_key = config_key.lower().replace("_", ".")

            try:
                env_data[config_key] = json.loads(value)
            except Exception:
                env_data[config_key] = value

        return env_data

    def load_env(self, prefix: str = "") -> None:
        """Load configuration from environment variables.

        Args:
            prefix: Environment variable prefix
        """
        env_data = self._collect_env_data(prefix)
        source_key = "env" if not prefix else f"env:{prefix}"
        label = "env" if not prefix else f"env ({prefix})"

        if env_data:
            self._config.merge(env_data)
            self._sources[source_key] = env_data
            logger.info(f"Loaded {len(env_data)} values from environment")
        else:
            self._sources.pop(source_key, None)

        self._source_metadata[source_key] = {
            "type": "env",
            "label": label,
            "prefix": prefix,
        }
        if source_key not in self._load_order:
            self._load_order.append(source_key)

    def save(self, path: Path | str, format: str = "auto") -> bool:
        """Save configuration to file.

        Args:
            path: File path
            format: File format

        Returns:
            True if saved successfully
        """
        path = Path(path)
        resolved_format = (
            format if format != "auto" else (path.suffix[1:] if path.suffix else "json")
        )

        try:
            data = self._config.to_dict()

            # Ensure schema version is set when saving
            if "$schema_version" not in data:
                data["$schema_version"] = self._migrator.get_current_version()

            return self._file_loader.save(path, data, resolved_format)

        except Exception as e:
            logger.exception("Failed to save config to %s: %s", path, e)
            return False

    def reload(self) -> None:
        """Reload all configuration sources."""
        self._config.clear()

        for source in self._load_order:
            metadata = self._source_metadata.get(source, {})
            source_type = metadata.get("type")
            try:
                if source_type == "file":
                    path_str = metadata.get("path", source)
                    resolved_format = metadata.get("format", "json")
                    validate = metadata.get("validate", True)
                    config_path = Path(path_str)
                    if not config_path.exists():
                        logger.warning("Configuration source missing: %s", path_str)
                        continue
                    data = self._file_loader.load(config_path, resolved_format)
                    data = self._migrator.validate_and_migrate(data, path_str)
                    if validate:
                        self._validator.validate(data, path_str)
                    self._sources[source] = data
                    self._config.merge(data)
                elif source_type == "env":
                    prefix = metadata.get("prefix", "")
                    env_data = self._collect_env_data(prefix)
                    if env_data:
                        self._sources[source] = env_data
                        self._config.merge(env_data)
                    else:
                        self._sources.pop(source, None)
                else:
                    existing_data = self._sources.get(source)
                    if isinstance(existing_data, dict):
                        self._config.merge(existing_data)
            except ConfigurationError:
                raise
            except Exception as exc:
                logger.exception("Failed to reload configuration source %s: %s", source, exc)

        logger.info("Reloaded all configuration sources")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key
            default: Default value

        Returns:
            Configuration value
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            key: Configuration key
            value: Value to set
        """
        self._config.set(key, value)

    def get_all(self) -> dict[str, Any]:
        """Get all configuration values as a dictionary.

        Returns:
            Dictionary containing all configuration keys and values
        """
        return self._config.to_dict()

    def get_config(self, *, exclude_defaults: bool = False) -> dict[str, Any]:
        """Get configuration data."""
        data = self._config.to_dict()
        if exclude_defaults and "defaults" in self._sources:
            return self._filter_non_defaults(data, self._sources["defaults"])
        return data

    def get_sources(self) -> list[str]:
        """Get list of configuration sources."""
        sources: list[str] = []
        for source in self._load_order:
            metadata = self._source_metadata.get(source)
            if metadata:
                sources.append(metadata.get("label", source))
            else:
                sources.append(source)
        # Include any ad-hoc sources not present in load order
        sources.extend(source for source in self._sources if source not in self._load_order)
        return sources

    def load_defaults(self, defaults: dict[str, Any]) -> None:
        """Load default configuration values.

        Args:
            defaults: Default configuration dictionary
        """
        logger.info("Loading default configuration")

        # Ensure defaults have schema version
        if "$schema_version" not in defaults:
            defaults["$schema_version"] = self._migrator.get_current_version()

        # Process schema validation for defaults too
        defaults = self._migrator.validate_and_migrate(defaults, "defaults")

        defaults_copy = copy.deepcopy(defaults)
        self._config.merge(defaults_copy)
        self._sources["defaults"] = defaults_copy
        self._source_metadata["defaults"] = {"type": "defaults", "label": "defaults"}
        if "defaults" not in self._load_order:
            self._load_order.insert(0, "defaults")  # Defaults have lowest priority

    def load_standard_configs(
        self,
        app_name: str,
        config_filename: str = "config.json",
        defaults: dict[str, Any] | None = None,
    ) -> int:
        """Load configuration from standard locations with defaults.

        This method implements the standard config loading pattern:
        1. Load defaults (lowest priority)
        2. Load system config (if exists)
        3. Load user config (if exists)
        4. Load local config (highest priority)
        5. Load environment variables (highest priority)

        Args:
            app_name: Application name for directory discovery
            config_filename: Config file name (default: config.json)
            defaults: Default configuration values

        Returns:
            Number of config files loaded

        Example:
            >>> config_manager = ConfigManager()
            >>> defaults = {"theme": "light", "debug": False}
            >>> config_manager.load_standard_configs("MyApp", "settings.json", defaults)
            3  # Loaded defaults + user config + local config
        """
        loaded_count = 0

        # 1. Load defaults first (lowest priority)
        if defaults:
            self.load_defaults(defaults)
            loaded_count += 1

        # 2. Find and load standard config files (system -> user -> local)
        config_files = find_config_files(app_name, config_filename)
        for config_file in config_files:
            try:
                if self.load_file(config_file, validate=True):
                    loaded_count += 1
            except ConfigurationError as e:
                logger.warning("Failed to load config from %s: %s", config_file, e)

        # 3. Load environment variables (highest priority)
        env_prefix = f"{app_name.upper()}_"
        self.load_env(env_prefix)

        logger.info("Loaded configuration from %s sources for app '%s'", loaded_count, app_name)
        return loaded_count

    def save_user_config(
        self, app_name: str, config_filename: str = "config.json", exclude_defaults: bool = True
    ) -> bool:
        """Save current configuration to user config directory.

        Args:
            app_name: Application name for directory discovery
            config_filename: Config file name (default: config.json)
            exclude_defaults: Whether to exclude default values from saved config

        Returns:
            True if saved successfully
        """
        config_path = get_preferred_config_path(app_name, config_filename)

        # Ensure the config directory exists
        if not ensure_directory(config_path.parent):
            logger.error(f"Could not create config directory: {config_path.parent}")
            return False

        # Get data to save
        if exclude_defaults and "defaults" in self._sources:
            # Save only non-default values
            current_data = self._config.to_dict()
            defaults_data = self._sources["defaults"]
            filtered_data = self._filter_non_defaults(current_data, defaults_data)

            # Only save if there are actual overrides
            if not filtered_data:
                logger.info("No configuration overrides to save")
                return True

            # Temporarily create a config with filtered data for saving
            Config(filtered_data)

            # Save filtered data
            try:
                import json

                # Ensure schema version is included in saved config
                if "$schema_version" not in filtered_data:
                    filtered_data["$schema_version"] = self._migrator.get_current_version()
                with Path(config_path).open("w", encoding="utf-8") as f:
                    json.dump(filtered_data, f, indent=2)
                logger.info("Saved user config to: %s", config_path)
                return True
            except Exception as e:
                logger.exception("Failed to save user config to %s: %s", config_path, e)
                return False
        else:
            # Save all current config
            return self.save(config_path)

    def _filter_non_defaults(
        self, current: dict[str, Any], defaults: dict[str, Any]
    ) -> dict[str, Any]:
        """Filter out default values from current config.

        Args:
            current: Current configuration
            defaults: Default configuration

        Returns:
            Configuration with only non-default values
        """
        filtered = {}

        for key, value in current.items():
            if isinstance(value, dict) and key in defaults and isinstance(defaults[key], dict):
                # Recursively filter nested dictionaries
                nested_filtered = self._filter_non_defaults(value, defaults[key])
                if nested_filtered:
                    filtered[key] = nested_filtered
            elif key not in defaults or defaults[key] != value:
                # Include if key doesn't exist in defaults or value is different
                filtered[key] = value

        return filtered

    def reset_to_defaults(self) -> None:
        """Reset configuration to the loaded defaults."""
        if "defaults" not in self._sources:
            logger.warning("No default configuration loaded to reset to")
            return
        defaults_copy = copy.deepcopy(self._sources["defaults"])
        self._config.from_dict(defaults_copy)
        logger.info("Configuration reset to defaults")

    def get_config_info(
        self, app_name: str, config_filename: str = "config.json"
    ) -> dict[str, Any]:
        """Get information about config file locations for an application.

        Args:
            app_name: Application name
            config_filename: Config file name (default: config.json)

        Returns:
            Dictionary with config file information
        """
        from qtframework.utils.paths import (
            get_system_config_dir,
        )

        info = {
            "app_name": app_name,
            "config_filename": config_filename,
            "user_config_dir": str(get_user_config_dir(app_name)),
            "preferred_config_path": str(get_preferred_config_path(app_name, config_filename)),
            "existing_configs": [str(f) for f in find_config_files(app_name, config_filename)],
            "loaded_sources": self.get_sources(),
        }

        system_dir = get_system_config_dir(app_name)
        if system_dir:
            info["system_config_dir"] = str(system_dir)

        return info

    def get_schema_version(self) -> str:
        """Get the current schema version.

        Returns:
            Current schema version string
        """
        return self._migrator.get_current_version()

    def get_config_schema_version(self) -> str:
        """Get the schema version of the loaded configuration.

        Returns:
            Schema version from the configuration, or current version if not set
        """
        result = self.get("$schema_version", self._migrator.get_current_version())
        return str(result) if result is not None else self._migrator.get_current_version()

    def register_migration_handler(self, from_version: str, migration_func) -> None:
        """Register a custom migration handler for a specific version.

        Args:
            from_version: Source version to migrate from
            migration_func: Function that takes config dict and returns migrated dict

        Example:
            >>> def migrate_1_0_to_1_1(data):
            ...     data["new_field"] = "default_value"
            ...     return data
            >>> config_manager.register_migration_handler("1.0.0", migrate_1_0_to_1_1)
        """
        self._migrator.register_handler(from_version, migration_func)

    def get_supported_versions(self) -> list[str]:
        """Get list of supported configuration versions.

        Returns:
            List of version strings that can be migrated
        """
        return self._migrator.get_supported_versions()
