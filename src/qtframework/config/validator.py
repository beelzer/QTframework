"""Configuration validation logic."""

from __future__ import annotations

from typing import Any

from qtframework.utils.exceptions import ConfigurationError
from qtframework.utils.logger import get_logger
from qtframework.utils.validation import ValidatorChain


logger = get_logger(__name__)


class ConfigValidator:
    """Handles configuration validation using validator chains."""

    def __init__(self) -> None:
        """Initialize configuration validator."""
        self._validators: dict[str, ValidatorChain] = {}
        self._setup_default_validators()

    def _setup_default_validators(self) -> None:
        """Setup default configuration validators."""
        from qtframework.utils.validation import (
            number_field,
            optional_string,
            required_string,
        )

        # Application configuration validators
        self._validators.update({
            "app.name": required_string(min_length=1, max_length=100),
            "app.version": required_string(min_length=1, max_length=20),
            "app.debug": ValidatorChain(),  # Allow any boolean-like value
            # Database configuration
            "database.host": optional_string(max_length=255),
            "database.port": number_field(min_value=1, max_value=65535),
            "database.name": optional_string(max_length=100),
            # UI configuration
            "ui.theme": optional_string(
                max_length=50
            ),  # Allow any theme name since themes can be loaded from files
            "ui.language": optional_string(max_length=10),
            "ui.font_scale": number_field(min_value=50, max_value=200),  # Percentage: 50% to 200%
            # Performance settings
            "performance.cache_size": number_field(min_value=0, max_value=1000),
            "performance.max_threads": number_field(min_value=1, max_value=64),
        })

    def register_validator(self, key: str, validator: ValidatorChain) -> None:
        """Register a validator for a specific configuration key.

        Args:
            key: Configuration key (e.g., 'app.name')
            validator: Validator chain to use
        """
        self._validators[key] = validator

    def validate(self, data: dict[str, Any], source: str) -> None:
        """Validate configuration data.

        Args:
            data: Configuration data
            source: Data source identifier

        Raises:
            ConfigurationError: If validation fails
        """
        self._validate_nested(data, source)

    def _validate_nested(self, obj: dict[str, Any], source: str, prefix: str = "") -> None:
        """Recursively validate nested configuration objects.

        Args:
            obj: Configuration dictionary to validate
            source: Data source identifier
            prefix: Key prefix for nested paths
        """
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                self._validate_nested(value, source, full_key)
            # Validate individual values
            elif full_key in self._validators:
                try:
                    result = self._validators[full_key].validate(value, full_key)
                    if not result.is_valid:
                        errors = "; ".join(result.get_error_messages())
                        raise ConfigurationError(
                            f"Validation failed for '{full_key}': {errors}",
                            config_key=full_key,
                            config_value=value,
                            source=source,
                        )
                except Exception as e:
                    if isinstance(e, ConfigurationError):
                        raise
                    raise ConfigurationError(
                        f"Validation error for '{full_key}': {e}",
                        config_key=full_key,
                        config_value=value,
                        source=source,
                    )
