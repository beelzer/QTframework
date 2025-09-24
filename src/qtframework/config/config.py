"""Configuration storage and access."""

from __future__ import annotations

import copy
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel
from PySide6.QtCore import QObject, Signal

from qtframework.utils.logger import get_logger


logger = get_logger(__name__)


class Config(QObject):
    """Configuration container with dot notation access."""

    value_changed = Signal(str, object)
    config_reloaded = Signal()

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        """Initialize config.

        Args:
            data: Initial configuration data
        """
        super().__init__()
        self._data = data or {}
        self._watchers: dict[str, list[Callable]] = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Dot-separated key path
            default: Default value if not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self._data

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            key: Dot-separated key path
            value: Value to set
        """
        keys = key.split(".")
        data = self._data

        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]

        old_value = data.get(keys[-1])
        data[keys[-1]] = value

        if old_value != value:
            self.value_changed.emit(key, value)
            self._notify_watchers(key, value)

    def delete(self, key: str) -> bool:
        """Delete configuration value.

        Args:
            key: Dot-separated key path

        Returns:
            True if deleted
        """
        keys = key.split(".")
        data = self._data

        for k in keys[:-1]:
            if k not in data:
                return False
            data = data[k]

        if keys[-1] in data:
            del data[keys[-1]]
            self.value_changed.emit(key, None)
            self._notify_watchers(key, None)
            return True

        return False

    def has(self, key: str) -> bool:
        """Check if configuration key exists.

        Args:
            key: Dot-separated key path

        Returns:
            True if exists
        """
        return self.get(key, object()) is not object()

    def watch(self, key: str, callback: Callable[[Any], None]) -> Callable[[], None]:
        """Watch configuration value changes.

        Args:
            key: Key to watch
            callback: Callback function

        Returns:
            Unwatch function
        """
        if key not in self._watchers:
            self._watchers[key] = []

        self._watchers[key].append(callback)

        def unwatch() -> None:
            if key in self._watchers and callback in self._watchers[key]:
                self._watchers[key].remove(callback)

        return unwatch

    def _notify_watchers(self, key: str, value: Any) -> None:
        """Notify watchers of value change.

        Args:
            key: Changed key
            value: New value
        """
        # Direct watchers
        if key in self._watchers:
            for callback in self._watchers[key][:]:
                try:
                    callback(value)
                except Exception as e:
                    logger.error(f"Watcher error for {key}: {e}")

        # Parent watchers (watch entire sections)
        parts = key.split(".")
        for i in range(len(parts) - 1):
            parent_key = ".".join(parts[: i + 1])
            if parent_key in self._watchers:
                parent_value = self.get(parent_key)
                for callback in self._watchers[parent_key][:]:
                    try:
                        callback(parent_value)
                    except Exception as e:
                        logger.error(f"Parent watcher error for {parent_key}: {e}")

    def merge(self, data: dict[str, Any], deep: bool = True) -> None:
        """Merge configuration data.

        Args:
            data: Data to merge
            deep: Perform deep merge
        """
        if deep:
            self._data = self._deep_merge(self._data, data)
        else:
            self._data.update(data)

        self.config_reloaded.emit()

    def _deep_merge(self, base: dict, update: dict) -> dict:
        """Deep merge dictionaries.

        Args:
            base: Base dictionary
            update: Update dictionary

        Returns:
            Merged dictionary
        """
        result = copy.deepcopy(base)

        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)

        return result

    def to_dict(self) -> dict[str, Any]:
        """Get configuration as dictionary.

        Returns:
            Configuration dictionary
        """
        return copy.deepcopy(self._data)

    def from_dict(self, data: dict[str, Any]) -> None:
        """Load configuration from dictionary.

        Args:
            data: Configuration dictionary
        """
        self._data = copy.deepcopy(data)
        self.config_reloaded.emit()

    def clear(self) -> None:
        """Clear all configuration."""
        self._data.clear()
        self.config_reloaded.emit()

    def keys(self, prefix: str = "") -> list[str]:
        """Get all configuration keys.

        Args:
            prefix: Key prefix filter

        Returns:
            List of keys
        """

        def extract_keys(data: dict, parent: str = "") -> list[str]:
            keys = []
            for key, value in data.items():
                full_key = f"{parent}.{key}" if parent else key
                keys.append(full_key)

                if isinstance(value, dict):
                    keys.extend(extract_keys(value, full_key))

            return keys

        all_keys = extract_keys(self._data)

        if prefix:
            return [k for k in all_keys if k.startswith(prefix)]
        return all_keys

    def validate(self, schema: type[BaseModel]) -> bool:
        """Validate configuration against schema.

        Args:
            schema: Pydantic model schema

        Returns:
            True if valid
        """
        try:
            schema(**self._data)
            return True
        except Exception:
            return False

    def __getitem__(self, key: str) -> Any:
        """Get item by key.

        Args:
            key: Configuration key

        Returns:
            Configuration value
        """
        value = self.get(key)
        if value is None:
            raise KeyError(f"Configuration key not found: {key}")
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item by key.

        Args:
            key: Configuration key
            value: Value to set
        """
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        """Check if key exists.

        Args:
            key: Configuration key

        Returns:
            True if exists
        """
        return self.has(key)
