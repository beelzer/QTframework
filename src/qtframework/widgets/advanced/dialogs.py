"""Advanced dialog components."""

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


class InputDialog(QDialog):
    """Input dialog for getting user input."""

    def __init__(
        self,
        title: str = "Input",
        label: str = "Enter value:",
        value: str = "",
        parent: QWidget | None = None,
    ) -> None:
        """Initialize input dialog."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(label))

        self.input = QLineEdit(value)
        layout.addWidget(self.input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_value(self) -> str:
        """Get input value."""
        return self.input.text()


class ConfirmDialog(QDialog):
    """Confirmation dialog."""

    def __init__(
        self,
        title: str = "Confirm",
        message: str = "Are you sure?",
        parent: QWidget | None = None,
    ) -> None:
        """Initialize confirm dialog."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(message))

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class ProgressDialog(QDialog):
    """Progress dialog with progress bar."""

    canceled = Signal()

    def __init__(
        self,
        title: str = "Progress",
        label: str = "Processing...",
        maximum: int = 100,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize progress dialog."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout(self)

        self.label = QLabel(label)
        layout.addWidget(self.label)

        self.progress = QProgressBar()
        self.progress.setMaximum(maximum)
        layout.addWidget(self.progress)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._on_cancel)
        layout.addWidget(self.cancel_btn)

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


class FormDialog(QDialog):
    """Form dialog for structured input."""

    def __init__(
        self,
        title: str = "Form",
        fields: list[tuple[str, str]] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize form dialog.

        Args:
            title: Dialog title
            fields: List of (label, default_value) tuples
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.inputs: dict[str, QLineEdit] = {}

        for label, default in fields or []:
            input_field = QLineEdit(default)
            form_layout.addRow(label, input_field)
            self.inputs[label] = input_field

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_values(self) -> dict[str, str]:
        """Get form values."""
        return {label: input.text() for label, input in self.inputs.items()}
