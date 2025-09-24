"""Plugin system for extending the framework."""

from __future__ import annotations

from qtframework.plugins.base import Plugin, PluginMetadata
from qtframework.plugins.manager import PluginManager


__all__ = ["Plugin", "PluginManager", "PluginMetadata"]
