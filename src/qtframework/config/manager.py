"""Configuration manager for handling multiple config sources."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from qtframework.config.config import Config
from qtframework.utils.exceptions import ConfigurationError
from qtframework.utils.logger import get_logger
from qtframework.utils.paths import (
    ensure_directory,
    find_config_files,
    get_preferred_config_path,
    get_user_config_dir,
)
from qtframework.utils.validation import ValidatorChain


logger = get_logger(__name__)


class ConfigManager:
    """Manager for handling configuration from multiple sources."""

    def __init__(self) -> None:
        """Initialize config manager."""
        self._config = Config()
        self._sources: dict[str, Any] = {}
        self._source_metadata: dict[str, dict[str, Any]] = {}
        self._load_order: list[str] = []
        self._validators: dict[str, ValidatorChain] = {}
        self._current_schema_version = "1.0.0"
        self._migration_handlers: dict[str, callable] = {}
        self._setup_default_validators()
        self._setup_schema_migrations()

    @property
    def config(self) -> Config:
        """Get configuration object."""
        return self._config

    def _setup_default_validators(self) -> None:
        """Setup default configuration validators."""
        from qtframework.utils.validation import (
            choice_field,
            number_field,
            optional_string,
            required_string,
        )

        # Application configuration validators
        self._validators.update({
            "app.name": required_string(min_length=1, max_length=100),
            "app.version": required_string(min_length=1, max_length=20),
            "app.debug": ValidatorChain(),  # Allow any boolean-like value
            # Database configuration
            "database.host": optional_string(max_length=255),
            "database.port": number_field(min_value=1, max_value=65535),
            "database.name": optional_string(max_length=100),
            # UI configuration
            "ui.theme": choice_field(["light", "dark", "monokai", "blue", "purple", "auto"]),
            "ui.language": optional_string(max_length=10),
            "ui.font_size": number_field(min_value=8, max_value=72),
            # Performance settings
            "performance.cache_size": number_field(min_value=0, max_value=1000),
            "performance.max_threads": number_field(min_value=1, max_value=64),
        })

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
            logger.warning(f"Configuration file not found: {path}")
            return False

        # Validate file security
        if not self._validate_config_file_security(path):
            raise ConfigurationError(
                f"Configuration file failed security validation: {path}", source=str(path)
            )

        resolved_format = format
        if format == "auto":
            resolved_format = path.suffix[1:] if path.suffix else "json"
        else:
            resolved_format = format

        try:
            data = self._load_file_data(path, resolved_format)

            # Validate and migrate schema if needed
            data = self._validate_schema_version(data, str(path))

            if validate:
                self._validate_config_data(data, str(path))

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
            logger.info(f"Loaded config from: {path}")
            return True

        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError(f"Failed to load config from {path}: {e}", source=str(path))

    def _validate_config_file_security(self, path: Path) -> bool:
        """Validate configuration file for security concerns.

        Args:
            path: Configuration file path

        Returns:
            True if file passes security validation
        """
        try:
            # Check file size (prevent loading huge files)
            if path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
                logger.error(f"Configuration file too large: {path}")
                return False

            # Check file permissions (basic check)
            if not path.is_file():
                logger.error(f"Path is not a file: {path}")
                return False

            return True
        except Exception as e:
            logger.error(f"Error validating config file security: {e}")
            return False

    def _load_file_data(self, path: Path, format: str) -> dict[str, Any]:
        """Load data from configuration file.

        Args:
            path: File path
            format: File format

        Returns:
            Configuration data

        Raises:
            ConfigurationError: If file loading fails
        """
        try:
            if format == "json":
                import json

                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
            elif format in ["yaml", "yml"]:
                import yaml

                with open(path, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            elif format == "ini":
                import configparser

                parser = configparser.ConfigParser()
                parser.read(path)
                data = {s: dict(parser.items(s)) for s in parser.sections()}
            elif format == "env":
                from dotenv import dotenv_values

                data = dict(dotenv_values(path))
            else:
                raise ConfigurationError(f"Unsupported format: {format}", source=str(path))

            if not isinstance(data, dict):
                raise ConfigurationError(
                    f"Configuration file must contain a dictionary, got {type(data)}",
                    source=str(path),
                )

            return data

        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ConfigurationError(
                f"Invalid {format.upper()} format in config file: {e}", source=str(path)
            )
        except Exception as e:
            raise ConfigurationError(f"Error reading config file: {e}", source=str(path))

    def _validate_config_data(self, data: dict[str, Any], source: str) -> None:
        """Validate configuration data.

        Args:
            data: Configuration data
            source: Data source identifier

        Raises:
            ConfigurationError: If validation fails
        """

        def validate_nested(obj: dict[str, Any], prefix: str = "") -> None:
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key

                if isinstance(value, dict):
                    validate_nested(value, full_key)
                # Validate individual values
                elif full_key in self._validators:
                    try:
                        result = self._validators[full_key].validate(value, full_key)
                        if not result.is_valid:
                            errors = "; ".join(result.get_error_messages())
                            raise ConfigurationError(
                                f"Validation failed for '{full_key}': {errors}",
                                config_key=full_key,
                                config_value=value,
                                source=source,
                            )
                    except Exception as e:
                        if isinstance(e, ConfigurationError):
                            raise
                        raise ConfigurationError(
                            f"Validation error for '{full_key}': {e}",
                            config_key=full_key,
                            config_value=value,
                            source=source,
                        )

        validate_nested(data)

    def _setup_schema_migrations(self) -> None:
        """Setup schema migration handlers for different versions."""

        # Example migration from 0.9.x to 1.0.0
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

    def _validate_schema_version(self, data: dict[str, Any], source: str) -> dict[str, Any]:
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
        if schema_version == self._current_schema_version:
            logger.debug(f"Config schema version {schema_version} is current for {source}")
            return data

        # Check if migration is possible
        if schema_version in self._migration_handlers:
            logger.info(
                f"Migrating config from schema version {schema_version} to {self._current_schema_version} for {source}"
            )
            try:
                migrated_data = self._migration_handlers[schema_version](data)
                migrated_data["$schema_version"] = self._current_schema_version
                return migrated_data
            except Exception as e:
                raise ConfigurationError(
                    f"Failed to migrate config schema from {schema_version} to {self._current_schema_version}: {e}",
                    source=source,
                )

        # Check if schema version is newer than supported
        if self._compare_versions(schema_version, self._current_schema_version) > 0:
            logger.warning(
                f"Config schema version {schema_version} is newer than supported {self._current_schema_version} for {source}"
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
            f"Unknown config schema version {schema_version} for {source}, proceeding without migration"
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
            logger.warning(f"Failed to parse version strings '{version1}' and '{version2}': {e}")
            return 0  # Treat as equal if parsing fails

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
        path.parent.mkdir(parents=True, exist_ok=True)

        if format == "auto":
            format = path.suffix[1:] if path.suffix else "json"

        try:
            data = self._config.to_dict()

            # Ensure schema version is set when saving
            if "$schema_version" not in data:
                data["$schema_version"] = self._current_schema_version

            if format == "json":
                import json

                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            elif format in ["yaml", "yml"]:
                import yaml

                with open(path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(data, f, default_flow_style=False)
            else:
                logger.error(f"Unsupported save format: {format}")
                return False

            logger.info(f"Saved config to: {path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save config to {path}: {e}")
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
                        logger.warning(f"Configuration source missing: {path_str}")
                        continue
                    data = self._load_file_data(config_path, resolved_format)
                    data = self._validate_schema_version(data, path_str)
                    if validate:
                        self._validate_config_data(data, path_str)
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
                    data = self._sources.get(source)
                    if data:
                        self._config.merge(data)
            except ConfigurationError:
                raise
            except Exception as exc:
                logger.error(f"Failed to reload configuration source {source}: {exc}")

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
        for source in self._sources.keys():
            if source not in self._load_order:
                sources.append(source)
        return sources

    def load_defaults(self, defaults: dict[str, Any]) -> None:
        """Load default configuration values.

        Args:
            defaults: Default configuration dictionary
        """
        logger.info("Loading default configuration")

        # Ensure defaults have schema version
        if "$schema_version" not in defaults:
            defaults["$schema_version"] = self._current_schema_version

        # Process schema validation for defaults too
        defaults = self._validate_schema_version(defaults, "defaults")

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
                logger.warning(f"Failed to load config from {config_file}: {e}")

        # 3. Load environment variables (highest priority)
        env_prefix = f"{app_name.upper()}_"
        self.load_env(env_prefix)

        logger.info(f"Loaded configuration from {loaded_count} sources for app '{app_name}'")
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
            temp_config = Config(filtered_data)

            # Save filtered data
            try:
                import json

                # Ensure schema version is included in saved config
                if "$schema_version" not in filtered_data:
                    filtered_data["$schema_version"] = self._current_schema_version
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(filtered_data, f, indent=2)
                logger.info(f"Saved user config to: {config_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to save user config to {config_path}: {e}")
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
        return self._current_schema_version

    def get_config_schema_version(self) -> str:
        """Get the schema version of the loaded configuration.

        Returns:
            Schema version from the configuration, or current version if not set
        """
        return self.get("$schema_version", self._current_schema_version)

    def register_migration_handler(self, from_version: str, migration_func: callable) -> None:
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
        self._migration_handlers[from_version] = migration_func
        logger.info(f"Registered migration handler for version {from_version}")

    def get_supported_versions(self) -> list[str]:
        """Get list of supported configuration versions.

        Returns:
            List of version strings that can be migrated
        """
        versions = [self._current_schema_version]
        versions.extend(self._migration_handlers.keys())
        return sorted(set(versions), key=lambda v: self._parse_version(v), reverse=True)

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
