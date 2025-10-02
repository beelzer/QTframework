"""Tests for configuration validation."""

from __future__ import annotations

import pytest

from qtframework.config.validator import ConfigValidator
from qtframework.utils.exceptions import ConfigurationError
from qtframework.utils.validation import ValidatorChain


class TestConfigValidator:
    """Test configuration validator."""

    def test_validator_initialization(self) -> None:
        """Test validator initializes with default validators."""
        validator = ConfigValidator()
        assert len(validator._validators) > 0
        assert "app.name" in validator._validators
        assert "app.version" in validator._validators

    def test_register_validator(self) -> None:
        """Test registering custom validators."""
        validator = ConfigValidator()
        custom_chain = ValidatorChain()

        validator.register_validator("custom.key", custom_chain)
        assert "custom.key" in validator._validators
        assert validator._validators["custom.key"] == custom_chain

    def test_validate_valid_config(self) -> None:
        """Test validating valid configuration."""
        validator = ConfigValidator()
        config = {
            "app": {
                "name": "TestApp",
                "version": "1.0.0",
            }
        }

        # Should not raise
        validator.validate(config, "test_source")

    def test_validate_invalid_app_name_empty(self) -> None:
        """Test validation fails for empty app name."""
        validator = ConfigValidator()
        config = {
            "app": {
                "name": "",
                "version": "1.0.0",
            }
        }

        with pytest.raises(ConfigurationError) as exc_info:
            validator.validate(config, "test_source")

        assert "app.name" in str(exc_info.value)

    def test_validate_invalid_app_name_too_long(self) -> None:
        """Test validation fails for too long app name."""
        validator = ConfigValidator()
        config = {
            "app": {
                "name": "x" * 101,  # max is 100
                "version": "1.0.0",
            }
        }

        with pytest.raises(ConfigurationError) as exc_info:
            validator.validate(config, "test_source")

        assert "app.name" in str(exc_info.value)

    def test_validate_invalid_version_empty(self) -> None:
        """Test validation fails for empty version."""
        validator = ConfigValidator()
        config = {
            "app": {
                "name": "TestApp",
                "version": "",
            }
        }

        with pytest.raises(ConfigurationError) as exc_info:
            validator.validate(config, "test_source")

        assert "app.version" in str(exc_info.value)

    def test_validate_database_port_valid(self) -> None:
        """Test validating valid database port."""
        validator = ConfigValidator()
        config = {
            "database": {
                "port": 5432,
            }
        }

        validator.validate(config, "test_source")

    def test_validate_database_port_invalid_too_low(self) -> None:
        """Test validation fails for port too low."""
        validator = ConfigValidator()
        config = {
            "database": {
                "port": 0,
            }
        }

        with pytest.raises(ConfigurationError) as exc_info:
            validator.validate(config, "test_source")

        assert "database.port" in str(exc_info.value)

    def test_validate_database_port_invalid_too_high(self) -> None:
        """Test validation fails for port too high."""
        validator = ConfigValidator()
        config = {
            "database": {
                "port": 70000,
            }
        }

        with pytest.raises(ConfigurationError) as exc_info:
            validator.validate(config, "test_source")

        assert "database.port" in str(exc_info.value)

    def test_validate_nested_config(self) -> None:
        """Test validating nested configuration."""
        validator = ConfigValidator()
        config = {
            "app": {
                "name": "TestApp",
            },
            "database": {
                "host": "localhost",
                "port": 5432,
            },
            "ui": {
                "theme": "dark",
                "font_scale": 100,
            },
        }

        validator.validate(config, "test_source")

    def test_validate_optional_fields(self) -> None:
        """Test validation with optional fields missing."""
        validator = ConfigValidator()
        config = {
            "ui": {
                "theme": "dark",
            }
        }

        # Should not raise for optional fields
        validator.validate(config, "test_source")

    def test_validate_font_scale_valid(self) -> None:
        """Test validating valid font scale."""
        validator = ConfigValidator()
        config = {
            "ui": {
                "font_scale": 125,
            }
        }

        validator.validate(config, "test_source")

    def test_validate_font_scale_invalid_too_low(self) -> None:
        """Test validation fails for font scale too low."""
        validator = ConfigValidator()
        config = {
            "ui": {
                "font_scale": 25,
            }
        }

        with pytest.raises(ConfigurationError) as exc_info:
            validator.validate(config, "test_source")

        assert "ui.font_scale" in str(exc_info.value)

    def test_validate_font_scale_invalid_too_high(self) -> None:
        """Test validation fails for font scale too high."""
        validator = ConfigValidator()
        config = {
            "ui": {
                "font_scale": 300,
            }
        }

        with pytest.raises(ConfigurationError) as exc_info:
            validator.validate(config, "test_source")

        assert "ui.font_scale" in str(exc_info.value)

    def test_validate_performance_settings(self) -> None:
        """Test validating performance settings."""
        validator = ConfigValidator()
        config = {
            "performance": {
                "cache_size": 500,
                "max_threads": 8,
            }
        }

        validator.validate(config, "test_source")

    def test_validate_debug_flag(self) -> None:
        """Test validating debug flag."""
        validator = ConfigValidator()
        config = {
            "app": {
                "debug": True,
            }
        }

        validator.validate(config, "test_source")

    def test_configuration_error_details(self) -> None:
        """Test that ConfigurationError includes proper details."""
        validator = ConfigValidator()
        config = {
            "app": {
                "name": "",
            }
        }

        with pytest.raises(ConfigurationError) as exc_info:
            validator.validate(config, "test_source")

        error = exc_info.value
        assert error.config_key == "app.name"
        assert error.config_value == ""
        assert error.source == "test_source"

    def test_validate_unregistered_keys_pass(self) -> None:
        """Test that unregistered keys pass validation."""
        validator = ConfigValidator()
        config = {
            "custom": {
                "unknown": "value",
            }
        }

        # Should not raise for unregistered keys
        validator.validate(config, "test_source")
