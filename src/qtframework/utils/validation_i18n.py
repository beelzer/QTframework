"""Validation module with i18n support."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any

from qtframework.i18n import t
from qtframework.utils.exceptions import ValidationError


class I18nValidator(ABC):
    """Base class for validators with i18n support."""

    def __init__(
        self,
        message: str | None = None,
        translation_key: str | None = None,
        **translation_args,
    ) -> None:
        """Initialize validator.

        Args:
            message: Custom error message (overrides translation)
            translation_key: Translation key for error message
            **translation_args: Arguments for translation interpolation
        """
        self.message = message
        self.translation_key = translation_key
        self.translation_args = translation_args

    def get_error_message(self, **additional_args) -> str:
        """Get error message with i18n support."""
        if self.message:
            return self.message

        if self.translation_key:
            args = {**self.translation_args, **additional_args}
            return t(self.translation_key, **args)

        # Fallback to default English message
        return self._get_default_message(**additional_args)

    @abstractmethod
    def _get_default_message(self, **kwargs) -> str:
        """Get default error message."""

    @abstractmethod
    def validate(self, value: Any, field_name: str = "") -> bool:
        """Validate a value."""

    def __call__(self, value: Any, field_name: str = "") -> bool:
        """Make validator callable."""
        return self.validate(value, field_name)


class RequiredValidator(I18nValidator):
    """Validates that a value is not empty with i18n support."""

    def __init__(
        self,
        message: str | None = None,
        translation_key: str | None = "form.validation.required",
    ) -> None:
        """Initialize required validator."""
        super().__init__(message, translation_key)

    def _get_default_message(self, **kwargs) -> str:
        """Get default error message."""
        return "This field is required"

    def validate(self, value: Any, field_name: str = "") -> bool:
        """Validate that value is not empty."""
        if value is None or value == "" or (hasattr(value, "__len__") and len(value) == 0):
            raise ValidationError(
                self.get_error_message(field_name=field_name),
                field_name=field_name,
                field_value=value,
                validation_rule="required",
            )
        return True


class LengthValidator(I18nValidator):
    """Validates string length with i18n support."""

    def __init__(
        self,
        min_length: int | None = None,
        max_length: int | None = None,
        message: str | None = None,
        translation_key: str | None = None,
    ) -> None:
        """Initialize length validator."""
        self.min_length = min_length
        self.max_length = max_length

        # Determine appropriate translation key
        if not translation_key:
            if min_length and max_length:
                translation_key = "form.validation.length_range"
            elif min_length:
                translation_key = "form.validation.min_length"
            elif max_length:
                translation_key = "form.validation.max_length"

        super().__init__(
            message,
            translation_key,
            min=min_length,
            max=max_length,
        )

    def _get_default_message(self, **kwargs) -> str:
        """Get default error message."""
        if self.min_length and self.max_length:
            return f"Length must be between {self.min_length} and {self.max_length} characters"
        if self.min_length:
            return f"Length must be at least {self.min_length} characters"
        if self.max_length:
            return f"Length must not exceed {self.max_length} characters"
        return "Invalid length"

    def validate(self, value: Any, field_name: str = "") -> bool:
        """Validate string length."""
        if not isinstance(value, str):
            value = str(value) if value is not None else ""

        length = len(value)

        if self.min_length is not None and length < self.min_length:
            raise ValidationError(
                self.get_error_message(min=self.min_length, actual=length),
                field_name=field_name,
                field_value=value,
                validation_rule=f"min_length:{self.min_length}",
            )

        if self.max_length is not None and length > self.max_length:
            raise ValidationError(
                self.get_error_message(max=self.max_length, actual=length),
                field_name=field_name,
                field_value=value,
                validation_rule=f"max_length:{self.max_length}",
            )

        return True


class EmailValidator(I18nValidator):
    """Validates email addresses with i18n support."""

    EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    def __init__(
        self,
        message: str | None = None,
        translation_key: str | None = "form.validation.email",
    ) -> None:
        """Initialize email validator."""
        self.pattern = re.compile(self.EMAIL_PATTERN)
        super().__init__(message, translation_key)

    def _get_default_message(self, **kwargs) -> str:
        """Get default error message."""
        return "Please enter a valid email address"

    def validate(self, value: Any, field_name: str = "") -> bool:
        """Validate email address."""
        if not isinstance(value, str):
            value = str(value) if value is not None else ""

        if not self.pattern.match(value):
            raise ValidationError(
                self.get_error_message(),
                field_name=field_name,
                field_value=value,
                validation_rule="email",
            )

        return True


class NumberValidator(I18nValidator):
    """Validates numeric values with i18n support."""

    def __init__(
        self,
        min_value: float | None = None,
        max_value: float | None = None,
        allow_float: bool = True,
        message: str | None = None,
        translation_key: str | None = None,
    ) -> None:
        """Initialize number validator."""
        self.min_value = min_value
        self.max_value = max_value
        self.allow_float = allow_float

        # Determine appropriate translation key
        if not translation_key:
            if min_value is not None and max_value is not None:
                translation_key = "form.validation.range"
            elif min_value is not None:
                translation_key = "form.validation.min_value"
            elif max_value is not None:
                translation_key = "form.validation.max_value"
            else:
                translation_key = "form.validation.number"

        super().__init__(
            message,
            translation_key,
            min=min_value,
            max=max_value,
        )

    def _get_default_message(self, **kwargs) -> str:
        """Get default error message."""
        if self.min_value is not None and self.max_value is not None:
            return f"Value must be between {self.min_value} and {self.max_value}"
        if self.min_value is not None:
            return f"Value must be at least {self.min_value}"
        if self.max_value is not None:
            return f"Value must not exceed {self.max_value}"
        return "Please enter a valid number"

    def validate(self, value: Any, field_name: str = "") -> bool:
        """Validate numeric value."""
        try:
            if self.allow_float:
                num_value = float(value)
            else:
                num_value = int(value)
                if str(value).count(".") > 0:
                    raise ValueError("Float not allowed")
        except (ValueError, TypeError):
            raise ValidationError(
                t("form.validation.number"),
                field_name=field_name,
                field_value=value,
                validation_rule="number",
            )

        if self.min_value is not None and num_value < self.min_value:
            raise ValidationError(
                self.get_error_message(min=self.min_value, actual=num_value),
                field_name=field_name,
                field_value=value,
                validation_rule=f"min_value:{self.min_value}",
            )

        if self.max_value is not None and num_value > self.max_value:
            raise ValidationError(
                self.get_error_message(max=self.max_value, actual=num_value),
                field_name=field_name,
                field_value=value,
                validation_rule=f"max_value:{self.max_value}",
            )

        return True


class PatternValidator(I18nValidator):
    """Validates value against a regular expression with i18n support."""

    def __init__(
        self,
        pattern: str | re.Pattern[str],
        message: str | None = None,
        translation_key: str | None = "form.validation.pattern",
    ) -> None:
        """Initialize pattern validator."""
        self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
        super().__init__(message, translation_key)

    def _get_default_message(self, **kwargs) -> str:
        """Get default error message."""
        return "Please match the required format"

    def validate(self, value: Any, field_name: str = "") -> bool:
        """Validate value against pattern."""
        if not isinstance(value, str):
            value = str(value) if value is not None else ""

        if not self.pattern.match(value):
            raise ValidationError(
                self.get_error_message(),
                field_name=field_name,
                field_value=value,
                validation_rule=f"pattern:{self.pattern.pattern}",
            )

        return True


# Export all validators
__all__ = [
    "EmailValidator",
    "I18nValidator",
    "LengthValidator",
    "NumberValidator",
    "PatternValidator",
    "RequiredValidator",
]
