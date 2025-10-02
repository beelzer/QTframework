"""Tests for custom exceptions."""

from __future__ import annotations

import pytest

from qtframework.utils.exceptions import (
    ConfigurationError,
    NavigationError,
    PluginError,
    QtFrameworkError,
    SecurityError,
    StateError,
    ThemeError,
    ValidationError,
)


class TestQtFrameworkError:
    """Test base QtFrameworkError."""

    def test_error_creation_message_only(self) -> None:
        """Test creating error with message only."""
        error = QtFrameworkError("Test error")
        assert error.message == "Test error"
        assert error.details == {}

    def test_error_creation_with_details(self) -> None:
        """Test creating error with details."""
        error = QtFrameworkError("Test error", {"key": "value"})
        assert error.message == "Test error"
        assert error.details == {"key": "value"}

    def test_error_str_no_details(self) -> None:
        """Test string representation without details."""
        error = QtFrameworkError("Test error")
        assert str(error) == "Test error"

    def test_error_str_with_details(self) -> None:
        """Test string representation with details."""
        error = QtFrameworkError("Test error", {"key": "value", "num": 42})
        error_str = str(error)
        assert "Test error" in error_str
        assert "key=value" in error_str
        assert "num=42" in error_str

    def test_error_is_exception(self) -> None:
        """Test error is an Exception."""
        error = QtFrameworkError("Test")
        assert isinstance(error, Exception)

    def test_error_can_be_raised(self) -> None:
        """Test error can be raised."""
        with pytest.raises(QtFrameworkError, match="Test error"):
            raise QtFrameworkError("Test error")


class TestConfigurationError:
    """Test ConfigurationError."""

    def test_config_error_minimal(self) -> None:
        """Test configuration error with minimal parameters."""
        error = ConfigurationError("Config failed")
        assert error.message == "Config failed"
        assert error.config_key is None
        assert error.config_value is None
        assert error.source is None

    def test_config_error_with_key(self) -> None:
        """Test configuration error with config key."""
        error = ConfigurationError("Invalid config", config_key="app.name")
        assert error.config_key == "app.name"
        assert "config_key" in error.details

    def test_config_error_with_value(self) -> None:
        """Test configuration error with config value."""
        error = ConfigurationError("Invalid value", config_value="bad_value")
        assert error.config_value == "bad_value"
        assert "config_value" in error.details

    def test_config_error_with_source(self) -> None:
        """Test configuration error with source."""
        error = ConfigurationError("Load failed", source="/path/to/config.yaml")
        assert error.source == "/path/to/config.yaml"
        assert "source" in error.details

    def test_config_error_full(self) -> None:
        """Test configuration error with all parameters."""
        error = ConfigurationError(
            "Config error",
            config_key="database.port",
            config_value=99999,
            source="config.yaml",
        )
        assert error.config_key == "database.port"
        assert error.config_value == 99999
        assert error.source == "config.yaml"
        assert len(error.details) == 3

    def test_config_error_inherits_base(self) -> None:
        """Test ConfigurationError inherits QtFrameworkError."""
        error = ConfigurationError("Test")
        assert isinstance(error, QtFrameworkError)


class TestPluginError:
    """Test PluginError."""

    def test_plugin_error_minimal(self) -> None:
        """Test plugin error with minimal parameters."""
        error = PluginError("Plugin failed")
        assert error.message == "Plugin failed"
        assert error.plugin_id is None
        assert error.plugin_path is None
        assert error.operation is None

    def test_plugin_error_with_id(self) -> None:
        """Test plugin error with plugin ID."""
        error = PluginError("Load failed", plugin_id="my.plugin")
        assert error.plugin_id == "my.plugin"
        assert "plugin_id" in error.details

    def test_plugin_error_with_path(self) -> None:
        """Test plugin error with plugin path."""
        error = PluginError("Load failed", plugin_path="/plugins/my_plugin.py")
        assert error.plugin_path == "/plugins/my_plugin.py"
        assert "plugin_path" in error.details

    def test_plugin_error_with_operation(self) -> None:
        """Test plugin error with operation."""
        error = PluginError("Operation failed", operation="activate")
        assert error.operation == "activate"
        assert "operation" in error.details

    def test_plugin_error_full(self) -> None:
        """Test plugin error with all parameters."""
        error = PluginError(
            "Plugin error",
            plugin_id="test.plugin",
            plugin_path="/path/to/plugin",
            operation="load",
        )
        assert error.plugin_id == "test.plugin"
        assert error.plugin_path == "/path/to/plugin"
        assert error.operation == "load"

    def test_plugin_error_inherits_base(self) -> None:
        """Test PluginError inherits QtFrameworkError."""
        error = PluginError("Test")
        assert isinstance(error, QtFrameworkError)


class TestThemeError:
    """Test ThemeError."""

    def test_theme_error_minimal(self) -> None:
        """Test theme error with minimal parameters."""
        error = ThemeError("Theme failed")
        assert error.message == "Theme failed"
        assert error.theme_name is None
        assert error.theme_path is None

    def test_theme_error_with_name(self) -> None:
        """Test theme error with theme name."""
        error = ThemeError("Load failed", theme_name="dark")
        assert error.theme_name == "dark"
        assert "theme_name" in error.details

    def test_theme_error_with_path(self) -> None:
        """Test theme error with theme path."""
        error = ThemeError("Load failed", theme_path="/themes/dark.yaml")
        assert error.theme_path == "/themes/dark.yaml"
        assert "theme_path" in error.details

    def test_theme_error_full(self) -> None:
        """Test theme error with all parameters."""
        error = ThemeError(
            "Theme error",
            theme_name="custom",
            theme_path="/path/to/theme.yaml",
        )
        assert error.theme_name == "custom"
        assert error.theme_path == "/path/to/theme.yaml"

    def test_theme_error_inherits_base(self) -> None:
        """Test ThemeError inherits QtFrameworkError."""
        error = ThemeError("Test")
        assert isinstance(error, QtFrameworkError)


class TestValidationError:
    """Test ValidationError."""

    def test_validation_error_minimal(self) -> None:
        """Test validation error with minimal parameters."""
        error = ValidationError("Validation failed")
        assert error.message == "Validation failed"
        assert error.field_name is None
        assert error.field_value is None
        assert error.validation_rule is None

    def test_validation_error_with_field_name(self) -> None:
        """Test validation error with field name."""
        error = ValidationError("Invalid field", field_name="email")
        assert error.field_name == "email"
        assert "field_name" in error.details

    def test_validation_error_with_field_value(self) -> None:
        """Test validation error with field value."""
        error = ValidationError("Invalid value", field_value="bad@email")
        assert error.field_value == "bad@email"
        assert "field_value" in error.details

    def test_validation_error_with_rule(self) -> None:
        """Test validation error with validation rule."""
        error = ValidationError("Rule failed", validation_rule="email_format")
        assert error.validation_rule == "email_format"
        assert "validation_rule" in error.details

    def test_validation_error_full(self) -> None:
        """Test validation error with all parameters."""
        error = ValidationError(
            "Validation failed",
            field_name="age",
            field_value=-5,
            validation_rule="positive_number",
        )
        assert error.field_name == "age"
        assert error.field_value == -5
        assert error.validation_rule == "positive_number"

    def test_validation_error_inherits_base(self) -> None:
        """Test ValidationError inherits QtFrameworkError."""
        error = ValidationError("Test")
        assert isinstance(error, QtFrameworkError)


class TestNavigationError:
    """Test NavigationError."""

    def test_navigation_error_minimal(self) -> None:
        """Test navigation error with minimal parameters."""
        error = NavigationError("Navigation failed")
        assert error.message == "Navigation failed"
        assert error.route_path is None
        assert error.from_path is None
        assert error.to_path is None

    def test_navigation_error_with_route(self) -> None:
        """Test navigation error with route path."""
        error = NavigationError("Route not found", route_path="/home")
        assert error.route_path == "/home"
        assert "route_path" in error.details

    def test_navigation_error_with_from_to(self) -> None:
        """Test navigation error with from/to paths."""
        error = NavigationError(
            "Navigation failed",
            from_path="/home",
            to_path="/settings",
        )
        assert error.from_path == "/home"
        assert error.to_path == "/settings"

    def test_navigation_error_full(self) -> None:
        """Test navigation error with all parameters."""
        error = NavigationError(
            "Navigation error",
            route_path="/profile",
            from_path="/home",
            to_path="/profile",
        )
        assert error.route_path == "/profile"
        assert error.from_path == "/home"
        assert error.to_path == "/profile"

    def test_navigation_error_inherits_base(self) -> None:
        """Test NavigationError inherits QtFrameworkError."""
        error = NavigationError("Test")
        assert isinstance(error, QtFrameworkError)


class TestStateError:
    """Test StateError."""

    def test_state_error_minimal(self) -> None:
        """Test state error with minimal parameters."""
        error = StateError("State error")
        assert error.message == "State error"
        assert error.action_type is None
        assert error.state_path is None

    def test_state_error_with_action_type(self) -> None:
        """Test state error with action type."""
        error = StateError("Action failed", action_type="UPDATE_USER")
        assert error.action_type == "UPDATE_USER"
        assert "action_type" in error.details

    def test_state_error_with_state_path(self) -> None:
        """Test state error with state path."""
        error = StateError("Invalid path", state_path="user.profile.name")
        assert error.state_path == "user.profile.name"
        assert "state_path" in error.details

    def test_state_error_full(self) -> None:
        """Test state error with all parameters."""
        error = StateError(
            "State error",
            action_type="DELETE",
            state_path="items.0",
        )
        assert error.action_type == "DELETE"
        assert error.state_path == "items.0"

    def test_state_error_inherits_base(self) -> None:
        """Test StateError inherits QtFrameworkError."""
        error = StateError("Test")
        assert isinstance(error, QtFrameworkError)


class TestSecurityError:
    """Test SecurityError."""

    def test_security_error_minimal(self) -> None:
        """Test security error with minimal parameters."""
        error = SecurityError("Security violation")
        assert error.message == "Security violation"
        assert error.security_context is None
        assert error.attempted_action is None

    def test_security_error_with_context(self) -> None:
        """Test security error with security context."""
        error = SecurityError("Access denied", security_context="plugin")
        assert error.security_context == "plugin"
        assert "security_context" in error.details

    def test_security_error_with_action(self) -> None:
        """Test security error with attempted action."""
        error = SecurityError("Forbidden", attempted_action="delete_config")
        assert error.attempted_action == "delete_config"
        assert "attempted_action" in error.details

    def test_security_error_full(self) -> None:
        """Test security error with all parameters."""
        error = SecurityError(
            "Security violation",
            security_context="config",
            attempted_action="write",
        )
        assert error.security_context == "config"
        assert error.attempted_action == "write"

    def test_security_error_inherits_base(self) -> None:
        """Test SecurityError inherits QtFrameworkError."""
        error = SecurityError("Test")
        assert isinstance(error, QtFrameworkError)


class TestExceptionInheritance:
    """Test exception inheritance hierarchy."""

    def test_all_inherit_base_error(self) -> None:
        """Test all custom errors inherit base error."""
        errors = [
            ConfigurationError("test"),
            PluginError("test"),
            ThemeError("test"),
            ValidationError("test"),
            NavigationError("test"),
            StateError("test"),
            SecurityError("test"),
        ]

        for error in errors:
            assert isinstance(error, QtFrameworkError)
            assert isinstance(error, Exception)
