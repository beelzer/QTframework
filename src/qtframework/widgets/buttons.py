"""Button widget components."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from PySide6.QtCore import Property, QSize, Qt, Signal
from PySide6.QtWidgets import QPushButton


if TYPE_CHECKING:
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QWidget


class ButtonVariant(Enum):
    """Button variant styles."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"
    OUTLINE = "outline"
    TEXT = "text"


class ButtonSize(Enum):
    """Button size options.

    COMPACT: Matches input field height, ideal for buttons next to QLineEdit/QComboBox
    SMALL: Small standalone button (28px height)
    MEDIUM: Default button size (36px height)
    LARGE: Large emphasis button (44px height)
    """

    COMPACT = "compact"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class Button(QPushButton):
    """Enhanced button widget."""

    variant_changed = Signal(str)
    size_changed = Signal(str)

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        variant: ButtonVariant = ButtonVariant.PRIMARY,
        size: ButtonSize = ButtonSize.MEDIUM,
        icon: QIcon | None = None,
        object_name: str | None = None,
    ) -> None:
        """Initialize button.

        Args:
            text: Button text
            parent: Parent widget
            variant: Button variant
            size: Button size
            icon: Button icon
            object_name: Object name for styling
        """
        super().__init__(text, parent)

        if object_name:
            self.setObjectName(object_name)

        self._variant = variant
        self._size = size

        if icon:
            from PySide6.QtGui import QIcon as QIconClass

            if isinstance(icon, QIconClass):
                self.setIcon(icon)

        self._apply_variant()
        self._apply_size()

    def _get_variant(self) -> str:
        """Get button variant.

        Returns:
            Variant name
        """
        return self._variant.value

    def _set_variant(self, value: str) -> None:
        """Set button variant.

        Args:
            value: Variant name
        """
        try:
            variant = ButtonVariant(value)
            if self._variant != variant:
                self._variant = variant
                self._apply_variant()
                self.variant_changed.emit(value)
        except ValueError:
            pass

    variant = Property(str, _get_variant, _set_variant)

    def _get_size(self) -> str:
        """Get button size.

        Returns:
            Size name
        """
        return self._size.value

    def _set_size(self, value: str) -> None:
        """Set button size.

        Args:
            value: Size name
        """
        try:
            size = ButtonSize(value)
            if self._size != size:
                self._size = size
                self._apply_size()
                self.size_changed.emit(value)
        except ValueError:
            pass

    buttonSize = Property(str, _get_size, _set_size)  # noqa: N815

    def _apply_variant(self) -> None:
        """Apply variant styling."""
        self.setProperty("variant", self._variant.value)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _apply_size(self) -> None:
        """Apply size styling."""
        self.setProperty("size", self._size.value)

        if self._size == ButtonSize.COMPACT:
            # Match input field height with minimal padding
            # Uses same vertical padding as QLineEdit (6px) with no min-height
            self.setStyleSheet("padding: 6px 8px; min-height: 0px;")
            self.setMinimumWidth(60)
        else:
            size_map = {
                ButtonSize.SMALL: (80, 28),
                ButtonSize.MEDIUM: (100, 36),
                ButtonSize.LARGE: (120, 44),
            }
            min_width, height = size_map[self._size]
            self.setMinimumWidth(min_width)
            self.setFixedHeight(height)

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class IconButton(QPushButton):
    """Icon-only button widget."""

    def __init__(
        self,
        icon: QIcon,
        parent: QWidget | None = None,
        *,
        size: QSize | None = None,
        tooltip: str = "",
        object_name: str | None = None,
    ) -> None:
        """Initialize icon button.

        Args:
            icon: Button icon
            parent: Parent widget
            size: Icon size
            tooltip: Tooltip text
            object_name: Object name for styling
        """
        super().__init__(parent)

        if object_name:
            self.setObjectName(object_name)

        self.setIcon(icon)
        self.setFlat(True)

        size = size or QSize(32, 32)
        self.setIconSize(size)
        self.setFixedSize(size.width() + 8, size.height() + 8)

        if tooltip:
            self.setToolTip(tooltip)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("class", "icon-button")


class CloseButton(QPushButton):
    """Standardized close button widget."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        size: int = 20,
        style: str = "default",
    ) -> None:
        """Initialize close button.

        Args:
            parent: Parent widget
            size: Button size in pixels
            style: Button style ('default', 'light', 'dark')
        """
        super().__init__("×", parent)

        self.setFixedSize(size, size)
        self.setFlat(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("class", "close-button")
        self.setProperty("style", style)

        # Apply inline styles based on style parameter
        # Style will be applied through theme system
        # Keep minimal styles that won't conflict with theme
        self.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        # default style will use theme stylesheet


class ToggleButton(QPushButton):
    """Toggle button widget."""

    toggled_on = Signal()
    toggled_off = Signal()

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        checked: bool = False,
        on_text: str | None = None,
        off_text: str | None = None,
        object_name: str | None = None,
    ) -> None:
        """Initialize toggle button.

        Args:
            text: Button text
            parent: Parent widget
            checked: Initial checked state
            on_text: Text when toggled on
            off_text: Text when toggled off
            object_name: Object name for styling
        """
        super().__init__(text, parent)

        if object_name:
            self.setObjectName(object_name)

        self._on_text = on_text or text
        self._off_text = off_text or text

        self.setCheckable(True)
        self.toggled.connect(self._on_toggled)
        self.setProperty("class", "toggle-button")

        self.setChecked(checked)  # Set checked last, after attributes are initialized

    def _on_toggled(self, checked: bool) -> None:
        """Handle toggle state change.

        Args:
            checked: New checked state
        """
        self._update_text()
        if checked:
            self.toggled_on.emit()
        else:
            self.toggled_off.emit()

    def _update_text(self) -> None:
        """Update button text based on state."""
        if self.isChecked():
            self.setText(self._on_text)
        else:
            self.setText(self._off_text)

    def setChecked(self, checked: bool) -> None:
        """Set checked state.

        Args:
            checked: Checked state
        """
        super().setChecked(checked)
        self._update_text()
