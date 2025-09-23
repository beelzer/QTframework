"""Utility modules for the framework."""

from __future__ import annotations

from qtframework.utils.logger import get_logger, setup_logging
from qtframework.utils.exceptions import (
    QtFrameworkError,
    ConfigurationError,
    PluginError,
    ThemeError,
    ValidationError,
    NavigationError,
    StateError,
    SecurityError,
)
from qtframework.utils.validation import (
    Validator,
    ValidatorChain,
    ValidationResult,
    FormValidator,
    RequiredValidator,
    LengthValidator,
    RegexValidator,
    EmailValidator,
    NumberValidator,
    PathValidator,
    ChoiceValidator,
    CustomValidator,
    required_string,
    optional_string,
    email_field,
    number_field,
    path_field,
    choice_field,
)
from qtframework.utils.paths import (
    get_user_config_dir,
    get_user_data_dir,
    get_user_cache_dir,
    get_system_config_dir,
    get_preferred_config_path,
    find_config_files,
    ensure_directory,
)

__all__ = [
    # Logging
    "get_logger",
    "setup_logging",
    # Exceptions
    "QtFrameworkError",
    "ConfigurationError",
    "PluginError",
    "ThemeError",
    "ValidationError",
    "NavigationError",
    "StateError",
    "SecurityError",
    # Validation
    "Validator",
    "ValidatorChain",
    "ValidationResult",
    "FormValidator",
    "RequiredValidator",
    "LengthValidator",
    "RegexValidator",
    "EmailValidator",
    "NumberValidator",
    "PathValidator",
    "ChoiceValidator",
    "CustomValidator",
    "required_string",
    "optional_string",
    "email_field",
    "number_field",
    "path_field",
    "choice_field",
    # Paths
    "get_user_config_dir",
    "get_user_data_dir",
    "get_user_cache_dir",
    "get_system_config_dir",
    "get_preferred_config_path",
    "find_config_files",
    "ensure_directory",
]
