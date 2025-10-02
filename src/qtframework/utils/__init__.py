"""Utility modules for the framework."""

from __future__ import annotations

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
from qtframework.utils.logger import get_logger, setup_logging
from qtframework.utils.paths import (
    ensure_directory,
    find_config_files,
    get_preferred_config_path,
    get_system_config_dir,
    get_user_cache_dir,
    get_user_config_dir,
    get_user_data_dir,
)
from qtframework.utils.search import (
    SearchableMixin,
    SearchHighlighter,
    collect_searchable_text,
)
from qtframework.utils.styling import (
    batch_style_updates,
    refresh_widget_style,
    set_heading_level,
    set_widget_properties,
    set_widget_property,
    set_widget_variant,
)
from qtframework.utils.validation import (
    ChoiceValidator,
    CustomValidator,
    EmailValidator,
    FormValidator,
    LengthValidator,
    NumberValidator,
    PathValidator,
    RegexValidator,
    RequiredValidator,
    ValidationResult,
    Validator,
    ValidatorChain,
    choice_field,
    email_field,
    number_field,
    optional_string,
    path_field,
    required_string,
)


__all__ = [
    "ChoiceValidator",
    "ConfigurationError",
    "CustomValidator",
    "EmailValidator",
    "FormValidator",
    "LengthValidator",
    "NavigationError",
    "NumberValidator",
    "PathValidator",
    "PluginError",
    # Exceptions
    "QtFrameworkError",
    "RegexValidator",
    "RequiredValidator",
    "SearchHighlighter",
    "SearchableMixin",
    "SecurityError",
    "StateError",
    "ThemeError",
    "ValidationError",
    "ValidationResult",
    # Validation
    "Validator",
    "ValidatorChain",
    "batch_style_updates",
    "choice_field",
    "collect_searchable_text",
    "email_field",
    "ensure_directory",
    "find_config_files",
    # Logging
    "get_logger",
    "get_preferred_config_path",
    "get_system_config_dir",
    "get_user_cache_dir",
    # Paths
    "get_user_config_dir",
    "get_user_data_dir",
    "number_field",
    "optional_string",
    "path_field",
    "refresh_widget_style",
    "required_string",
    "set_heading_level",
    "set_widget_properties",
    "set_widget_property",
    "set_widget_variant",
    "setup_logging",
]
