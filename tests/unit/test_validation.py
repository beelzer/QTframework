"""Tests for validation framework."""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

import pytest

from qtframework.utils.exceptions import ValidationError
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
    optional_email_field,
    optional_string,
    path_field,
    required_string,
)


class TestValidatorBase:
    """Test base Validator class."""

    def test_validator_creation_default_message(self) -> None:
        """Test validator creation with default message."""

        class TestValidator(Validator):
            def validate(self, value, field_name="") -> bool:
                return True

        validator = TestValidator()
        assert validator.message == "Validation failed"

    def test_validator_creation_custom_message(self) -> None:
        """Test validator creation with custom message."""

        class TestValidator(Validator):
            def validate(self, value, field_name="") -> bool:
                return True

        validator = TestValidator(message="Custom error")
        assert validator.message == "Custom error"

    def test_validator_callable(self) -> None:
        """Test validator is callable."""

        class TestValidator(Validator):
            def validate(self, value, field_name="") -> bool:
                return value == "valid"

        validator = TestValidator()
        assert validator("valid") is True


class TestRequiredValidator:
    """Test RequiredValidator."""

    def test_required_validator_default_message(self) -> None:
        """Test required validator default message."""
        validator = RequiredValidator()
        assert validator.message == "This field is required"

    def test_required_validator_custom_message(self) -> None:
        """Test required validator custom message."""
        validator = RequiredValidator(message="Field cannot be empty")
        assert validator.message == "Field cannot be empty"

    def test_required_validator_valid_string(self) -> None:
        """Test required validator with valid string."""
        validator = RequiredValidator()
        assert validator.validate("test", "field") is True

    def test_required_validator_empty_string(self) -> None:
        """Test required validator with empty string."""
        validator = RequiredValidator()
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("", "field")
        assert exc_info.value.validation_rule == "required"

    def test_required_validator_none(self) -> None:
        """Test required validator with None."""
        validator = RequiredValidator()
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(None, "field")
        assert exc_info.value.field_name == "field"

    def test_required_validator_empty_list(self) -> None:
        """Test required validator with empty list."""
        validator = RequiredValidator()
        with pytest.raises(ValidationError):
            validator.validate([], "field")

    def test_required_validator_valid_list(self) -> None:
        """Test required validator with valid list."""
        validator = RequiredValidator()
        assert validator.validate([1, 2, 3], "field") is True


class TestLengthValidator:
    """Test LengthValidator."""

    def test_length_validator_min_only(self) -> None:
        """Test length validator with min only."""
        validator = LengthValidator(min_length=3)
        assert "at least 3" in validator.message

    def test_length_validator_max_only(self) -> None:
        """Test length validator with max only."""
        validator = LengthValidator(max_length=10)
        assert "not exceed 10" in validator.message

    def test_length_validator_both(self) -> None:
        """Test length validator with min and max."""
        validator = LengthValidator(min_length=3, max_length=10)
        assert "between 3 and 10" in validator.message

    def test_length_validator_valid_length(self) -> None:
        """Test length validator with valid length."""
        validator = LengthValidator(min_length=3, max_length=10)
        assert validator.validate("hello", "field") is True

    def test_length_validator_too_short(self) -> None:
        """Test length validator with too short string."""
        validator = LengthValidator(min_length=5)
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("ab", "field")
        assert "min_length:5" in exc_info.value.validation_rule

    def test_length_validator_too_long(self) -> None:
        """Test length validator with too long string."""
        validator = LengthValidator(max_length=5)
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("toolongstring", "field")
        assert "max_length:5" in exc_info.value.validation_rule

    def test_length_validator_non_string(self) -> None:
        """Test length validator converts non-string to string."""
        validator = LengthValidator(min_length=1, max_length=5)
        assert validator.validate(123, "field") is True

    def test_length_validator_none_value(self) -> None:
        """Test length validator with None value."""
        validator = LengthValidator(min_length=1)
        with pytest.raises(ValidationError):
            validator.validate(None, "field")


class TestRegexValidator:
    """Test RegexValidator."""

    def test_regex_validator_string_pattern(self) -> None:
        """Test regex validator with string pattern."""
        validator = RegexValidator(r"^\d{3}$")
        assert validator.pattern.pattern == r"^\d{3}$"

    def test_regex_validator_compiled_pattern(self) -> None:
        """Test regex validator with compiled pattern."""
        pattern = re.compile(r"^\d{3}$")
        validator = RegexValidator(pattern)
        assert validator.pattern == pattern

    def test_regex_validator_valid_match(self) -> None:
        """Test regex validator with valid match."""
        validator = RegexValidator(r"^\d{3}$")
        assert validator.validate("123", "field") is True

    def test_regex_validator_invalid_match(self) -> None:
        """Test regex validator with invalid match."""
        validator = RegexValidator(r"^\d{3}$")
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("abc", "field")
        assert "regex:" in exc_info.value.validation_rule

    def test_regex_validator_non_string(self) -> None:
        """Test regex validator converts non-string."""
        validator = RegexValidator(r"^\d+$")
        assert validator.validate(123, "field") is True

    def test_regex_validator_custom_message(self) -> None:
        """Test regex validator with custom message."""
        validator = RegexValidator(r"^\d{3}$", message="Must be 3 digits")
        assert validator.message == "Must be 3 digits"


class TestEmailValidator:
    """Test EmailValidator."""

    def test_email_validator_valid_email(self) -> None:
        """Test email validator with valid email."""
        validator = EmailValidator()
        assert validator.validate("user@example.com", "email") is True

    def test_email_validator_valid_subdomain(self) -> None:
        """Test email validator with subdomain."""
        validator = EmailValidator()
        assert validator.validate("user@mail.example.com", "email") is True

    def test_email_validator_invalid_no_at(self) -> None:
        """Test email validator without @ symbol."""
        validator = EmailValidator()
        with pytest.raises(ValidationError):
            validator.validate("userexample.com", "email")

    def test_email_validator_invalid_no_domain(self) -> None:
        """Test email validator without domain."""
        validator = EmailValidator()
        with pytest.raises(ValidationError):
            validator.validate("user@", "email")

    def test_email_validator_invalid_no_tld(self) -> None:
        """Test email validator without TLD."""
        validator = EmailValidator()
        with pytest.raises(ValidationError):
            validator.validate("user@example", "email")

    def test_email_validator_custom_message(self) -> None:
        """Test email validator with custom message."""
        validator = EmailValidator(message="Invalid email format")
        assert validator.message == "Invalid email format"


class TestNumberValidator:
    """Test NumberValidator."""

    def test_number_validator_min_only(self) -> None:
        """Test number validator with min only."""
        validator = NumberValidator(min_value=0)
        assert "at least 0" in validator.message

    def test_number_validator_max_only(self) -> None:
        """Test number validator with max only."""
        validator = NumberValidator(max_value=100)
        assert "not exceed 100" in validator.message

    def test_number_validator_both(self) -> None:
        """Test number validator with min and max."""
        validator = NumberValidator(min_value=0, max_value=100)
        assert "between 0 and 100" in validator.message

    def test_number_validator_valid_int(self) -> None:
        """Test number validator with valid integer."""
        validator = NumberValidator(min_value=0, max_value=100)
        assert validator.validate(50, "field") is True

    def test_number_validator_valid_float(self) -> None:
        """Test number validator with valid float."""
        validator = NumberValidator(min_value=0.0, max_value=100.0)
        assert validator.validate(50.5, "field") is True

    def test_number_validator_too_small(self) -> None:
        """Test number validator with too small value."""
        validator = NumberValidator(min_value=10)
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(5, "field")
        assert "min_value:10" in exc_info.value.validation_rule

    def test_number_validator_too_large(self) -> None:
        """Test number validator with too large value."""
        validator = NumberValidator(max_value=10)
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(15, "field")
        assert "max_value:10" in exc_info.value.validation_rule

    def test_number_validator_string_number(self) -> None:
        """Test number validator with string number."""
        validator = NumberValidator(min_value=0, max_value=100)
        assert validator.validate("50", "field") is True

    def test_number_validator_invalid_string(self) -> None:
        """Test number validator with invalid string."""
        validator = NumberValidator()
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("not a number", "field")
        assert exc_info.value.validation_rule == "number"

    def test_number_validator_no_float_allowed(self) -> None:
        """Test number validator with float not allowed."""
        validator = NumberValidator(allow_float=False)
        with pytest.raises(ValidationError):
            validator.validate("3.14", "field")

    def test_number_validator_int_only(self) -> None:
        """Test number validator with integers only."""
        validator = NumberValidator(allow_float=False)
        assert validator.validate(10, "field") is True


class TestPathValidator:
    """Test PathValidator."""

    def test_path_validator_default(self) -> None:
        """Test path validator with defaults."""
        validator = PathValidator()
        assert validator.validate("/some/path", "field") is True

    def test_path_validator_existing_file(self) -> None:
        """Test path validator with existing file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = Path(f.name)

        try:
            validator = PathValidator(must_exist=True, must_be_file=True)
            assert validator.validate(str(path), "field") is True
        finally:
            path.unlink()

    def test_path_validator_existing_dir(self) -> None:
        """Test path validator with existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = PathValidator(must_exist=True, must_be_dir=True)
            assert validator.validate(tmpdir, "field") is True

    def test_path_validator_nonexistent_path(self) -> None:
        """Test path validator with nonexistent path."""
        validator = PathValidator(must_exist=True)
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("/nonexistent/path", "field")
        assert exc_info.value.validation_rule == "path_exists"

    def test_path_validator_not_a_file(self) -> None:
        """Test path validator expecting file but got directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = PathValidator(must_exist=True, must_be_file=True)
            with pytest.raises(ValidationError) as exc_info:
                validator.validate(tmpdir, "field")
            assert exc_info.value.validation_rule == "path_is_file"

    def test_path_validator_not_a_dir(self) -> None:
        """Test path validator expecting directory but got file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = Path(f.name)

        try:
            validator = PathValidator(must_exist=True, must_be_dir=True)
            with pytest.raises(ValidationError) as exc_info:
                validator.validate(str(path), "field")
            assert exc_info.value.validation_rule == "path_is_dir"
        finally:
            path.unlink()

    def test_path_validator_invalid_type(self) -> None:
        """Test path validator with invalid type."""
        validator = PathValidator()
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(123, "field")
        assert exc_info.value.validation_rule == "path_type"

    def test_path_validator_path_object(self) -> None:
        """Test path validator with Path object."""
        validator = PathValidator()
        assert validator.validate(Path("/some/path"), "field") is True


class TestChoiceValidator:
    """Test ChoiceValidator."""

    def test_choice_validator_valid_choice(self) -> None:
        """Test choice validator with valid choice."""
        validator = ChoiceValidator(["red", "green", "blue"])
        assert validator.validate("red", "field") is True

    def test_choice_validator_invalid_choice(self) -> None:
        """Test choice validator with invalid choice."""
        validator = ChoiceValidator(["red", "green", "blue"])
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("yellow", "field")
        assert "choice:" in exc_info.value.validation_rule

    def test_choice_validator_numeric_choices(self) -> None:
        """Test choice validator with numeric choices."""
        validator = ChoiceValidator([1, 2, 3])
        assert validator.validate(2, "field") is True

    def test_choice_validator_message(self) -> None:
        """Test choice validator message generation."""
        validator = ChoiceValidator(["a", "b", "c"])
        assert "a, b, c" in validator.message

    def test_choice_validator_custom_message(self) -> None:
        """Test choice validator with custom message."""
        validator = ChoiceValidator([1, 2, 3], message="Must select 1, 2, or 3")
        assert validator.message == "Must select 1, 2, or 3"


class TestCustomValidator:
    """Test CustomValidator."""

    def test_custom_validator_valid(self) -> None:
        """Test custom validator with valid value."""
        validator = CustomValidator(lambda x: x > 0, message="Must be positive")
        assert validator.validate(5, "field") is True

    def test_custom_validator_invalid(self) -> None:
        """Test custom validator with invalid value."""
        validator = CustomValidator(lambda x: x > 0, message="Must be positive")
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(-5, "field")
        assert exc_info.value.message == "Must be positive"

    def test_custom_validator_exception(self) -> None:
        """Test custom validator with exception."""

        def failing_validator(value):
            raise ValueError("Something went wrong")

        validator = CustomValidator(failing_validator)
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("test", "field")
        assert "Something went wrong" in exc_info.value.message

    def test_custom_validator_raises_validation_error(self) -> None:
        """Test custom validator that raises ValidationError."""

        def validator_func(value):
            if value != "valid":
                raise ValidationError("Custom validation failed", field_name="field")
            return True

        validator = CustomValidator(validator_func)
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("invalid", "field")
        assert exc_info.value.message == "Custom validation failed"


class TestValidationResult:
    """Test ValidationResult."""

    def test_validation_result_default(self) -> None:
        """Test validation result defaults."""
        result = ValidationResult()
        assert result.is_valid is True
        assert result.errors == []

    def test_validation_result_with_errors(self) -> None:
        """Test validation result with errors."""
        errors = [
            ValidationError("Error 1", field_name="field1"),
            ValidationError("Error 2", field_name="field2"),
        ]
        result = ValidationResult(is_valid=False, errors=errors)
        assert result.is_valid is False
        assert len(result.errors) == 2

    def test_validation_result_add_error(self) -> None:
        """Test adding error to result."""
        result = ValidationResult()
        result.add_error(ValidationError("Error", field_name="field"))
        assert result.is_valid is False
        assert len(result.errors) == 1

    def test_validation_result_get_field_errors(self) -> None:
        """Test getting errors for specific field."""
        result = ValidationResult()
        result.add_error(ValidationError("Error 1", field_name="field1"))
        result.add_error(ValidationError("Error 2", field_name="field2"))
        result.add_error(ValidationError("Error 3", field_name="field1"))

        field1_errors = result.get_field_errors("field1")
        assert len(field1_errors) == 2

    def test_validation_result_get_error_messages(self) -> None:
        """Test getting all error messages."""
        result = ValidationResult()
        result.add_error(ValidationError("Error 1"))
        result.add_error(ValidationError("Error 2"))

        messages = result.get_error_messages()
        assert "Error 1" in messages
        assert "Error 2" in messages

    def test_validation_result_get_field_error_messages(self) -> None:
        """Test getting error messages for specific field."""
        result = ValidationResult()
        result.add_error(ValidationError("Field1 Error", field_name="field1"))
        result.add_error(ValidationError("Field2 Error", field_name="field2"))

        messages = result.get_field_error_messages("field1")
        assert messages == ["Field1 Error"]


class TestValidatorChain:
    """Test ValidatorChain."""

    def test_validator_chain_empty(self) -> None:
        """Test empty validator chain."""
        chain = ValidatorChain()
        result = chain.validate("value", "field")
        assert result.is_valid is True

    def test_validator_chain_with_validators(self) -> None:
        """Test validator chain with validators."""
        chain = ValidatorChain([RequiredValidator(), LengthValidator(min_length=3)])
        result = chain.validate("hello", "field")
        assert result.is_valid is True

    def test_validator_chain_add_validator(self) -> None:
        """Test adding validator to chain."""
        chain = ValidatorChain()
        chain.add_validator(RequiredValidator())
        assert len(chain.validators) == 1

    def test_validator_chain_all_pass(self) -> None:
        """Test validator chain where all pass."""
        chain = ValidatorChain([
            RequiredValidator(),
            LengthValidator(min_length=3, max_length=10),
        ])
        result = chain.validate("hello", "field")
        assert result.is_valid is True

    def test_validator_chain_one_fails(self) -> None:
        """Test validator chain where one fails."""
        chain = ValidatorChain([
            RequiredValidator(),
            LengthValidator(min_length=10),
        ])
        result = chain.validate("short", "field")
        assert result.is_valid is False
        assert len(result.errors) == 1

    def test_validator_chain_multiple_fail(self) -> None:
        """Test validator chain where multiple fail."""
        chain = ValidatorChain([
            LengthValidator(min_length=10),
            EmailValidator(),
        ])
        result = chain.validate("short", "field")
        assert result.is_valid is False
        assert len(result.errors) == 2

    def test_validator_chain_fluent_interface(self) -> None:
        """Test validator chain fluent interface."""
        chain = (
            ValidatorChain()
            .add_validator(RequiredValidator())
            .add_validator(LengthValidator(min_length=3))
        )
        assert len(chain.validators) == 2


class TestFormValidator:
    """Test FormValidator."""

    def test_form_validator_empty(self) -> None:
        """Test empty form validator."""
        form = FormValidator()
        result = form.validate({})
        assert result.is_valid is True

    def test_form_validator_add_field_list(self) -> None:
        """Test adding field with validator list."""
        form = FormValidator()
        form.add_field("username", [RequiredValidator()])
        assert "username" in form.field_validators

    def test_form_validator_add_field_chain(self) -> None:
        """Test adding field with validator chain."""
        form = FormValidator()
        chain = ValidatorChain([RequiredValidator()])
        form.add_field("username", chain)
        assert "username" in form.field_validators

    def test_form_validator_all_valid(self) -> None:
        """Test form validator with all valid fields."""
        form = FormValidator()
        form.add_field("username", [RequiredValidator(), LengthValidator(min_length=3)])
        form.add_field("email", [RequiredValidator(), EmailValidator()])

        data = {"username": "john", "email": "john@example.com"}
        result = form.validate(data)
        assert result.is_valid is True

    def test_form_validator_one_invalid(self) -> None:
        """Test form validator with one invalid field."""
        form = FormValidator()
        form.add_field("username", [RequiredValidator()])
        form.add_field("email", [RequiredValidator(), EmailValidator()])

        data = {"username": "john", "email": "invalid"}
        result = form.validate(data)
        assert result.is_valid is False
        assert len(result.get_field_errors("email")) == 1

    def test_form_validator_multiple_invalid(self) -> None:
        """Test form validator with multiple invalid fields."""
        form = FormValidator()
        form.add_field("username", [RequiredValidator()])
        form.add_field("email", [RequiredValidator(), EmailValidator()])

        data = {"username": "", "email": "invalid"}
        result = form.validate(data)
        assert result.is_valid is False
        assert len(result.errors) == 2

    def test_form_validator_missing_field(self) -> None:
        """Test form validator with missing field."""
        form = FormValidator()
        form.add_field("username", [RequiredValidator()])

        data = {}
        result = form.validate(data)
        assert result.is_valid is False

    def test_form_validator_fluent_interface(self) -> None:
        """Test form validator fluent interface."""
        form = (
            FormValidator()
            .add_field("username", [RequiredValidator()])
            .add_field("email", [EmailValidator()])
        )
        assert len(form.field_validators) == 2


class TestPredefinedValidators:
    """Test predefined validator chain functions."""

    def test_required_string_default(self) -> None:
        """Test required_string with defaults."""
        chain = required_string()
        result = chain.validate("test", "field")
        assert result.is_valid is True

    def test_required_string_with_length(self) -> None:
        """Test required_string with length constraints."""
        chain = required_string(min_length=3, max_length=10)
        result = chain.validate("hello", "field")
        assert result.is_valid is True

    def test_required_string_too_short(self) -> None:
        """Test required_string with too short value."""
        chain = required_string(min_length=5)
        result = chain.validate("hi", "field")
        assert result.is_valid is False

    def test_optional_string_default(self) -> None:
        """Test optional_string with defaults."""
        chain = optional_string()
        result = chain.validate("", "field")
        assert result.is_valid is True

    def test_optional_string_with_max(self) -> None:
        """Test optional_string with max length."""
        chain = optional_string(max_length=10)
        result = chain.validate("short", "field")
        assert result.is_valid is True

    def test_optional_string_too_long(self) -> None:
        """Test optional_string exceeding max length."""
        chain = optional_string(max_length=5)
        result = chain.validate("toolongstring", "field")
        assert result.is_valid is False

    def test_email_field_valid(self) -> None:
        """Test email_field with valid email."""
        chain = email_field()
        result = chain.validate("user@example.com", "field")
        assert result.is_valid is True

    def test_email_field_invalid(self) -> None:
        """Test email_field with invalid email."""
        chain = email_field()
        result = chain.validate("invalid", "field")
        assert result.is_valid is False

    def test_optional_email_field_valid(self) -> None:
        """Test optional_email_field with valid email."""
        chain = optional_email_field()
        result = chain.validate("user@example.com", "field")
        assert result.is_valid is True

    def test_optional_email_field_empty(self) -> None:
        """Test optional_email_field with empty value."""
        chain = optional_email_field()
        result = chain.validate("", "field")
        assert result.is_valid is False

    def test_number_field_valid(self) -> None:
        """Test number_field with valid number."""
        chain = number_field(min_value=0, max_value=100)
        result = chain.validate(50, "field")
        assert result.is_valid is True

    def test_number_field_out_of_range(self) -> None:
        """Test number_field with out of range value."""
        chain = number_field(min_value=0, max_value=100)
        result = chain.validate(150, "field")
        assert result.is_valid is False

    def test_path_field_valid(self) -> None:
        """Test path_field with valid path."""
        chain = path_field()
        result = chain.validate("/some/path", "field")
        assert result.is_valid is True

    def test_path_field_existing_file(self) -> None:
        """Test path_field with existing file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = Path(f.name)

        try:
            chain = path_field(must_exist=True, must_be_file=True)
            result = chain.validate(str(path), "field")
            assert result.is_valid is True
        finally:
            path.unlink()

    def test_choice_field_valid(self) -> None:
        """Test choice_field with valid choice."""
        chain = choice_field(["red", "green", "blue"])
        result = chain.validate("red", "field")
        assert result.is_valid is True

    def test_choice_field_invalid(self) -> None:
        """Test choice_field with invalid choice."""
        chain = choice_field(["red", "green", "blue"])
        result = chain.validate("yellow", "field")
        assert result.is_valid is False


class TestValidationIntegration:
    """Test validation integration scenarios."""

    def test_complex_form_validation(self) -> None:
        """Test complex form validation scenario."""
        form = FormValidator()
        form.add_field("username", required_string(min_length=3, max_length=20))
        form.add_field("email", email_field())
        form.add_field("age", number_field(min_value=18, max_value=120))
        form.add_field("country", choice_field(["US", "UK", "CA"]))

        data = {
            "username": "john_doe",
            "email": "john@example.com",
            "age": 25,
            "country": "US",
        }

        result = form.validate(data)
        assert result.is_valid is True

    def test_complex_form_multiple_errors(self) -> None:
        """Test complex form with multiple errors."""
        form = FormValidator()
        form.add_field("username", required_string(min_length=3, max_length=20))
        form.add_field("email", email_field())
        form.add_field("age", number_field(min_value=18, max_value=120))

        data = {"username": "ab", "email": "invalid", "age": 15}

        result = form.validate(data)
        assert result.is_valid is False
        assert len(result.errors) == 3

    def test_nested_validation_chains(self) -> None:
        """Test nested validation chains."""
        chain = ValidatorChain([
            RequiredValidator(),
            LengthValidator(min_length=8),
            RegexValidator(r".*[A-Z].*", message="Must contain uppercase"),
            RegexValidator(r".*[0-9].*", message="Must contain number"),
        ])

        result = chain.validate("Password123", "password")
        assert result.is_valid is True

    def test_custom_business_rule(self) -> None:
        """Test custom business rule validation."""

        def age_check(value):
            age = int(value)
            return 18 <= age <= 65

        form = FormValidator()
        form.add_field(
            "age",
            [
                RequiredValidator(),
                NumberValidator(min_value=0, max_value=120),
                CustomValidator(
                    age_check, message="Age must be between 18 and 65 for this service"
                ),
            ],
        )

        # Valid age
        result = form.validate({"age": 30})
        assert result.is_valid is True

        # Invalid age (too young)
        result = form.validate({"age": 15})
        assert result.is_valid is False
