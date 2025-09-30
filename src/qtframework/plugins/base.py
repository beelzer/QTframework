"""Base plugin classes and interfaces.

This module defines the base plugin system for extending Qt Framework applications.
Plugins can add new features, modify behavior, and integrate with the application
lifecycle.

Example:
    Complete plugin implementation::

        from qtframework.plugins.base import Plugin, PluginMetadata, PluginState
        from PySide6.QtWidgets import QAction, QMessageBox

        # Define plugin metadata
        metadata = PluginMetadata(
            id="com.example.hello",
            name="Hello Plugin",
            version="1.0.0",
            description="A simple hello world plugin",
            author="Your Name",
            category="utility",
            dependencies=[],
        )


        # Create plugin class
        class HelloPlugin(Plugin):
            def __init__(self):
                super().__init__(metadata)
                self.action = None

            def initialize(self) -> bool:
                '''Called once when plugin is loaded'''
                self.log("Plugin initializing...", "info")
                # Load resources, initialize state
                return True

            def activate(self) -> bool:
                '''Called when plugin is activated'''
                self.log("Plugin activated", "info")

                # Add menu action to application
                if self.application:
                    self.action = QAction("Say Hello", self.application.window)
                    self.action.triggered.connect(self.show_hello)

                    # Add to Tools menu
                    tools_menu = self.application.window.menuBar().addMenu("Tools")
                    tools_menu.addAction(self.action)

                return True

            def deactivate(self) -> bool:
                '''Called when plugin is deactivated'''
                self.log("Plugin deactivated", "info")

                # Remove UI elements
                if self.action:
                    self.action.deleteLater()
                    self.action = None

                return True

            def cleanup(self) -> None:
                '''Called when plugin is unloaded'''
                self.log("Plugin cleaning up", "info")
                # Release resources

            def show_hello(self):
                '''Show hello message'''
                QMessageBox.information(
                    self.application.window,
                    "Hello Plugin",
                    "Hello from the plugin system!",
                )

            def on_settings_changed(self, settings: dict):
                '''Handle settings changes'''
                greeting = settings.get("greeting", "Hello")
                self.log(f"Greeting changed to: {greeting}", "info")


        # Use in application
        from qtframework.plugins.manager import PluginManager

        plugin_manager = PluginManager()
        hello_plugin = HelloPlugin()

        # Load and activate plugin
        plugin_manager.register_plugin(hello_plugin)
        plugin_manager.load_plugin("com.example.hello")
        plugin_manager.activate_plugin("com.example.hello")

See Also:
    :class:`PluginManager`: Manages plugin loading and lifecycle
    :class:`PluginMetadata`: Plugin metadata and configuration
    :class:`PluginState`: Plugin state enumeration
"""

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

        Called once when the plugin is first loaded. Use for one-time setup
        like loading resources or registering services.

        Returns:
            True if initialization successful, False if plugin should not be loaded
        """
        return True

    def activate(self) -> bool:
        """Activate the plugin.

        Called when the plugin is enabled. Use for connecting signals,
        starting services, or adding UI elements.

        Returns:
            True if activation successful, False if plugin failed to activate
        """
        return True

    def deactivate(self) -> bool:
        """Deactivate the plugin.

        Called when the plugin is disabled. Use for disconnecting signals,
        stopping services, or removing UI elements. Plugin remains loaded.

        Returns:
            True if deactivation successful, False if plugin failed to deactivate
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
