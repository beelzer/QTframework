"""Configuration providers for different sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ConfigProvider(ABC):
    """Abstract configuration provider."""

    @abstractmethod
    def load(self) -> dict[str, Any]:
        """Load configuration data."""
        ...

    @abstractmethod
    def save(self, data: dict[str, Any]) -> bool:
        """Save configuration data."""
        ...


class FileProvider(ConfigProvider):
    """File-based configuration provider."""

    def __init__(self, path: str) -> None:
        """Initialize file provider."""
        self.path = path

    def load(self) -> dict[str, Any]:
        """Load from file."""
        return {}

    def save(self, data: dict[str, Any]) -> bool:
        """Save to file."""
        return True


class JsonProvider(FileProvider):
    """JSON configuration provider."""

    def load(self) -> dict[str, Any]:
        """Load from JSON."""
        import json

        try:
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}


class YamlProvider(FileProvider):
    """YAML configuration provider."""

    def load(self) -> dict[str, Any]:
        """Load from YAML."""
        try:
            import yaml

            with open(self.path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except:
            return {}


class EnvProvider(ConfigProvider):
    """Environment variable configuration provider."""

    def __init__(self, prefix: str = "") -> None:
        """Initialize env provider."""
        self.prefix = prefix

    def load(self) -> dict[str, Any]:
        """Load from environment."""
        import os

        data = {}
        for key, value in os.environ.items():
            if self.prefix and not key.startswith(self.prefix):
                continue
            data[key] = value
        return data

    def save(self, data: dict[str, Any]) -> bool:
        """Cannot save to environment."""
        return False
