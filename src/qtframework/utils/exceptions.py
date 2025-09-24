"""Custom exceptions for the Qt Framework."""

from __future__ import annotations

from typing import Any


class QtFrameworkError(Exception):
    """Base exception for Qt Framework errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize framework error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """String representation of error."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class ConfigurationError(QtFrameworkError):
    """Configuration-related errors."""

    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        config_value: Any = None,
        source: str | None = None,
    ) -> None:
        """Initialize configuration error.

        Args:
            message: Error message
            config_key: Configuration key that caused the error
            config_value: Configuration value that caused the error
            source: Configuration source (file, env, etc.)
        """
        details = {}
        if config_key:
            details["config_key"] = config_key
        if config_value is not None:
            details["config_value"] = config_value
        if source:
            details["source"] = source

        super().__init__(message, details)
        self.config_key = config_key
        self.config_value = config_value
        self.source = source


class PluginError(QtFrameworkError):
    """Plugin-related errors."""

    def __init__(
        self,
        message: str,
        plugin_id: str | None = None,
        plugin_path: str | None = None,
        operation: str | None = None,
    ) -> None:
        """Initialize plugin error.

        Args:
            message: Error message
            plugin_id: Plugin ID
            plugin_path: Plugin path
            operation: Operation that failed (load, activate, etc.)
        """
        details = {}
        if plugin_id:
            details["plugin_id"] = plugin_id
        if plugin_path:
            details["plugin_path"] = plugin_path
        if operation:
            details["operation"] = operation

        super().__init__(message, details)
        self.plugin_id = plugin_id
        self.plugin_path = plugin_path
        self.operation = operation


class ThemeError(QtFrameworkError):
    """Theme-related errors."""

    def __init__(
        self,
        message: str,
        theme_name: str | None = None,
        theme_path: str | None = None,
    ) -> None:
        """Initialize theme error.

        Args:
            message: Error message
            theme_name: Theme name
            theme_path: Theme file path
        """
        details = {}
        if theme_name:
            details["theme_name"] = theme_name
        if theme_path:
            details["theme_path"] = theme_path

        super().__init__(message, details)
        self.theme_name = theme_name
        self.theme_path = theme_path


class ValidationError(QtFrameworkError):
    """Input validation errors."""

    def __init__(
        self,
        message: str,
        field_name: str | None = None,
        field_value: Any = None,
        validation_rule: str | None = None,
    ) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            field_name: Name of field that failed validation
            field_value: Value that failed validation
            validation_rule: Validation rule that failed
        """
        details = {}
        if field_name:
            details["field_name"] = field_name
        if field_value is not None:
            details["field_value"] = field_value
        if validation_rule:
            details["validation_rule"] = validation_rule

        super().__init__(message, details)
        self.field_name = field_name
        self.field_value = field_value
        self.validation_rule = validation_rule


class NavigationError(QtFrameworkError):
    """Navigation and routing errors."""

    def __init__(
        self,
        message: str,
        route_path: str | None = None,
        from_path: str | None = None,
        to_path: str | None = None,
    ) -> None:
        """Initialize navigation error.

        Args:
            message: Error message
            route_path: Route path that caused error
            from_path: Source route path
            to_path: Target route path
        """
        details = {}
        if route_path:
            details["route_path"] = route_path
        if from_path:
            details["from_path"] = from_path
        if to_path:
            details["to_path"] = to_path

        super().__init__(message, details)
        self.route_path = route_path
        self.from_path = from_path
        self.to_path = to_path


class StateError(QtFrameworkError):
    """State management errors."""

    def __init__(
        self,
        message: str,
        action_type: str | None = None,
        state_path: str | None = None,
    ) -> None:
        """Initialize state error.

        Args:
            message: Error message
            action_type: Action type that caused error
            state_path: State path that caused error
        """
        details = {}
        if action_type:
            details["action_type"] = action_type
        if state_path:
            details["state_path"] = state_path

        super().__init__(message, details)
        self.action_type = action_type
        self.state_path = state_path


class SecurityError(QtFrameworkError):
    """Security-related errors."""

    def __init__(
        self,
        message: str,
        security_context: str | None = None,
        attempted_action: str | None = None,
    ) -> None:
        """Initialize security error.

        Args:
            message: Error message
            security_context: Security context (plugin, config, etc.)
            attempted_action: Action that was attempted
        """
        details = {}
        if security_context:
            details["security_context"] = security_context
        if attempted_action:
            details["attempted_action"] = attempted_action

        super().__init__(message, details)
        self.security_context = security_context
        self.attempted_action = attempted_action
