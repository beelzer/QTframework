"""Advanced dialog components with i18n support."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from qtframework.i18n import get_i18n_manager, t


class InputDialog(QDialog):
    """Input dialog for getting user input with i18n support."""

    def __init__(
        self,
        title: str = None,
        label: str = None,
        value: str = "",
        parent: QWidget | None = None,
        translation_key_title: str = None,
        translation_key_label: str = None,
    ) -> None:
        """Initialize input dialog.

        Args:
            title: Dialog title (overrides translation)
            label: Input label (overrides translation)
            value: Default input value
            parent: Parent widget
            translation_key_title: Translation key for title
            translation_key_label: Translation key for label
        """
        super().__init__(parent)

        # Set title with translation support
        if title:
            self.setWindowTitle(title)
        elif translation_key_title:
            self.setWindowTitle(t(translation_key_title))
        else:
            self.setWindowTitle(t("dialog.input.title"))

        self.setModal(True)

        layout = QVBoxLayout(self)

        # Set label with translation support
        if label:
            label_text = label
        elif translation_key_label:
            label_text = t(translation_key_label)
        else:
            label_text = t("dialog.input.label")

        layout.addWidget(QLabel(label_text))

        self.input = QLineEdit(value)
        layout.addWidget(self.input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        # Translate button text if i18n manager is available
        manager = get_i18n_manager()
        if manager:
            ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
            cancel_button = buttons.button(QDialogButtonBox.StandardButton.Cancel)
            if ok_button:
                ok_button.setText(t("common.ok"))
            if cancel_button:
                cancel_button.setText(t("common.cancel"))

        layout.addWidget(buttons)

    def get_value(self) -> str:
        """Get input value."""
        return self.input.text()


class ConfirmDialog(QDialog):
    """Confirmation dialog with i18n support."""

    def __init__(
        self,
        title: str = None,
        message: str = None,
        parent: QWidget | None = None,
        translation_key_title: str = None,
        translation_key_message: str = None,
        **kwargs,
    ) -> None:
        """Initialize confirm dialog.

        Args:
            title: Dialog title (overrides translation)
            message: Confirmation message (overrides translation)
            parent: Parent widget
            translation_key_title: Translation key for title
            translation_key_message: Translation key for message
            **kwargs: Variables for translation interpolation
        """
        super().__init__(parent)

        # Set title with translation support
        if title:
            self.setWindowTitle(title)
        elif translation_key_title:
            self.setWindowTitle(t(translation_key_title, **kwargs))
        else:
            self.setWindowTitle(t("dialog.confirm.title"))

        self.setModal(True)

        layout = QVBoxLayout(self)

        # Set message with translation support
        if message:
            message_text = message
        elif translation_key_message:
            message_text = t(translation_key_message, **kwargs)
        else:
            message_text = t("dialog.confirm.message")

        layout.addWidget(QLabel(message_text))

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        # Translate button text if i18n manager is available
        manager = get_i18n_manager()
        if manager:
            yes_button = buttons.button(QDialogButtonBox.StandardButton.Yes)
            no_button = buttons.button(QDialogButtonBox.StandardButton.No)
            if yes_button:
                yes_button.setText(t("common.yes"))
            if no_button:
                no_button.setText(t("common.no"))

        layout.addWidget(buttons)


class ProgressDialog(QDialog):
    """Progress dialog with progress bar and i18n support."""

    canceled = Signal()

    def __init__(
        self,
        title: str = None,
        label: str = None,
        maximum: int = 100,
        parent: QWidget | None = None,
        translation_key_title: str = None,
        translation_key_label: str = None,
    ) -> None:
        """Initialize progress dialog.

        Args:
            title: Dialog title (overrides translation)
            label: Progress label (overrides translation)
            maximum: Maximum progress value
            parent: Parent widget
            translation_key_title: Translation key for title
            translation_key_label: Translation key for label
        """
        super().__init__(parent)

        # Set title with translation support
        if title:
            self.setWindowTitle(title)
        elif translation_key_title:
            self.setWindowTitle(t(translation_key_title))
        else:
            self.setWindowTitle(t("dialog.progress.title"))

        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout(self)

        # Set label with translation support
        if label:
            label_text = label
        elif translation_key_label:
            label_text = t(translation_key_label)
        else:
            label_text = t("dialog.progress.label")

        self.label = QLabel(label_text)
        layout.addWidget(self.label)

        self.progress = QProgressBar()
        self.progress.setMaximum(maximum)
        layout.addWidget(self.progress)

        self.cancel_btn = QPushButton(t("common.cancel"))
        self.cancel_btn.clicked.connect(self._on_cancel)
        layout.addWidget(self.cancel_btn)

        # Update button text when locale changes
        manager = get_i18n_manager()
        if manager:
            manager.locale_changed.connect(self._update_translations)

    def set_value(self, value: int) -> None:
        """Set progress value."""
        self.progress.setValue(value)

    def set_label(self, text: str) -> None:
        """Set label text."""
        self.label.setText(text)

    def _on_cancel(self) -> None:
        """Handle cancel."""
        self.canceled.emit()
        self.reject()

    def _update_translations(self) -> None:
        """Update button text on locale change."""
        self.cancel_btn.setText(t("common.cancel"))


class FormDialog(QDialog):
    """Form dialog for structured input with i18n support."""

    def __init__(
        self,
        title: str = None,
        fields: list[tuple[str, str]] | None = None,
        parent: QWidget | None = None,
        translation_key_title: str = None,
        field_translation_keys: list[tuple[str, str]] | None = None,
    ) -> None:
        """Initialize form dialog.

        Args:
            title: Dialog title (overrides translation)
            fields: List of (label, default_value) tuples
            parent: Parent widget
            translation_key_title: Translation key for title
            field_translation_keys: List of (translation_key, default_value) tuples
        """
        super().__init__(parent)

        # Set title with translation support
        if title:
            self.setWindowTitle(title)
        elif translation_key_title:
            self.setWindowTitle(t(translation_key_title))
        else:
            self.setWindowTitle(t("dialog.form.title"))

        self.setModal(True)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.inputs: dict[str, QLineEdit] = {}
        self._field_keys: dict[str, str] = {}

        # Use translated fields if provided
        if field_translation_keys:
            for trans_key, default in field_translation_keys:
                label = t(trans_key)
                input_field = QLineEdit(default)
                form_layout.addRow(label, input_field)
                self.inputs[label] = input_field
                self._field_keys[label] = trans_key
        elif fields:
            for label, default in fields:
                input_field = QLineEdit(default)
                form_layout.addRow(label, input_field)
                self.inputs[label] = input_field

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        # Translate button text if i18n manager is available
        manager = get_i18n_manager()
        if manager:
            ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
            cancel_button = buttons.button(QDialogButtonBox.StandardButton.Cancel)
            if ok_button:
                ok_button.setText(t("common.ok"))
            if cancel_button:
                cancel_button.setText(t("common.cancel"))

            # Update form labels on locale change
            if self._field_keys:
                manager.locale_changed.connect(self._update_field_labels)

        layout.addWidget(buttons)

    def get_values(self) -> dict[str, str]:
        """Get form values."""
        return {label: input.text() for label, input in self.inputs.items()}

    def _update_field_labels(self) -> None:
        """Update field labels on locale change."""
        # This would require rebuilding the form layout
        # For now, dialogs are typically short-lived so this is less critical


def show_error_dialog(
    parent: QWidget | None = None,
    title: str | None = None,
    message: str | None = None,
    translation_key_title: str = "dialog.error.title",
    translation_key_message: str = "dialog.error.generic",
    **kwargs,
) -> None:
    """Show an error dialog with i18n support.

    Args:
        parent: Parent widget
        title: Dialog title (overrides translation)
        message: Error message (overrides translation)
        translation_key_title: Translation key for title
        translation_key_message: Translation key for message
        **kwargs: Variables for translation interpolation
    """
    from PySide6.QtWidgets import QMessageBox

    title_text = title if title else t(translation_key_title)
    message_text = message if message else t(translation_key_message, **kwargs)

    QMessageBox.critical(parent, title_text, message_text)


def show_warning_dialog(
    parent: QWidget | None = None,
    title: str | None = None,
    message: str | None = None,
    translation_key_title: str = "common.warning",
    translation_key_message: str = None,
    **kwargs,
) -> None:
    """Show a warning dialog with i18n support."""
    from PySide6.QtWidgets import QMessageBox

    title_text = title if title else t(translation_key_title)

    if message:
        message_text = message
    elif translation_key_message:
        message_text = t(translation_key_message, **kwargs)
    else:
        message_text = ""

    QMessageBox.warning(parent, title_text, message_text)


def show_info_dialog(
    parent: QWidget | None = None,
    title: str | None = None,
    message: str | None = None,
    translation_key_title: str = "common.info",
    translation_key_message: str = None,
    **kwargs,
) -> None:
    """Show an information dialog with i18n support."""
    from PySide6.QtWidgets import QMessageBox

    title_text = title if title else t(translation_key_title)

    if message:
        message_text = message
    elif translation_key_message:
        message_text = t(translation_key_message, **kwargs)
    else:
        message_text = ""

    QMessageBox.information(parent, title_text, message_text)


__all__ = [
    "InputDialog",
    "ConfirmDialog",
    "ProgressDialog",
    "FormDialog",
    "show_error_dialog",
    "show_warning_dialog",
    "show_info_dialog",
]
