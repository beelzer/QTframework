"""Configuration management system.

This module provides a flexible configuration system that supports multiple
sources (files, environment variables, programmatic), validation, and
hierarchical key access.

Configuration Patterns:
    Loading configuration from multiple sources::

        from qtframework.config import ConfigManager, YamlProvider, EnvProvider

        # Create config manager
        config_mgr = ConfigManager()

        # Add YAML file provider
        config_mgr.add_provider(YamlProvider("config.yaml"), priority=10)

        # Add environment variables with prefix
        config_mgr.add_provider(
            EnvProvider(prefix="APP_"),
            priority=20,  # Higher priority overrides YAML
        )

        # Load configuration
        config_mgr.load()

        # Access configuration
        config = config_mgr.get_config()
        db_host = config.get("database.host", "localhost")
        api_key = config["api.key"]

    Configuration file structure::

        # config.yaml
        database:
          host: localhost
          port: 5432
          name: myapp

        api:
          key: secret_key_here
          timeout: 30

        features:
          enable_analytics: true
          max_upload_size: 10485760

    Environment variable mapping::

        # Environment variables (with APP_ prefix)
        APP_DATABASE__HOST = prod.example.com
        APP_DATABASE__PORT = 5432
        APP_API__KEY = production_key

        # Double underscore (__) becomes dot (.) in config path
        # APP_DATABASE__HOST → database.host

    Using Config directly::

        from qtframework.config import Config

        # Create from dictionary
        config = Config({"app": {"name": "MyApp", "version": "1.0.0"}, "debug": True})

        # Access with dot notation
        app_name = config.get("app.name")
        debug = config.get("debug", False)

        # Dict-like access
        version = config["app.version"]

        # Check key existence
        if "app.theme" in config:
            theme = config["app.theme"]

        # Get section
        app_config = config.get("app")  # Returns {"name": "MyApp", "version": "1.0.0"}

Hierarchical Access:
    Configuration keys support dot notation for nested access::

        config.get("database.host")  # Simple nested key
        config.get("features.cache.ttl", 300)  # With default value
        config["api.endpoints.users"]  # Dict-style access

See Also:
    :class:`Config`: Main configuration container
    :class:`ConfigManager`: Multi-source configuration manager
    :class:`YamlProvider`: YAML file configuration provider
    :class:`EnvProvider`: Environment variable provider
    :class:`JsonProvider`: JSON file configuration provider
"""

from __future__ import annotations

from qtframework.config.config import Config
from qtframework.config.file_loader import ConfigFileLoader
from qtframework.config.manager import ConfigManager
from qtframework.config.migrator import ConfigMigrator
from qtframework.config.providers import (
    ConfigProvider,
    EnvProvider,
    FileProvider,
    JsonProvider,
    YamlProvider,
)
from qtframework.config.validator import ConfigValidator


__all__ = [
    "Config",
    "ConfigFileLoader",
    "ConfigManager",
    "ConfigMigrator",
    "ConfigProvider",
    "ConfigValidator",
    "EnvProvider",
    "FileProvider",
    "JsonProvider",
    "YamlProvider",
]
