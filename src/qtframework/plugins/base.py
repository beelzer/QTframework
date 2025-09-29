"""Base plugin classes and interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, Signal


if TYPE_CHECKING:
    from collections.abc import Callable

    from qtframework.core.application import Application


class PluginState(Enum):
    """Plugin state enumeration."""

    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class PluginMetadata:
    """Plugin metadata information."""

    id: str
    name: str
    version: str
    description: str = ""
    author: str = ""
    website: str = ""
    dependencies: list[str] | None = None
    category: str = "general"
    icon: str = ""
    min_framework_version: str = "0.1.0"
    max_framework_version: str | None = None
    settings_schema: dict[str, Any] | None = None


class Plugin(QObject):
    """Abstract base class for plugins."""

    state_changed = Signal(str)
    error_occurred = Signal(str)
    message = Signal(str, str)  # level, message

    def __init__(self, metadata: PluginMetadata) -> None:
        """Initialize plugin.

        Args:
            metadata: Plugin metadata
        """
        super().__init__()
        self._metadata = metadata
        self._state = PluginState.UNLOADED
        self._app: Application | None = None
        self._settings: dict[str, Any] = {}
        self._hooks: dict[str, list[Callable]] = {}

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return self._metadata

    @property
    def id(self) -> str:
        """Get plugin ID."""
        return self._metadata.id

    @property
    def name(self) -> str:
        """Get plugin name."""
        return self._metadata.name

    @property
    def state(self) -> PluginState:
        """Get plugin state."""
        return self._state

    @property
    def application(self) -> Application | None:
        """Get application instance."""
        return self._app

    def set_application(self, app: Application) -> None:
        """Set application instance.

        Args:
            app: Application instance
        """
        self._app = app

    def set_state(self, state: PluginState) -> None:
        """Set plugin state.

        Args:
            state: New plugin state
        """
        if self._state != state:
            self._state = state
            self.state_changed.emit(state.value)

    def initialize(self) -> bool:
        """Initialize the plugin.

        Returns:
            True if initialization successful
        """
        return True

    def activate(self) -> bool:
        """Activate the plugin.

        Returns:
            True if activation successful
        """
        return True

    def deactivate(self) -> bool:
        """Deactivate the plugin.

        Returns:
            True if deactivation successful
        """
        return True

    def cleanup(self) -> None:
        """Clean up plugin resources."""

    def get_settings(self) -> dict[str, Any]:
        """Get plugin settings.

        Returns:
            Plugin settings dictionary
        """
        return self._settings.copy()

    def set_settings(self, settings: dict[str, Any]) -> None:
        """Set plugin settings.

        Args:
            settings: Settings dictionary
        """
        self._settings = settings
        self.on_settings_changed(settings)

    def on_settings_changed(self, settings: dict[str, Any]) -> None:
        """Handle settings change.

        Args:
            settings: New settings
        """

    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """Register a hook callback.

        Args:
            hook_name: Hook name
            callback: Callback function
        """
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(callback)

    def unregister_hook(self, hook_name: str, callback: Callable) -> None:
        """Unregister a hook callback.

        Args:
            hook_name: Hook name
            callback: Callback function
        """
        if hook_name in self._hooks and callback in self._hooks[hook_name]:
            self._hooks[hook_name].remove(callback)

    def trigger_hook(self, hook_name: str, *args: Any, **kwargs: Any) -> list[Any]:
        """Trigger a hook.

        Args:
            hook_name: Hook name
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            List of hook results
        """
        results = []
        if hook_name in self._hooks:
            for callback in self._hooks[hook_name]:
                try:
                    result = callback(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    self.error_occurred.emit(f"Hook error in {hook_name}: {e}")
        return results

    def log(self, message: str, level: str = "info") -> None:
        """Log a message.

        Args:
            message: Log message
            level: Log level (debug, info, warning, error)
        """
        self.message.emit(level, f"[{self.name}] {message}")
