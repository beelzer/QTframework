"""Application context management."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Signal


class Context(QObject):
    """Application-wide context for sharing state."""

    value_changed = Signal(str, object)

    def __init__(self) -> None:
        """Initialize context."""
        super().__init__()
        self._data: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """Set a context value.

        Args:
            key: Context key
            value: Value to set
        """
        old_value = self._data.get(key)
        self._data[key] = value
        if old_value != value:
            self.value_changed.emit(key, value)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a context value.

        Args:
            key: Context key
            default: Default value if key not found

        Returns:
            Context value or default
        """
        return self._data.get(key, default)

    def remove(self, key: str) -> None:
        """Remove a context value.

        Args:
            key: Context key to remove
        """
        if key in self._data:
            del self._data[key]
            self.value_changed.emit(key, None)

    def clear(self) -> None:
        """Clear all context values."""
        self._data.clear()

    def keys(self) -> list[str]:
        """Get all context keys.

        Returns:
            List of context keys
        """
        return list(self._data.keys())

    def items(self) -> list[tuple[str, Any]]:
        """Get all context items.

        Returns:
            List of (key, value) tuples
        """
        return list(self._data.items())

    def update(self, data: dict[str, Any]) -> None:
        """Update multiple context values.

        Args:
            data: Dictionary of values to update
        """
        for key, value in data.items():
            self.set(key, value)
