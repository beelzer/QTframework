"""Plugin manager for handling plugin lifecycle."""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, Signal

from qtframework.plugins.base import Plugin, PluginMetadata, PluginState
from qtframework.utils.exceptions import PluginError, SecurityError
from qtframework.utils.logger import get_logger


if TYPE_CHECKING:
    from collections.abc import Callable

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
            logger.info("Added plugin path: %s", path)

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
                with Path(metadata_file).open(encoding="utf-8") as f:
                    data = json.load(f)
                return PluginMetadata(**data)
            except Exception as e:
                logger.exception("Failed to load metadata from %s: %s", metadata_file, e)
        return None

    def load_plugin(self, plugin_id: str, plugin_path: Path | None = None) -> bool:
        """Load a plugin with security validation.

        Args:
            plugin_id: Plugin ID
            plugin_path: Optional specific plugin path

        Returns:
            True if plugin loaded successfully

        Raises:
            PluginError: If plugin loading fails
            SecurityError: If security validation fails
        """
        if not isinstance(plugin_id, str) or not plugin_id:
            raise PluginError("Plugin ID must be a non-empty string", plugin_id=plugin_id)

        if plugin_id in self._plugins:
            logger.warning("Plugin %s already loaded", plugin_id)
            return True

        try:
            if plugin_path:
                # Validate plugin path security
                if not self._validate_plugin_path_security(plugin_path):
                    raise SecurityError(
                        f"Plugin path failed security validation: {plugin_path}",
                        security_context="plugin_loading",
                        attempted_action="load_plugin",
                    )
                plugin = self._load_plugin_from_path(plugin_path)
            else:
                plugin = self._find_and_load_plugin(plugin_id)

            if plugin:
                # Validate plugin instance
                self._validate_plugin_instance(plugin, plugin_id)

                self._plugins[plugin_id] = plugin
                if self._app is not None:
                    plugin.set_application(self._app)
                plugin.set_state(PluginState.LOADED)

                if plugin.initialize():
                    self.plugin_loaded.emit(plugin_id)
                    logger.info("Plugin %s loaded successfully", plugin_id)
                    return True
                plugin.set_state(PluginState.ERROR)
                del self._plugins[plugin_id]
                raise PluginError(
                    f"Plugin {plugin_id} initialization failed",
                    plugin_id=plugin_id,
                    operation="initialize",
                )
            raise PluginError(
                f"Failed to load plugin {plugin_id}", plugin_id=plugin_id, operation="load"
            )

        except (PluginError, SecurityError) as e:
            self.plugin_error.emit(plugin_id, str(e))
            raise
        except Exception as e:
            error = PluginError(
                f"Unexpected error loading plugin {plugin_id}: {e}",
                plugin_id=plugin_id,
                operation="load",
            )
            self.plugin_error.emit(plugin_id, str(error))
            raise error

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
                plugin = module.create_plugin()
                if isinstance(plugin, Plugin):
                    return plugin
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
            logger.error("Plugin %s not found", plugin_id)
            return False

        if plugin.state == PluginState.ACTIVE:
            logger.warning("Plugin %s already active", plugin_id)
            return True

        try:
            if plugin.activate():
                plugin.set_state(PluginState.ACTIVE)
                self.plugin_activated.emit(plugin_id)
                logger.info("Plugin %s activated", plugin_id)
                return True
            plugin.set_state(PluginState.ERROR)
            return False
        except Exception as e:
            logger.exception("Failed to activate plugin %s: %s", plugin_id, e)
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
            logger.error("Plugin %s not found", plugin_id)
            return False

        if plugin.state != PluginState.ACTIVE:
            logger.warning("Plugin %s not active", plugin_id)
            return True

        try:
            if plugin.deactivate():
                plugin.set_state(PluginState.LOADED)
                self.plugin_deactivated.emit(plugin_id)
                logger.info("Plugin %s deactivated", plugin_id)
                return True
            return False
        except Exception as e:
            logger.exception("Failed to deactivate plugin %s: %s", plugin_id, e)
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
            logger.info("Plugin %s unloaded", plugin_id)
            return True
        except Exception as e:
            logger.exception("Failed to unload plugin %s: %s", plugin_id, e)
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
                    logger.exception("Hook error in %s.%s: %s", plugin_id, hook_name, e)
        return results

    def _validate_plugin_path_security(self, path: Path) -> bool:
        """Validate plugin path for security concerns.

        Args:
            path: Plugin path to validate

        Returns:
            True if path passes security validation
        """
        try:
            # Ensure path exists and is a directory
            if not path.exists() or not path.is_dir():
                logger.warning("Plugin path does not exist or is not a directory: %s", path)
                return False

            # Check for restricted directories
            restricted_paths = [
                Path.home(),
                Path("/"),
                Path("C:\\"),
                Path("/usr"),
                Path("/bin"),
                Path("/sys"),
                Path("C:\\Windows"),
                Path("C:\\Program Files"),
            ]

            for restricted in restricted_paths:
                try:
                    if path.is_relative_to(restricted):
                        logger.warning("Plugin path in restricted directory: %s", path)
                        return False
                except (ValueError, TypeError):
                    continue

            # Check plugin directory size (prevent loading huge plugins)
            total_size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
            if total_size > 50 * 1024 * 1024:  # 50MB limit
                logger.warning("Plugin directory too large: %s (%s bytes)", path, total_size)
                return False

            # Check for main.py file
            main_file = path / "main.py"
            if not main_file.exists():
                logger.warning("Plugin missing main.py file: %s", path)
                return False

            # Basic security scan of main.py
            return self._validate_plugin_file_content(main_file)

        except Exception as e:
            logger.exception("Error validating plugin path security: %s", e)
            return False

    def _validate_plugin_file_content(self, file_path: Path) -> bool:
        """Validate plugin file content for security.

        Args:
            file_path: Path to plugin file

        Returns:
            True if file content is safe
        """
        try:
            content = file_path.read_text(encoding="utf-8")

            # Check for suspicious imports/operations
            suspicious_patterns = [
                "import os",
                "import sys",
                "import subprocess",
                "import shutil",
                "exec(",
                "eval(",
                "__import__",
                "open(",
                "file(",
                "urllib",
                "requests",
                "socket",
                "tempfile",
            ]

            for pattern in suspicious_patterns:
                if pattern in content:
                    logger.warning(
                        "Suspicious pattern '%s' found in plugin file: %s", pattern, file_path
                    )
                    return False

            return True

        except Exception as e:
            logger.exception("Error reading plugin file for security validation: %s", e)
            return False

    def _validate_plugin_instance(self, plugin: Plugin, plugin_id: str) -> None:
        """Validate plugin instance.

        Args:
            plugin: Plugin instance to validate
            plugin_id: Plugin ID

        Raises:
            PluginError: If plugin validation fails
        """
        # Check if plugin is actually a Plugin instance
        if not isinstance(plugin, Plugin):
            raise PluginError(
                f"Plugin {plugin_id} is not a valid Plugin instance", plugin_id=plugin_id
            )

        # Check required methods
        required_methods = ["initialize", "activate", "deactivate", "cleanup"]
        for method in required_methods:
            if not hasattr(plugin, method) or not callable(getattr(plugin, method)):
                raise PluginError(
                    f"Plugin {plugin_id} missing required method: {method}", plugin_id=plugin_id
                )

        # Check plugin metadata if available
        if hasattr(plugin, "metadata"):
            metadata = plugin.metadata
            if metadata and hasattr(metadata, "id") and metadata.id != plugin_id:
                raise PluginError(
                    f"Plugin metadata ID mismatch: expected {plugin_id}, got {metadata.id}",
                    plugin_id=plugin_id,
                )
