"""Base widget class."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Property, Signal
from PySide6.QtWidgets import QWidget


class Widget(QWidget):
    """Enhanced base widget with framework integration."""

    style_changed = Signal()

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        object_name: str | None = None,
        style_class: str | None = None,
    ) -> None:
        """Initialize widget.

        Args:
            parent: Parent widget
            object_name: Object name for styling
            style_class: CSS-like class for styling
        """
        super().__init__(parent)

        if object_name:
            self.setObjectName(object_name)

        self._style_class = style_class or ""
        if self._style_class:
            self.setProperty("class", self._style_class)

        self._custom_properties: dict[str, Any] = {}

    @Property(str, notify=style_changed)
    def styleClass(self) -> str:  # noqa: N802
        """Get style class.

        Returns:
            Style class name
        """
        return self._style_class

    @styleClass.setter
    def styleClass(self, value: str) -> None:  # noqa: N802
        """Set style class.

        Args:
            value: Style class name
        """
        if self._style_class != value:
            self._style_class = value
            self.setProperty("class", value)
            self.style_changed.emit()
            self.style().unpolish(self)
            self.style().polish(self)
            self.update()

    def add_style_class(self, class_name: str) -> None:
        """Add a style class.

        Args:
            class_name: Class name to add
        """
        classes = self._style_class.split() if self._style_class else []
        if class_name not in classes:
            classes.append(class_name)
            self.styleClass = " ".join(classes)

    def remove_style_class(self, class_name: str) -> None:
        """Remove a style class.

        Args:
            class_name: Class name to remove
        """
        classes = self._style_class.split() if self._style_class else []
        if class_name in classes:
            classes.remove(class_name)
            self.styleClass = " ".join(classes)

    def toggle_style_class(self, class_name: str) -> None:
        """Toggle a style class.

        Args:
            class_name: Class name to toggle
        """
        classes = self._style_class.split() if self._style_class else []
        if class_name in classes:
            classes.remove(class_name)
        else:
            classes.append(class_name)
        self.styleClass = " ".join(classes)

    def has_style_class(self, class_name: str) -> bool:
        """Check if widget has a style class.

        Args:
            class_name: Class name to check

        Returns:
            True if class is present
        """
        classes = self._style_class.split() if self._style_class else []
        return class_name in classes

    def set_custom_property(self, name: str, value: Any) -> None:
        """Set a custom property.

        Args:
            name: Property name
            value: Property value
        """
        self._custom_properties[name] = value
        self.setProperty(name, value)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def get_custom_property(self, name: str, default: Any = None) -> Any:
        """Get a custom property.

        Args:
            name: Property name
            default: Default value

        Returns:
            Property value or default
        """
        return self._custom_properties.get(name, default)

    def get_application(self) -> Any | None:
        """Get the application instance.

        Returns:
            Application instance or None
        """
        from PySide6.QtWidgets import QApplication

        from qtframework.core.application import Application

        app = QApplication.instance()
        if isinstance(app, Application):
            return app
        return None
