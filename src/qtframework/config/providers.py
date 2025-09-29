"""Configuration providers for different sources."""

from __future__ import annotations

import pathlib
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
            with pathlib.Path(self.path).open(encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)
                return data
        except:
            return {}


class YamlProvider(FileProvider):
    """YAML configuration provider."""

    def load(self) -> dict[str, Any]:
        """Load from YAML."""
        try:
            import yaml

            with pathlib.Path(self.path).open(encoding="utf-8") as f:
                data: dict[str, Any] = yaml.safe_load(f) or {}
                return data
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
