"""Configuration file loading and I/O operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qtframework.utils.exceptions import ConfigurationError
from qtframework.utils.logger import get_logger


logger = get_logger(__name__)


class ConfigFileLoader:
    """Handles loading and saving configuration files in multiple formats."""

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def validate_file_security(self, path: Path) -> bool:
        """Validate configuration file for security concerns.

        Args:
            path: Configuration file path

        Returns:
            True if file passes security validation
        """
        try:
            # Check file size (prevent loading huge files)
            if path.stat().st_size > self.MAX_FILE_SIZE:
                logger.error("Configuration file too large: %s", path)
                return False

            # Check file permissions (basic check)
            if not path.is_file():
                logger.error("Path is not a file: %s", path)
                return False

            return True
        except Exception as e:
            logger.exception("Error validating config file security: %s", e)
            return False

    def load(self, path: Path, format: str) -> dict[str, Any]:
        """Load data from configuration file.

        Args:
            path: File path
            format: File format (json, yaml, yml, ini, env)

        Returns:
            Configuration data

        Raises:
            ConfigurationError: If file loading fails
        """
        try:
            if format == "json":
                return self._load_json(path)
            if format in {"yaml", "yml"}:
                return self._load_yaml(path)
            if format == "ini":
                return self._load_ini(path)
            if format == "env":
                return self._load_env(path)
            raise ConfigurationError(f"Unsupported format: {format}", source=str(path))

        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError(f"Error reading config file: {e}", source=str(path))

    def _load_json(self, path: Path) -> dict[str, Any]:
        """Load JSON configuration file."""
        import json

        try:
            with Path(path).open(encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON format in config file: {e}", source=str(path))

        if not isinstance(data, dict):
            raise ConfigurationError(
                f"Configuration file must contain a dictionary, got {type(data)}",
                source=str(path),
            )

        return data

    def _load_yaml(self, path: Path) -> dict[str, Any]:
        """Load YAML configuration file."""
        import yaml

        try:
            with Path(path).open(encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML format in config file: {e}", source=str(path))

        if not isinstance(data, dict):
            raise ConfigurationError(
                f"Configuration file must contain a dictionary, got {type(data)}",
                source=str(path),
            )

        return data

    def _load_ini(self, path: Path) -> dict[str, Any]:
        """Load INI configuration file."""
        import configparser

        parser = configparser.ConfigParser()
        parser.read(path)
        return {s: dict(parser.items(s)) for s in parser.sections()}

    def _load_env(self, path: Path) -> dict[str, Any]:
        """Load .env configuration file."""
        from dotenv import dotenv_values

        return dict(dotenv_values(path))

    def save(self, path: Path, data: dict[str, Any], format: str) -> bool:
        """Save configuration data to file.

        Args:
            path: File path
            data: Configuration data
            format: File format (json, yaml, yml)

        Returns:
            True if saved successfully
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)

            if format == "json":
                return self._save_json(path, data)
            if format in {"yaml", "yml"}:
                return self._save_yaml(path, data)
            logger.error("Unsupported save format: %s", format)
            return False

        except Exception as e:
            logger.exception("Failed to save config to %s: %s", path, e)
            return False

    def _save_json(self, path: Path, data: dict[str, Any]) -> bool:
        """Save configuration as JSON."""
        import json

        with Path(path).open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info("Saved config to: %s", path)
        return True

    def _save_yaml(self, path: Path, data: dict[str, Any]) -> bool:
        """Save configuration as YAML."""
        import yaml

        with Path(path).open("w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False)
        logger.info("Saved config to: %s", path)
        return True
