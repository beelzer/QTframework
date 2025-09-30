"""Input validation framework for Qt Framework.

This module provides a comprehensive validation system with built-in validators
for common use cases (email, numbers, paths, etc.) and support for custom
validators and multi-field form validation.

Example:
    Basic validation with built-in validators::

        from qtframework.utils.validation import (
            RequiredValidator,
            EmailValidator,
            LengthValidator,
            NumberValidator,
            ValidationError,
        )

        # Simple field validation
        email_validator = EmailValidator()
        try:
            email_validator.validate("user@example.com", "email")
            print("Valid email!")
        except ValidationError as e:
            print(f"Error: {e.message}")

        # Chained validators
        from qtframework.utils.validation import ValidatorChain

        username_validators = ValidatorChain([
            RequiredValidator("Username is required"),
            LengthValidator(min_length=3, max_length=20),
        ])

        result = username_validators.validate("ab", "username")
        if not result.is_valid:
            print(result.get_error_messages())

    Complete form validation example::

        from qtframework.utils.validation import (
            FormValidator,
            required_string,
            email_field,
            number_field,
        )

        # Create form validator
        form = FormValidator()
        form.add_field("username", required_string(min_length=3, max_length=20))
        form.add_field("email", email_field())
        form.add_field("age", number_field(min_value=18, max_value=120))

        # Validate form data
        data = {"username": "john_doe", "email": "john@example.com", "age": 25}

        result = form.validate(data)
        if result.is_valid:
            print("Form is valid!")
        else:
            for error in result.errors:
                print(f"{error.field_name}: {error.message}")

    Integration with Input widgets::

        from qtframework.widgets.inputs import Input
        from qtframework.utils.validation import email_field

        # Create input with validation
        email_input = Input(
            label="Email Address",
            placeholder="Enter your email",
            validators=email_field().validators,
        )


        # Validate on change
        def on_email_change(text):
            result = email_field().validate(text, "email")
            if not result.is_valid:
                email_input.set_error(result.get_error_messages()[0])
            else:
                email_input.clear_error()


        email_input.textChanged.connect(on_email_change)

See Also:
    :class:`Validator`: Base validator class for custom validators
    :class:`FormValidator`: Multi-field form validation
    :exc:`qtframework.utils.exceptions.ValidationError`: Validation error exception
    :mod:`qtframework.widgets.inputs`: Input widgets with validation support
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

from qtframework.utils.exceptions import ValidationError


if TYPE_CHECKING:
    from collections.abc import Callable


class Validator(ABC):
    """Base class for validators."""

    def __init__(self, message: str | None = None) -> None:
        """Initialize validator.

        Args:
            message: Custom error message
        """
        self.message: str = message or "Validation failed"

    @abstractmethod
    def validate(self, value: Any, field_name: str = "") -> bool:
        """Validate a value.

        Args:
            value: Value to validate
            field_name: Name of the field being validated

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """

    def __call__(self, value: Any, field_name: str = "") -> bool:
        """Make validator callable."""
        return self.validate(value, field_name)


class RequiredValidator(Validator):
    """Validates that a value is not empty."""

    def __init__(self, message: str | None = None) -> None:
        """Initialize required validator."""
        super().__init__(message or "This field is required")

    def validate(self, value: Any, field_name: str = "") -> bool:
        """Validate that value is not empty."""
        if value is None or value == "" or (hasattr(value, "__len__") and len(value) == 0):
            raise ValidationError(
                self.message, field_name=field_name, field_value=value, validation_rule="required"
            )
        return True


class LengthValidator(Validator):
    """Validates string length."""

    def __init__(
        self,
        min_length: int | None = None,
        max_length: int | None = None,
        message: str | None = None,
    ) -> None:
        """Initialize length validator.

        Args:
            min_length: Minimum length
            max_length: Maximum length
            message: Custom error message
        """
        self.min_length = min_length
        self.max_length = max_length

        if not message:
            if min_length and max_length:
                message = f"Length must be between {min_length} and {max_length} characters"
            elif min_length:
                message = f"Length must be at least {min_length} characters"
            elif max_length:
                message = f"Length must not exceed {max_length} characters"
            else:
                message = "Invalid length"

        super().__init__(message)

    def validate(self, value: Any, field_name: str = "") -> bool:
        """Validate string length."""
        if not isinstance(value, str):
            value = str(value) if value is not None else ""

        length = len(value)

        if self.min_length is not None and length < self.min_length:
            raise ValidationError(
                self.message,
                field_name=field_name,
                field_value=value,
                validation_rule=f"min_length:{self.min_length}",
            )

        if self.max_length is not None and length > self.max_length:
            raise ValidationError(
                self.message,
                field_name=field_name,
                field_value=value,
                validation_rule=f"max_length:{self.max_length}",
            )

        return True


class RegexValidator(Validator):
    """Validates value against a regular expression."""

    def __init__(self, pattern: str | re.Pattern[str], message: str | None = None) -> None:
        """Initialize regex validator.

        Args:
            pattern: Regular expression pattern
            message: Custom error message
        """
        self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
        super().__init__(message or f"Value does not match required pattern: {pattern}")

    def validate(self, value: Any, field_name: str = "") -> bool:
        """Validate value against regex pattern."""
        if not isinstance(value, str):
            value = str(value) if value is not None else ""

        if not self.pattern.match(value):
            raise ValidationError(
                self.message,
                field_name=field_name,
                field_value=value,
                validation_rule=f"regex:{self.pattern.pattern}",
            )

        return True


class EmailValidator(RegexValidator):
    """Validates email addresses."""

    EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    def __init__(self, message: str | None = None) -> None:
        """Initialize email validator."""
        super().__init__(self.EMAIL_PATTERN, message or "Please enter a valid email address")


class NumberValidator(Validator):
    """Validates numeric values."""

    def __init__(
        self,
        min_value: float | None = None,
        max_value: float | None = None,
        allow_float: bool = True,
        message: str | None = None,
    ) -> None:
        """Initialize number validator.

        Args:
            min_value: Minimum value
            max_value: Maximum value
            allow_float: Whether to allow floating point numbers
            message: Custom error message
        """
        self.min_value = min_value
        self.max_value = max_value
        self.allow_float = allow_float

        if not message:
            if min_value is not None and max_value is not None:
                message = f"Value must be between {min_value} and {max_value}"
            elif min_value is not None:
                message = f"Value must be at least {min_value}"
            elif max_value is not None:
                message = f"Value must not exceed {max_value}"
            else:
                message = "Invalid number"

        super().__init__(message)

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
                "Please enter a valid number",
                field_name=field_name,
                field_value=value,
                validation_rule="number",
            )

        if self.min_value is not None and num_value < self.min_value:
            raise ValidationError(
                self.message,
                field_name=field_name,
                field_value=value,
                validation_rule=f"min_value:{self.min_value}",
            )

        if self.max_value is not None and num_value > self.max_value:
            raise ValidationError(
                self.message,
                field_name=field_name,
                field_value=value,
                validation_rule=f"max_value:{self.max_value}",
            )

        return True


class PathValidator(Validator):
    """Validates file and directory paths."""

    def __init__(
        self,
        must_exist: bool = False,
        must_be_file: bool = False,
        must_be_dir: bool = False,
        message: str | None = None,
    ) -> None:
        """Initialize path validator.

        Args:
            must_exist: Whether path must exist
            must_be_file: Whether path must be a file
            must_be_dir: Whether path must be a directory
            message: Custom error message
        """
        self.must_exist = must_exist
        self.must_be_file = must_be_file
        self.must_be_dir = must_be_dir
        super().__init__(message or "Invalid path")

    def validate(self, value: Any, field_name: str = "") -> bool:
        """Validate path."""
        if not isinstance(value, str | Path):
            raise ValidationError(
                "Path must be a string or Path object",
                field_name=field_name,
                field_value=value,
                validation_rule="path_type",
            )

        path = Path(value)

        if self.must_exist and not path.exists():
            raise ValidationError(
                "Path does not exist",
                field_name=field_name,
                field_value=value,
                validation_rule="path_exists",
            )

        if self.must_be_file and path.exists() and not path.is_file():
            raise ValidationError(
                "Path must be a file",
                field_name=field_name,
                field_value=value,
                validation_rule="path_is_file",
            )

        if self.must_be_dir and path.exists() and not path.is_dir():
            raise ValidationError(
                "Path must be a directory",
                field_name=field_name,
                field_value=value,
                validation_rule="path_is_dir",
            )

        return True


class ChoiceValidator(Validator):
    """Validates that value is one of allowed choices."""

    def __init__(self, choices: list[Any], message: str | None = None) -> None:
        """Initialize choice validator.

        Args:
            choices: List of allowed choices
            message: Custom error message
        """
        self.choices = choices
        super().__init__(message or f"Value must be one of: {', '.join(map(str, choices))}")

    def validate(self, value: Any, field_name: str = "") -> bool:
        """Validate that value is in choices."""
        if value not in self.choices:
            raise ValidationError(
                self.message,
                field_name=field_name,
                field_value=value,
                validation_rule=f"choice:{self.choices}",
            )
        return True


class CustomValidator(Validator):
    """Validates using a custom function."""

    def __init__(self, func: Callable[[Any], bool], message: str | None = None) -> None:
        """Initialize custom validator.

        Args:
            func: Validation function that returns True if valid
            message: Custom error message
        """
        self.func = func
        super().__init__(message or "Validation failed")

    def validate(self, value: Any, field_name: str = "") -> bool:
        """Validate using custom function."""
        try:
            if not self.func(value):
                raise ValidationError(
                    self.message, field_name=field_name, field_value=value, validation_rule="custom"
                )
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(
                f"Validation error: {e}",
                field_name=field_name,
                field_value=value,
                validation_rule="custom",
            )
        return True


class ValidationResult:
    """Result of validation operation."""

    def __init__(self, is_valid: bool = True, errors: list[ValidationError] | None = None) -> None:
        """Initialize validation result.

        Args:
            is_valid: Whether validation passed
            errors: List of validation errors
        """
        self.is_valid = is_valid
        self.errors = errors or []

    def add_error(self, error: ValidationError) -> None:
        """Add validation error."""
        self.errors.append(error)
        self.is_valid = False

    def get_field_errors(self, field_name: str) -> list[ValidationError]:
        """Get errors for specific field."""
        return [error for error in self.errors if error.field_name == field_name]

    def get_error_messages(self) -> list[str]:
        """Get all error messages."""
        return [error.message for error in self.errors]

    def get_field_error_messages(self, field_name: str) -> list[str]:
        """Get error messages for specific field."""
        return [error.message for error in self.get_field_errors(field_name)]


class ValidatorChain:
    """Chain of validators for a field."""

    def __init__(self, validators: list[Validator] | None = None) -> None:
        """Initialize validator chain.

        Args:
            validators: List of validators
        """
        self.validators = validators or []

    def add_validator(self, validator: Validator) -> ValidatorChain:
        """Add validator to chain."""
        self.validators.append(validator)
        return self

    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """Validate value using all validators in chain."""
        result = ValidationResult()

        for validator in self.validators:
            try:
                validator.validate(value, field_name)
            except ValidationError as e:
                result.add_error(e)

        return result


class FormValidator:
    """Validates multiple fields with different validators.

    Manages validation for entire forms with multiple fields, each having
    their own validation rules.

    Example:
        Multi-field form validation::

            from qtframework.utils.validation import (
                FormValidator,
                ValidatorChain,
                RequiredValidator,
                EmailValidator,
                LengthValidator,
                NumberValidator,
                CustomValidator,
            )

            # Create form validator
            form = FormValidator()

            # Add username validation
            form.add_field(
                "username",
                [RequiredValidator(), LengthValidator(min_length=3, max_length=20)],
            )

            # Add email validation
            form.add_field("email", [RequiredValidator(), EmailValidator()])


            # Add age validation with custom rule
            def check_age(value):
                age = int(value)
                return 18 <= age <= 120


            form.add_field(
                "age",
                [
                    RequiredValidator(),
                    NumberValidator(min_value=18, max_value=120, allow_float=False),
                    CustomValidator(check_age, "Age must be between 18 and 120"),
                ],
            )

            # Add password confirmation validation
            form.add_field("password", [RequiredValidator(), LengthValidator(min_length=8)])

            # Validate entire form
            data = {
                "username": "john_doe",
                "email": "john@example.com",
                "age": 25,
                "password": "securepass123",  # pragma: allowlist secret
            }

            result = form.validate(data)

            if result.is_valid:
                print("All fields valid!")
            else:
                # Get all errors
                for error in result.errors:
                    print(f"{error.field_name}: {error.message}")

                # Get errors for specific field
                username_errors = result.get_field_error_messages("username")
    """

    def __init__(self) -> None:
        """Initialize form validator."""
        self.field_validators: dict[str, ValidatorChain] = {}

    def add_field(
        self, field_name: str, validators: list[Validator] | ValidatorChain
    ) -> FormValidator:
        """Add field validation.

        Args:
            field_name: Name of field
            validators: Validators for the field
        """
        if isinstance(validators, list):
            validators = ValidatorChain(validators)
        self.field_validators[field_name] = validators
        return self

    def validate(self, data: dict[str, Any]) -> ValidationResult:
        """Validate all fields.

        Args:
            data: Dictionary of field values

        Returns:
            Validation result
        """
        result = ValidationResult()

        for field_name, validator_chain in self.field_validators.items():
            field_value = data.get(field_name)
            field_result = validator_chain.validate(field_value, field_name)

            if not field_result.is_valid:
                result.is_valid = False
                result.errors.extend(field_result.errors)

        return result


# Predefined validator chains for common use cases
def required_string(min_length: int = 1, max_length: int | None = None) -> ValidatorChain:
    """Create validator chain for required string."""
    validators: list[Validator] = [RequiredValidator()]
    if min_length > 1 or max_length:
        validators.append(LengthValidator(min_length, max_length))
    return ValidatorChain(validators)


def optional_string(max_length: int | None = None) -> ValidatorChain:
    """Create validator chain for optional string."""
    validators: list[Validator] = []
    if max_length:
        validators.append(LengthValidator(max_length=max_length))
    return ValidatorChain(validators)


def email_field() -> ValidatorChain:
    """Create validator chain for email field."""
    return ValidatorChain([RequiredValidator(), EmailValidator()])


def optional_email_field() -> ValidatorChain:
    """Create validator chain for optional email field."""
    return ValidatorChain([EmailValidator()])


def number_field(min_value: float | None = None, max_value: float | None = None) -> ValidatorChain:
    """Create validator chain for number field."""
    return ValidatorChain([RequiredValidator(), NumberValidator(min_value, max_value)])


def path_field(
    must_exist: bool = False, must_be_file: bool = False, must_be_dir: bool = False
) -> ValidatorChain:
    """Create validator chain for path field."""
    return ValidatorChain([
        RequiredValidator(),
        PathValidator(must_exist, must_be_file, must_be_dir),
    ])


def choice_field(choices: list[Any]) -> ValidatorChain:
    """Create validator chain for choice field."""
    return ValidatorChain([RequiredValidator(), ChoiceValidator(choices)])
