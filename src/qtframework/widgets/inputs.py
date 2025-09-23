"""Input widget components."""

from __future__ import annotations

from typing import Any, override

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QWidget

from qtframework.widgets.base import Widget
from qtframework.widgets.buttons import CloseButton


class Input(QLineEdit):
    """Enhanced input widget."""

    validation_changed = Signal(bool)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        placeholder: str = "",
        value: str = "",
        read_only: bool = False,
        max_length: int | None = None,
        object_name: str | None = None,
    ) -> None:
        """Initialize input.

        Args:
            parent: Parent widget
            placeholder: Placeholder text
            value: Initial value
            read_only: Read-only state
            max_length: Maximum length
            object_name: Object name for styling
        """
        super().__init__(parent)

        if object_name:
            self.setObjectName(object_name)

        if placeholder:
            self.setPlaceholderText(placeholder)
        if value:
            self.setText(value)
        if read_only:
            self.setReadOnly(read_only)
        if max_length:
            self.setMaxLength(max_length)

        self._validation_error = False
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text: str) -> None:
        """Handle text change.

        Args:
            text: New text value
        """
        self.validate()

    def validate(self) -> bool:
        """Validate input.

        Returns:
            True if valid
        """
        return True

    def set_validation_error(self, error: bool) -> None:
        """Set validation error state.

        Args:
            error: Error state
        """
        if self._validation_error != error:
            self._validation_error = error
            self.setProperty("error", error)
            self.style().unpolish(self)
            self.style().polish(self)
            self.update()
            self.validation_changed.emit(error)

    @property
    def validation_error(self) -> bool:
        """Get validation error state.

        Returns:
            Error state
        """
        return self._validation_error

    def set_icon(self, icon: QIcon, position: str = "left") -> None:
        """Set input icon.

        Args:
            icon: Icon to display
            position: Icon position (left or right)
        """
        action = self.addAction(
            icon,
            QLineEdit.ActionPosition.LeadingPosition
            if position == "left"
            else QLineEdit.ActionPosition.TrailingPosition,
        )
        action.setEnabled(False)


class PasswordInput(Input):
    """Password input widget."""

    visibility_changed = Signal(bool)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        placeholder: str = "Enter password",
        show_toggle: bool = True,
        object_name: str | None = None,
    ) -> None:
        """Initialize password input.

        Args:
            parent: Parent widget
            placeholder: Placeholder text
            show_toggle: Show visibility toggle
            object_name: Object name for styling
        """
        super().__init__(
            parent,
            placeholder=placeholder,
            object_name=object_name,
        )

        self.setEchoMode(QLineEdit.EchoMode.Password)
        self._visible = False

        if show_toggle:
            self._add_visibility_toggle()

    def _add_visibility_toggle(self) -> None:
        """Add visibility toggle button."""
        action = self.addAction(
            QIcon(),
            QLineEdit.ActionPosition.TrailingPosition,
        )
        action.triggered.connect(self.toggle_visibility)
        self._update_visibility_icon(action)

    def toggle_visibility(self) -> None:
        """Toggle password visibility."""
        self._visible = not self._visible
        self.setEchoMode(
            QLineEdit.EchoMode.Normal if self._visible else QLineEdit.EchoMode.Password
        )
        self.visibility_changed.emit(self._visible)

        for action in self.actions():
            self._update_visibility_icon(action)

    def _update_visibility_icon(self, action: Any) -> None:
        """Update visibility icon.

        Args:
            action: QAction to update
        """


class SearchInput(Widget):
    """Search input widget."""

    search_triggered = Signal(str)
    text_changed = Signal(str)
    cleared = Signal()

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        placeholder: str = "Search...",
        instant_search: bool = True,
        object_name: str | None = None,
    ) -> None:
        """Initialize search input.

        Args:
            parent: Parent widget
            placeholder: Placeholder text
            instant_search: Enable instant search
            object_name: Object name for styling
        """
        super().__init__(parent, object_name=object_name)

        self._instant_search = instant_search
        self._setup_ui(placeholder)
        self._connect_signals()

    def _setup_ui(self, placeholder: str) -> None:
        """Setup UI components.

        Args:
            placeholder: Placeholder text
        """
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._input = QLineEdit()
        self._input.setPlaceholderText(placeholder)

        self._search_btn = QPushButton("Search")
        self._search_btn.setVisible(not self._instant_search)

        self._clear_btn = CloseButton(size=24, style="default")
        self._clear_btn.setVisible(False)
        self._clear_btn.setFlat(True)

        layout.addWidget(self._input)
        layout.addWidget(self._clear_btn)
        layout.addWidget(self._search_btn)

        self.setProperty("class", "search-input")

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        self._input.textChanged.connect(self._on_text_changed)
        self._input.returnPressed.connect(self._on_return_pressed)
        self._search_btn.clicked.connect(self._on_search_clicked)
        self._clear_btn.clicked.connect(self.clear)

    def _on_text_changed(self, text: str) -> None:
        """Handle text change.

        Args:
            text: New text value
        """
        self._clear_btn.setVisible(bool(text))
        self.text_changed.emit(text)

        if self._instant_search and text:
            self.search_triggered.emit(text)

    def _on_return_pressed(self) -> None:
        """Handle return key press."""
        text = self._input.text()
        if text:
            self.search_triggered.emit(text)

    def _on_search_clicked(self) -> None:
        """Handle search button click."""
        text = self._input.text()
        if text:
            self.search_triggered.emit(text)

    def text(self) -> str:
        """Get search text.

        Returns:
            Search text
        """
        return self._input.text()

    def setText(self, text: str) -> None:  # noqa: N802
        """Set search text.

        Args:
            text: Text to set
        """
        self._input.setText(text)

    def clear(self) -> None:
        """Clear search input."""
        self._input.clear()
        self.cleared.emit()

    def setFocus(self) -> None:  # noqa: N802
        """Set focus to input."""
        self._input.setFocus()


class TextArea(QTextEdit):
    """Enhanced text area widget."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        placeholder: str = "",
        value: str = "",
        read_only: bool = False,
        max_length: int | None = None,
        object_name: str | None = None,
    ) -> None:
        """Initialize text area.

        Args:
            parent: Parent widget
            placeholder: Placeholder text
            value: Initial value
            read_only: Read-only state
            max_length: Maximum length
            object_name: Object name for styling
        """
        super().__init__(parent)

        if object_name:
            self.setObjectName(object_name)

        if placeholder:
            self.setPlaceholderText(placeholder)
        if value:
            self.setPlainText(value)
        if read_only:
            self.setReadOnly(read_only)

        self._max_length = max_length
        if max_length:
            self.textChanged.connect(self._enforce_max_length)

    def _enforce_max_length(self) -> None:
        """Enforce maximum length."""
        if self._max_length and len(self.toPlainText()) > self._max_length:
            cursor = self.textCursor()
            cursor.deletePreviousChar()

    @override
    def setPlainText(self, text: str) -> None:
        """Set plain text.

        Args:
            text: Text to set
        """
        if self._max_length:
            text = text[: self._max_length]
        super().setPlainText(text)
