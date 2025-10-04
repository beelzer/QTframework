"""Layout container widgets.

This module provides convenient layout container widgets that wrap Qt's layout
managers with a more intuitive API and framework integration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout

from qtframework.widgets.base import Widget


if TYPE_CHECKING:
    from PySide6.QtWidgets import QLayout, QWidget


class VBox(Widget):
    """Vertical box layout container.

    A convenience widget that wraps QVBoxLayout with a simplified API.
    Provides automatic widget management and cleaner syntax for vertical layouts.

    Args:
        spacing: Space between widgets in pixels (default: 0)
        margins: Margins around the layout (left, top, right, bottom).
                 Can be a single int for uniform margins or tuple of 4 ints.
                 Default: (0, 0, 0, 0)
        alignment: Default alignment for widgets
        parent: Parent widget

    Example:
        >>> from qtframework.widgets import VBox, Button
        >>> layout = VBox(spacing=8, margins=16)
        >>> layout.add_widget(Button("First"))
        >>> layout.add_widget(Button("Second"))
        >>> layout.add_stretch()
    """

    def __init__(
        self,
        *,
        spacing: int = 0,
        margins: int | tuple[int, int, int, int] = 0,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignTop,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the VBox layout container."""
        super().__init__(parent=parent)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(spacing)

        # Set margins
        if isinstance(margins, int):
            self._layout.setContentsMargins(margins, margins, margins, margins)
        else:
            self._layout.setContentsMargins(*margins)

        self._layout.setAlignment(alignment)

    @property
    def layout(self) -> QVBoxLayout:
        """Get the underlying QVBoxLayout."""
        return self._layout

    def add_widget(
        self,
        widget: QWidget,
        stretch: int = 0,
        alignment: Qt.AlignmentFlag | None = None,
    ) -> None:
        """Add a widget to the layout.

        Args:
            widget: Widget to add
            stretch: Stretch factor for this widget (default: 0)
            alignment: Alignment for this widget (overrides default)
        """
        if alignment is not None:
            self._layout.addWidget(widget, stretch, alignment)
        else:
            self._layout.addWidget(widget, stretch)

    def add_layout(self, layout: QLayout, stretch: int = 0) -> None:
        """Add a layout to this layout.

        Args:
            layout: Layout to add
            stretch: Stretch factor for this layout (default: 0)
        """
        self._layout.addLayout(layout, stretch)

    def add_stretch(self, stretch: int = 1) -> None:
        """Add stretchable space to the layout.

        Args:
            stretch: Stretch factor (default: 1)
        """
        self._layout.addStretch(stretch)

    def add_spacing(self, size: int) -> None:
        """Add fixed spacing to the layout.

        Args:
            size: Size of spacing in pixels
        """
        self._layout.addSpacing(size)

    def insert_widget(
        self,
        index: int,
        widget: QWidget,
        stretch: int = 0,
        alignment: Qt.AlignmentFlag | None = None,
    ) -> None:
        """Insert a widget at a specific position.

        Args:
            index: Position to insert at
            widget: Widget to insert
            stretch: Stretch factor for this widget (default: 0)
            alignment: Alignment for this widget
        """
        if alignment is not None:
            self._layout.insertWidget(index, widget, stretch, alignment)
        else:
            self._layout.insertWidget(index, widget, stretch)

    def remove_widget(self, widget: QWidget) -> None:
        """Remove a widget from the layout.

        Args:
            widget: Widget to remove
        """
        self._layout.removeWidget(widget)

    def clear(self) -> None:
        """Remove all widgets from the layout."""
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def set_spacing(self, spacing: int) -> None:
        """Set spacing between widgets.

        Args:
            spacing: Space between widgets in pixels
        """
        self._layout.setSpacing(spacing)

    def set_margins(self, *args: int) -> None:
        """Set layout margins.

        Args:
            *args: Either 1 int (uniform) or 4 ints (left, top, right, bottom)
        """
        if len(args) == 1:
            self._layout.setContentsMargins(args[0], args[0], args[0], args[0])
        elif len(args) == 4:
            self._layout.setContentsMargins(*args)
        else:
            raise ValueError("Expected 1 or 4 arguments for margins")


class HBox(Widget):
    """Horizontal box layout container.

    A convenience widget that wraps QHBoxLayout with a simplified API.
    Provides automatic widget management and cleaner syntax for horizontal layouts.

    Args:
        spacing: Space between widgets in pixels (default: 0)
        margins: Margins around the layout (left, top, right, bottom).
                 Can be a single int for uniform margins or tuple of 4 ints.
                 Default: (0, 0, 0, 0)
        alignment: Default alignment for widgets
        parent: Parent widget

    Example:
        >>> from qtframework.widgets import HBox, Button
        >>> layout = HBox(spacing=8, margins=16)
        >>> layout.add_widget(Button("Left"))
        >>> layout.add_stretch()
        >>> layout.add_widget(Button("Right"))
    """

    def __init__(
        self,
        *,
        spacing: int = 0,
        margins: int | tuple[int, int, int, int] = 0,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the HBox layout container."""
        super().__init__(parent=parent)

        self._layout = QHBoxLayout(self)
        self._layout.setSpacing(spacing)

        # Set margins
        if isinstance(margins, int):
            self._layout.setContentsMargins(margins, margins, margins, margins)
        else:
            self._layout.setContentsMargins(*margins)

        self._layout.setAlignment(alignment)

    @property
    def layout(self) -> QHBoxLayout:
        """Get the underlying QHBoxLayout."""
        return self._layout

    def add_widget(
        self,
        widget: QWidget,
        stretch: int = 0,
        alignment: Qt.AlignmentFlag | None = None,
    ) -> None:
        """Add a widget to the layout.

        Args:
            widget: Widget to add
            stretch: Stretch factor for this widget (default: 0)
            alignment: Alignment for this widget (overrides default)
        """
        if alignment is not None:
            self._layout.addWidget(widget, stretch, alignment)
        else:
            self._layout.addWidget(widget, stretch)

    def add_layout(self, layout: QLayout, stretch: int = 0) -> None:
        """Add a layout to this layout.

        Args:
            layout: Layout to add
            stretch: Stretch factor for this layout (default: 0)
        """
        self._layout.addLayout(layout, stretch)

    def add_stretch(self, stretch: int = 1) -> None:
        """Add stretchable space to the layout.

        Args:
            stretch: Stretch factor (default: 1)
        """
        self._layout.addStretch(stretch)

    def add_spacing(self, size: int) -> None:
        """Add fixed spacing to the layout.

        Args:
            size: Size of spacing in pixels
        """
        self._layout.addSpacing(size)

    def insert_widget(
        self,
        index: int,
        widget: QWidget,
        stretch: int = 0,
        alignment: Qt.AlignmentFlag | None = None,
    ) -> None:
        """Insert a widget at a specific position.

        Args:
            index: Position to insert at
            widget: Widget to insert
            stretch: Stretch factor for this widget (default: 0)
            alignment: Alignment for this widget
        """
        if alignment is not None:
            self._layout.insertWidget(index, widget, stretch, alignment)
        else:
            self._layout.insertWidget(index, widget, stretch)

    def remove_widget(self, widget: QWidget) -> None:
        """Remove a widget from the layout.

        Args:
            widget: Widget to remove
        """
        self._layout.removeWidget(widget)

    def clear(self) -> None:
        """Remove all widgets from the layout."""
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def set_spacing(self, spacing: int) -> None:
        """Set spacing between widgets.

        Args:
            spacing: Space between widgets in pixels
        """
        self._layout.setSpacing(spacing)

    def set_margins(self, *args: int) -> None:
        """Set layout margins.

        Args:
            *args: Either 1 int (uniform) or 4 ints (left, top, right, bottom)
        """
        if len(args) == 1:
            self._layout.setContentsMargins(args[0], args[0], args[0], args[0])
        elif len(args) == 4:
            self._layout.setContentsMargins(*args)
        else:
            raise ValueError("Expected 1 or 4 arguments for margins")
