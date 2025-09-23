"""Configuration manager for handling multiple config sources."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qtframework.config.config import Config
from qtframework.utils.logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """Manager for handling configuration from multiple sources."""

    def __init__(self) -> None:
        """Initialize config manager."""
        self._config = Config()
        self._sources: dict[str, Any] = {}
        self._load_order: list[str] = []

    @property
    def config(self) -> Config:
        """Get configuration object."""
        return self._config

    def load_file(self, path: Path | str, format: str = "auto") -> bool:
        """Load configuration from file.

        Args:
            path: File path
            format: File format (auto, json, yaml, ini, env)

        Returns:
            True if loaded successfully
        """
        path = Path(path)
        if not path.exists():
            logger.error(f"Config file not found: {path}")
            return False

        if format == "auto":
            format = path.suffix[1:] if path.suffix else "json"

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
                logger.error(f"Unsupported format: {format}")
                return False

            self._config.merge(data)
            self._sources[str(path)] = data
            self._load_order.append(str(path))
            logger.info(f"Loaded config from: {path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load config from {path}: {e}")
            return False

    def load_env(self, prefix: str = "") -> None:
        """Load configuration from environment variables.

        Args:
            prefix: Environment variable prefix
        """
        import os

        env_data = {}
        for key, value in os.environ.items():
            if prefix and not key.startswith(prefix):
                continue

            # Remove prefix and convert to lowercase
            config_key = key[len(prefix):] if prefix else key
            config_key = config_key.lower().replace("_", ".")

            # Try to parse value
            try:
                import json
                value = json.loads(value)
            except:
                pass  # Keep as string

            env_data[config_key] = value

        if env_data:
            self._config.merge(env_data)
            self._sources["env"] = env_data
            logger.info(f"Loaded {len(env_data)} values from environment")

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
            if source in self._sources:
                self._config.merge(self._sources[source])

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

    def get_sources(self) -> list[str]:
        """Get list of configuration sources.

        Returns:
            List of source identifiers
        """
        return list(self._sources.keys())