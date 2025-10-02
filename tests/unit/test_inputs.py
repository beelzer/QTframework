"""Tests for input widgets."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QLineEdit

from qtframework.utils.validation import EmailValidator, LengthValidator, RequiredValidator, ValidatorChain
from qtframework.widgets.inputs import Input, PasswordInput, SearchInput, TextArea

if TYPE_CHECKING:
    from pytest_qt.qtbot import QtBot


class TestInputCreation:
    """Test Input creation."""

    def test_input_creation_default(self, qtbot: QtBot) -> None:
        """Test creating input with defaults."""
        input_widget = Input()
        qtbot.addWidget(input_widget)
        assert input_widget.text() == ""
        assert not input_widget.isReadOnly()

    def test_input_creation_with_placeholder(self, qtbot: QtBot) -> None:
        """Test creating input with placeholder."""
        input_widget = Input(placeholder="Enter text")
        qtbot.addWidget(input_widget)
        assert input_widget.placeholderText() == "Enter text"

    def test_input_creation_with_value(self, qtbot: QtBot) -> None:
        """Test creating input with initial value."""
        input_widget = Input(value="initial")
        qtbot.addWidget(input_widget)
        assert input_widget.text() == "initial"

    def test_input_creation_readonly(self, qtbot: QtBot) -> None:
        """Test creating readonly input."""
        input_widget = Input(read_only=True)
        qtbot.addWidget(input_widget)
        assert input_widget.isReadOnly() is True

    def test_input_creation_with_max_length(self, qtbot: QtBot) -> None:
        """Test creating input with max length."""
        input_widget = Input(max_length=10)
        qtbot.addWidget(input_widget)
        assert input_widget.maxLength() == 10

    def test_input_creation_with_object_name(self, qtbot: QtBot) -> None:
        """Test creating input with object name."""
        input_widget = Input(object_name="test_input")
        qtbot.addWidget(input_widget)
        assert input_widget.objectName() == "test_input"

    def test_input_creation_with_validators(self, qtbot: QtBot) -> None:
        """Test creating input with validators."""
        validators = ValidatorChain([RequiredValidator()])
        input_widget = Input(validators=validators)
        qtbot.addWidget(input_widget)
        assert input_widget._validators == validators


class TestInputValidation:
    """Test Input validation."""

    def test_validate_with_no_validators(self, qtbot: QtBot) -> None:
        """Test validation with no validators."""
        input_widget = Input(value="test")
        qtbot.addWidget(input_widget)
        result = input_widget.validate()
        assert result.is_valid is True

    def test_validate_required_valid(self, qtbot: QtBot) -> None:
        """Test validation with required validator - valid."""
        validators = ValidatorChain([RequiredValidator()])
        input_widget = Input(value="test", validators=validators)
        qtbot.addWidget(input_widget)
        result = input_widget.validate()
        assert result.is_valid is True

    def test_validate_required_invalid(self, qtbot: QtBot) -> None:
        """Test validation with required validator - invalid."""
        validators = ValidatorChain([RequiredValidator()])
        input_widget = Input(validators=validators)
        qtbot.addWidget(input_widget)
        result = input_widget.validate()
        assert result.is_valid is False

    def test_validate_length_valid(self, qtbot: QtBot) -> None:
        """Test validation with length validator - valid."""
        validators = ValidatorChain([LengthValidator(min_length=3, max_length=10)])
        input_widget = Input(value="hello", validators=validators)
        qtbot.addWidget(input_widget)
        result = input_widget.validate()
        assert result.is_valid is True

    def test_validate_length_invalid(self, qtbot: QtBot) -> None:
        """Test validation with length validator - invalid."""
        validators = ValidatorChain([LengthValidator(min_length=5)])
        input_widget = Input(value="ab", validators=validators)
        qtbot.addWidget(input_widget)
        result = input_widget.validate()
        assert result.is_valid is False

    def test_validate_email_valid(self, qtbot: QtBot) -> None:
        """Test validation with email validator - valid."""
        validators = ValidatorChain([EmailValidator()])
        input_widget = Input(value="test@example.com", validators=validators)
        qtbot.addWidget(input_widget)
        result = input_widget.validate()
        assert result.is_valid is True

    def test_validate_email_invalid(self, qtbot: QtBot) -> None:
        """Test validation with email validator - invalid."""
        validators = ValidatorChain([EmailValidator()])
        input_widget = Input(value="invalid-email", validators=validators)
        qtbot.addWidget(input_widget)
        result = input_widget.validate()
        assert result.is_valid is False

    def test_validate_on_change(self, qtbot: QtBot) -> None:
        """Test validation on text change."""
        validators = ValidatorChain([RequiredValidator()])
        input_widget = Input(validators=validators, validate_on_change=True)
        qtbot.addWidget(input_widget)

        # Start empty - should be invalid
        result = input_widget.validate()
        assert result.is_valid is False

        # Type text - should validate automatically
        input_widget.setText("test")
        result = input_widget.validate()
        assert result.is_valid is True

    def test_validate_no_auto_validate(self, qtbot: QtBot) -> None:
        """Test no auto-validation when disabled."""
        validators = ValidatorChain([RequiredValidator()])
        input_widget = Input(validators=validators, validate_on_change=False)
        qtbot.addWidget(input_widget)

        # Text change should not trigger validation
        input_widget.setText("test")
        # Manually validate
        result = input_widget.validate()
        assert result.is_valid is True


class TestInputValidationState:
    """Test Input validation state management."""

    def test_has_validation_error_default(self, qtbot: QtBot) -> None:
        """Test validation error state defaults to False."""
        input_widget = Input()
        qtbot.addWidget(input_widget)
        assert input_widget.has_validation_error is False

    def test_set_validation_error(self, qtbot: QtBot) -> None:
        """Test setting validation error."""
        input_widget = Input()
        qtbot.addWidget(input_widget)

        input_widget.set_validation_error(True, "Error message")
        assert input_widget.has_validation_error is True
        assert input_widget.error_message == "Error message"

    def test_set_validation_error_emits_signal(self, qtbot: QtBot) -> None:
        """Test setting validation error emits signal."""
        input_widget = Input()
        qtbot.addWidget(input_widget)

        with qtbot.waitSignal(input_widget.validation_changed, timeout=1000) as blocker:
            input_widget.set_validation_error(True)

        assert blocker.args == [True]

    def test_clear_validation_error(self, qtbot: QtBot) -> None:
        """Test clearing validation error."""
        input_widget = Input()
        qtbot.addWidget(input_widget)

        input_widget.set_validation_error(True, "Error")
        input_widget.clear_validation_error()

        assert input_widget.has_validation_error is False
        assert input_widget.error_message == ""

    def test_error_message_property(self, qtbot: QtBot) -> None:
        """Test error message property."""
        input_widget = Input()
        qtbot.addWidget(input_widget)

        assert input_widget.error_message == ""

        input_widget.set_validation_error(True, "Test error")
        assert input_widget.error_message == "Test error"

    def test_validation_error_signal(self, qtbot: QtBot) -> None:
        """Test validation error signal emission."""
        validators = ValidatorChain([RequiredValidator()])
        input_widget = Input(validators=validators)
        qtbot.addWidget(input_widget)

        with qtbot.waitSignal(input_widget.validation_error, timeout=1000) as blocker:
            input_widget.validate()

        assert "required" in blocker.args[0].lower()


class TestInputValidators:
    """Test Input validator management."""

    def test_add_validator(self, qtbot: QtBot) -> None:
        """Test adding validator."""
        input_widget = Input()
        qtbot.addWidget(input_widget)

        assert len(input_widget._validators.validators) == 0

        input_widget.add_validator(RequiredValidator())
        assert len(input_widget._validators.validators) == 1

    def test_set_validators(self, qtbot: QtBot) -> None:
        """Test setting validators."""
        input_widget = Input()
        qtbot.addWidget(input_widget)

        new_validators = ValidatorChain([RequiredValidator(), EmailValidator()])
        input_widget.set_validators(new_validators)

        assert input_widget._validators == new_validators
        assert len(input_widget._validators.validators) == 2


class TestInputIcon:
    """Test Input icon functionality."""

    def test_set_icon_left(self, qtbot: QtBot) -> None:
        """Test setting icon on left."""
        input_widget = Input()
        qtbot.addWidget(input_widget)

        pixmap = QPixmap(16, 16)
        icon = QIcon(pixmap)
        input_widget.set_icon(icon, position="left")

        # Should have one action
        assert len(input_widget.actions()) == 1

    def test_set_icon_right(self, qtbot: QtBot) -> None:
        """Test setting icon on right."""
        input_widget = Input()
        qtbot.addWidget(input_widget)

        pixmap = QPixmap(16, 16)
        icon = QIcon(pixmap)
        input_widget.set_icon(icon, position="right")

        assert len(input_widget.actions()) == 1


class TestPasswordInput:
    """Test PasswordInput widget."""

    def test_password_input_creation(self, qtbot: QtBot) -> None:
        """Test creating password input."""
        password_input = PasswordInput()
        qtbot.addWidget(password_input)
        assert password_input.echoMode() == QLineEdit.EchoMode.Password

    def test_password_input_placeholder(self, qtbot: QtBot) -> None:
        """Test password input with custom placeholder."""
        password_input = PasswordInput(placeholder="Custom placeholder")
        qtbot.addWidget(password_input)
        assert password_input.placeholderText() == "Custom placeholder"

    def test_password_input_default_placeholder(self, qtbot: QtBot) -> None:
        """Test password input default placeholder."""
        password_input = PasswordInput()
        qtbot.addWidget(password_input)
        assert password_input.placeholderText() == "Enter password"

    def test_password_input_with_toggle(self, qtbot: QtBot) -> None:
        """Test password input with visibility toggle."""
        password_input = PasswordInput(show_toggle=True)
        qtbot.addWidget(password_input)
        assert len(password_input.actions()) == 1

    def test_password_input_without_toggle(self, qtbot: QtBot) -> None:
        """Test password input without visibility toggle."""
        password_input = PasswordInput(show_toggle=False)
        qtbot.addWidget(password_input)
        assert len(password_input.actions()) == 0

    def test_toggle_visibility(self, qtbot: QtBot) -> None:
        """Test toggling password visibility."""
        password_input = PasswordInput()
        qtbot.addWidget(password_input)

        assert password_input.echoMode() == QLineEdit.EchoMode.Password
        assert password_input._visible is False

        password_input.toggle_visibility()

        assert password_input.echoMode() == QLineEdit.EchoMode.Normal
        assert password_input._visible is True

    def test_toggle_visibility_emits_signal(self, qtbot: QtBot) -> None:
        """Test toggling visibility emits signal."""
        password_input = PasswordInput()
        qtbot.addWidget(password_input)

        with qtbot.waitSignal(password_input.visibility_changed, timeout=1000) as blocker:
            password_input.toggle_visibility()

        assert blocker.args == [True]

    def test_toggle_visibility_twice(self, qtbot: QtBot) -> None:
        """Test toggling visibility twice."""
        password_input = PasswordInput()
        qtbot.addWidget(password_input)

        password_input.toggle_visibility()
        assert password_input._visible is True

        password_input.toggle_visibility()
        assert password_input._visible is False


class TestSearchInput:
    """Test SearchInput widget."""

    def test_search_input_creation(self, qtbot: QtBot) -> None:
        """Test creating search input."""
        search_input = SearchInput()
        qtbot.addWidget(search_input)
        assert search_input.text() == ""

    def test_search_input_placeholder(self, qtbot: QtBot) -> None:
        """Test search input with custom placeholder."""
        search_input = SearchInput(placeholder="Custom search")
        qtbot.addWidget(search_input)
        assert search_input._input.placeholderText() == "Custom search"

    def test_search_input_default_placeholder(self, qtbot: QtBot) -> None:
        """Test search input default placeholder."""
        search_input = SearchInput()
        qtbot.addWidget(search_input)
        assert search_input._input.placeholderText() == "Search..."

    def test_search_input_instant_search(self, qtbot: QtBot) -> None:
        """Test instant search enabled."""
        search_input = SearchInput(instant_search=True)
        qtbot.addWidget(search_input)
        assert search_input._instant_search is True
        assert not search_input._search_btn.isVisible()

    def test_search_input_no_instant_search(self, qtbot: QtBot) -> None:
        """Test instant search disabled."""
        search_input = SearchInput(instant_search=False)
        qtbot.addWidget(search_input)
        search_input.show()
        assert search_input._instant_search is False
        assert search_input._search_btn.isVisible()

    def test_search_input_text_change(self, qtbot: QtBot) -> None:
        """Test search input text change."""
        search_input = SearchInput()
        qtbot.addWidget(search_input)

        with qtbot.waitSignal(search_input.text_changed, timeout=1000) as blocker:
            search_input._input.setText("test")

        assert blocker.args == ["test"]

    def test_search_input_instant_search_trigger(self, qtbot: QtBot) -> None:
        """Test instant search triggers on text change."""
        search_input = SearchInput(instant_search=True)
        qtbot.addWidget(search_input)

        with qtbot.waitSignal(search_input.search_triggered, timeout=1000) as blocker:
            search_input._input.setText("query")

        assert blocker.args == ["query"]

    def test_search_input_return_press(self, qtbot: QtBot) -> None:
        """Test search triggered on return press."""
        search_input = SearchInput(instant_search=False)
        qtbot.addWidget(search_input)

        search_input._input.setText("search query")

        with qtbot.waitSignal(search_input.search_triggered, timeout=1000) as blocker:
            search_input._input.returnPressed.emit()

        assert blocker.args == ["search query"]

    def test_search_button_click(self, qtbot: QtBot) -> None:
        """Test search triggered on button click."""
        search_input = SearchInput(instant_search=False)
        qtbot.addWidget(search_input)

        search_input._input.setText("button search")

        with qtbot.waitSignal(search_input.search_triggered, timeout=1000) as blocker:
            search_input._search_btn.click()

        assert blocker.args == ["button search"]

    def test_clear_button_visibility(self, qtbot: QtBot) -> None:
        """Test clear button visibility."""
        search_input = SearchInput()
        qtbot.addWidget(search_input)
        search_input.show()

        assert not search_input._clear_btn.isVisible()

        search_input._input.setText("text")
        assert search_input._clear_btn.isVisible()

    def test_clear_search(self, qtbot: QtBot) -> None:
        """Test clearing search."""
        search_input = SearchInput()
        qtbot.addWidget(search_input)

        search_input._input.setText("test")

        with qtbot.waitSignal(search_input.cleared, timeout=1000):
            search_input.clear()

        assert search_input.text() == ""

    def test_setText(self, qtbot: QtBot) -> None:
        """Test setting text programmatically."""
        search_input = SearchInput()
        qtbot.addWidget(search_input)

        search_input.setText("programmatic text")
        assert search_input.text() == "programmatic text"

    def test_setFocus_no_reason(self, qtbot: QtBot) -> None:
        """Test setting focus without reason."""
        search_input = SearchInput()
        qtbot.addWidget(search_input)
        search_input.show()
        qtbot.waitExposed(search_input)

        search_input.setFocus()
        # Just verify setFocus was called without error
        assert True

    def test_setFocus_with_reason(self, qtbot: QtBot) -> None:
        """Test setting focus with reason."""
        search_input = SearchInput()
        qtbot.addWidget(search_input)
        search_input.show()
        qtbot.waitExposed(search_input)

        search_input.setFocus(Qt.FocusReason.TabFocusReason)
        # Just verify setFocus was called without error
        assert True

    def test_setFocus_invalid_reason(self, qtbot: QtBot) -> None:
        """Test setting focus with invalid reason raises error."""
        search_input = SearchInput()
        qtbot.addWidget(search_input)

        try:
            search_input.setFocus("invalid")  # type: ignore
            assert False, "Should have raised TypeError"
        except TypeError as e:
            assert "Qt.FocusReason" in str(e)


class TestTextArea:
    """Test TextArea widget."""

    def test_textarea_creation_default(self, qtbot: QtBot) -> None:
        """Test creating text area with defaults."""
        textarea = TextArea()
        qtbot.addWidget(textarea)
        assert textarea.toPlainText() == ""
        assert not textarea.isReadOnly()

    def test_textarea_creation_with_placeholder(self, qtbot: QtBot) -> None:
        """Test creating text area with placeholder."""
        textarea = TextArea(placeholder="Enter description")
        qtbot.addWidget(textarea)
        assert textarea.placeholderText() == "Enter description"

    def test_textarea_creation_with_value(self, qtbot: QtBot) -> None:
        """Test creating text area with initial value."""
        textarea = TextArea()
        qtbot.addWidget(textarea)
        textarea.setPlainText("initial content")
        assert textarea.toPlainText() == "initial content"

    def test_textarea_creation_readonly(self, qtbot: QtBot) -> None:
        """Test creating readonly text area."""
        textarea = TextArea(read_only=True)
        qtbot.addWidget(textarea)
        assert textarea.isReadOnly() is True

    def test_textarea_creation_with_object_name(self, qtbot: QtBot) -> None:
        """Test creating text area with object name."""
        textarea = TextArea(object_name="test_textarea")
        qtbot.addWidget(textarea)
        assert textarea.objectName() == "test_textarea"

    def test_textarea_max_length(self, qtbot: QtBot) -> None:
        """Test text area with max length."""
        textarea = TextArea(max_length=10)
        qtbot.addWidget(textarea)
        assert textarea._max_length == 10

    def test_textarea_set_text_respects_max_length(self, qtbot: QtBot) -> None:
        """Test setting text respects max length."""
        textarea = TextArea(max_length=10)
        qtbot.addWidget(textarea)

        textarea.setPlainText("This is a very long text that exceeds limit")
        assert len(textarea.toPlainText()) == 10

    def test_textarea_enforce_max_length_on_typing(self, qtbot: QtBot) -> None:
        """Test max length enforcement while typing."""
        textarea = TextArea(max_length=5)
        qtbot.addWidget(textarea)

        textarea.setPlainText("test")
        assert len(textarea.toPlainText()) == 4

        # Try to add more text
        textarea.setPlainText("testing")
        assert len(textarea.toPlainText()) == 5


class TestInputIntegration:
    """Test Input widget integration scenarios."""

    def test_input_with_multiple_validators(self, qtbot: QtBot) -> None:
        """Test input with multiple validators."""
        validators = ValidatorChain([
            RequiredValidator(),
            EmailValidator(),
        ])
        input_widget = Input(validators=validators)
        qtbot.addWidget(input_widget)

        # Empty - fails required
        result = input_widget.validate()
        assert not result.is_valid

        # Invalid email - fails email validation
        input_widget.setText("not-an-email")
        result = input_widget.validate()
        assert not result.is_valid

        # Valid email - passes all
        input_widget.setText("test@example.com")
        result = input_widget.validate()
        assert result.is_valid

    def test_input_validation_with_field_name(self, qtbot: QtBot) -> None:
        """Test validation with custom field name."""
        validators = ValidatorChain([RequiredValidator()])
        input_widget = Input(validators=validators, object_name="email_input")
        qtbot.addWidget(input_widget)

        result = input_widget.validate("email")
        assert not result.is_valid
        if result.errors:
            assert result.errors[0].field_name == "email"

    def test_password_input_validation(self, qtbot: QtBot) -> None:
        """Test password input with validation."""
        validators = ValidatorChain([
            RequiredValidator(),
            LengthValidator(min_length=8),
        ])
        password_input = PasswordInput()
        qtbot.addWidget(password_input)
        password_input.set_validators(validators)

        # Too short
        password_input.setText("short")
        result = password_input.validate()
        assert not result.is_valid

        # Valid
        password_input.setText("longenough")
        result = password_input.validate()
        assert result.is_valid

    def test_search_input_with_empty_text(self, qtbot: QtBot) -> None:
        """Test search input doesn't trigger on empty text."""
        search_input = SearchInput(instant_search=False)
        qtbot.addWidget(search_input)

        signals_received = []
        search_input.search_triggered.connect(lambda t: signals_received.append(t))

        # Click search with empty text - should not trigger
        search_input._search_btn.click()
        assert signals_received == []

        # Press return with empty text - should not trigger
        search_input._input.returnPressed.emit()
        assert signals_received == []
