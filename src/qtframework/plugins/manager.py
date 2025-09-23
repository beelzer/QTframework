"""Plugin manager for handling plugin lifecycle."""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from PySide6.QtCore import QObject, Signal

from qtframework.plugins.base import Plugin, PluginMetadata, PluginState
from qtframework.utils.logger import get_logger

if TYPE_CHECKING:
    from qtframework.core.application import Application

logger = get_logger(__name__)


class PluginManager(QObject):
    """Manager for handling plugins."""

    plugin_loaded = Signal(str)
    plugin_activated = Signal(str)
    plugin_deactivated = Signal(str)
    plugin_error = Signal(str, str)

    def __init__(self, application: Application | None = None) -> None:
        """Initialize plugin manager.

        Args:
            application: Application instance
        """
        super().__init__()
        self._app = application
        self._plugins: dict[str, Plugin] = {}
        self._plugin_paths: list[Path] = []
        self._hooks: dict[str, list[tuple[str, Callable]]] = {}

    def add_plugin_path(self, path: Path | str) -> None:
        """Add a plugin search path.

        Args:
            path: Path to search for plugins
        """
        path = Path(path)
        if path.exists() and path not in self._plugin_paths:
            self._plugin_paths.append(path)
            logger.info(f"Added plugin path: {path}")

    def discover_plugins(self) -> list[PluginMetadata]:
        """Discover available plugins.

        Returns:
            List of discovered plugin metadata
        """
        discovered = []
        for path in self._plugin_paths:
            if path.is_dir():
                for plugin_dir in path.iterdir():
                    if plugin_dir.is_dir():
                        metadata = self._load_plugin_metadata(plugin_dir)
                        if metadata:
                            discovered.append(metadata)
        logger.info(f"Discovered {len(discovered)} plugins")
        return discovered

    def _load_plugin_metadata(self, plugin_dir: Path) -> PluginMetadata | None:
        """Load plugin metadata from directory.

        Args:
            plugin_dir: Plugin directory

        Returns:
            Plugin metadata or None
        """
        metadata_file = plugin_dir / "plugin.json"
        if metadata_file.exists():
            import json

            try:
                with open(metadata_file, encoding="utf-8") as f:
                    data = json.load(f)
                return PluginMetadata(**data)
            except Exception as e:
                logger.error(f"Failed to load metadata from {metadata_file}: {e}")
        return None

    def load_plugin(self, plugin_id: str, plugin_path: Path | None = None) -> bool:
        """Load a plugin.

        Args:
            plugin_id: Plugin ID
            plugin_path: Optional specific plugin path

        Returns:
            True if plugin loaded successfully
        """
        if plugin_id in self._plugins:
            logger.warning(f"Plugin {plugin_id} already loaded")
            return True

        try:
            if plugin_path:
                plugin = self._load_plugin_from_path(plugin_path)
            else:
                plugin = self._find_and_load_plugin(plugin_id)

            if plugin:
                self._plugins[plugin_id] = plugin
                plugin.set_application(self._app)
                plugin.set_state(PluginState.LOADED)

                if plugin.initialize():
                    self.plugin_loaded.emit(plugin_id)
                    logger.info(f"Plugin {plugin_id} loaded successfully")
                    return True
                else:
                    plugin.set_state(PluginState.ERROR)
                    del self._plugins[plugin_id]
                    return False
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_id}: {e}")
            self.plugin_error.emit(plugin_id, str(e))

        return False

    def _load_plugin_from_path(self, path: Path) -> Plugin | None:
        """Load plugin from specific path.

        Args:
            path: Plugin path

        Returns:
            Plugin instance or None
        """
        main_file = path / "main.py"
        if not main_file.exists():
            return None

        spec = importlib.util.spec_from_file_location(f"plugin_{path.name}", main_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "create_plugin"):
                return module.create_plugin()
        return None

    def _find_and_load_plugin(self, plugin_id: str) -> Plugin | None:
        """Find and load plugin by ID.

        Args:
            plugin_id: Plugin ID

        Returns:
            Plugin instance or None
        """
        for path in self._plugin_paths:
            plugin_dir = path / plugin_id
            if plugin_dir.exists():
                return self._load_plugin_from_path(plugin_dir)
        return None

    def activate_plugin(self, plugin_id: str) -> bool:
        """Activate a plugin.

        Args:
            plugin_id: Plugin ID

        Returns:
            True if plugin activated successfully
        """
        plugin = self._plugins.get(plugin_id)
        if not plugin:
            logger.error(f"Plugin {plugin_id} not found")
            return False

        if plugin.state == PluginState.ACTIVE:
            logger.warning(f"Plugin {plugin_id} already active")
            return True

        try:
            if plugin.activate():
                plugin.set_state(PluginState.ACTIVE)
                self.plugin_activated.emit(plugin_id)
                logger.info(f"Plugin {plugin_id} activated")
                return True
            else:
                plugin.set_state(PluginState.ERROR)
                return False
        except Exception as e:
            logger.error(f"Failed to activate plugin {plugin_id}: {e}")
            plugin.set_state(PluginState.ERROR)
            self.plugin_error.emit(plugin_id, str(e))
            return False

    def deactivate_plugin(self, plugin_id: str) -> bool:
        """Deactivate a plugin.

        Args:
            plugin_id: Plugin ID

        Returns:
            True if plugin deactivated successfully
        """
        plugin = self._plugins.get(plugin_id)
        if not plugin:
            logger.error(f"Plugin {plugin_id} not found")
            return False

        if plugin.state != PluginState.ACTIVE:
            logger.warning(f"Plugin {plugin_id} not active")
            return True

        try:
            if plugin.deactivate():
                plugin.set_state(PluginState.LOADED)
                self.plugin_deactivated.emit(plugin_id)
                logger.info(f"Plugin {plugin_id} deactivated")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to deactivate plugin {plugin_id}: {e}")
            self.plugin_error.emit(plugin_id, str(e))
            return False

    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin.

        Args:
            plugin_id: Plugin ID

        Returns:
            True if plugin unloaded successfully
        """
        plugin = self._plugins.get(plugin_id)
        if not plugin:
            return True

        if plugin.state == PluginState.ACTIVE:
            self.deactivate_plugin(plugin_id)

        try:
            plugin.cleanup()
            del self._plugins[plugin_id]
            logger.info(f"Plugin {plugin_id} unloaded")
            return True
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_id}: {e}")
            return False

    def get_plugin(self, plugin_id: str) -> Plugin | None:
        """Get a plugin by ID.

        Args:
            plugin_id: Plugin ID

        Returns:
            Plugin instance or None
        """
        return self._plugins.get(plugin_id)

    def get_all_plugins(self) -> dict[str, Plugin]:
        """Get all loaded plugins.

        Returns:
            Dictionary of plugins
        """
        return self._plugins.copy()

    def get_active_plugins(self) -> list[Plugin]:
        """Get all active plugins.

        Returns:
            List of active plugins
        """
        return [p for p in self._plugins.values() if p.state == PluginState.ACTIVE]

    def register_global_hook(self, hook_name: str, plugin_id: str, callback: Callable) -> None:
        """Register a global hook.

        Args:
            hook_name: Hook name
            plugin_id: Plugin ID
            callback: Callback function
        """
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append((plugin_id, callback))

    def trigger_global_hook(self, hook_name: str, *args: Any, **kwargs: Any) -> list[Any]:
        """Trigger a global hook.

        Args:
            hook_name: Hook name
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            List of hook results
        """
        results = []
        if hook_name in self._hooks:
            for plugin_id, callback in self._hooks[hook_name]:
                try:
                    result = callback(*args, **kwargs)
                    results.append((plugin_id, result))
                except Exception as e:
                    logger.error(f"Hook error in {plugin_id}.{hook_name}: {e}")
        return results