"""Base layout implementations."""

from __future__ import annotations

from enum import Enum

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QWidget
from PySide6.QtWidgets import QGridLayout as QtGridLayout


class Direction(Enum):
    """Layout direction."""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class Alignment(Enum):
    """Layout alignment."""

    START = "start"
    CENTER = "center"
    END = "end"
    STRETCH = "stretch"
    SPACE_BETWEEN = "space_between"
    SPACE_AROUND = "space_around"
    SPACE_EVENLY = "space_evenly"


class FlexLayout(QBoxLayout):
    """Flexible box layout."""

    def __init__(
        self,
        direction: Direction = Direction.HORIZONTAL,
        *,
        spacing: int = 8,
        margins: int | tuple[int, int, int, int] = 8,
        alignment: Alignment = Alignment.START,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize flex layout.

        Args:
            direction: Layout direction
            spacing: Spacing between items
            margins: Layout margins (single value or tuple of left, top, right, bottom)
            alignment: Layout alignment
            parent: Parent widget
        """
        super().__init__(
            QBoxLayout.Direction.LeftToRight
            if direction == Direction.HORIZONTAL
            else QBoxLayout.Direction.TopToBottom,
            parent,
        )

        self.setSpacing(spacing)

        if isinstance(margins, int):
            self.setContentsMargins(margins, margins, margins, margins)
        else:
            self.setContentsMargins(*margins)

        self._apply_alignment(alignment)

    def _apply_alignment(self, alignment: Alignment) -> None:
        """Apply alignment to layout.

        Args:
            alignment: Alignment to apply
        """
        if alignment == Alignment.START:
            self.setAlignment(
                Qt.AlignmentFlag.AlignLeft
                if self.direction() == QBoxLayout.Direction.LeftToRight
                else Qt.AlignmentFlag.AlignTop
            )
        elif alignment == Alignment.CENTER:
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        elif alignment == Alignment.END:
            self.setAlignment(
                Qt.AlignmentFlag.AlignRight
                if self.direction() == QBoxLayout.Direction.LeftToRight
                else Qt.AlignmentFlag.AlignBottom
            )
        elif alignment == Alignment.SPACE_BETWEEN:
            self.insertStretch(0)
            self.addStretch()
        elif alignment == Alignment.SPACE_AROUND:
            self.insertStretch(0)
            for i in range(self.count()):
                if i < self.count() - 1:
                    self.insertStretch(i * 2 + 1)
            self.addStretch()
        elif alignment == Alignment.SPACE_EVENLY:
            for i in range(self.count() + 1):
                self.insertStretch(i * 2)

    def add_widget(
        self,
        widget: QWidget,
        stretch: int = 0,
        alignment: Qt.AlignmentFlag | None = None,
    ) -> None:
        """Add widget to layout.

        Args:
            widget: Widget to add
            stretch: Stretch factor
            alignment: Widget alignment
        """
        if alignment:
            self.addWidget(widget, stretch, alignment)
        else:
            self.addWidget(widget, stretch)

    def add_spacing(self, size: int) -> None:
        """Add spacing to layout.

        Args:
            size: Spacing size
        """
        self.addSpacing(size)

    def add_stretch(self, stretch: int = 0) -> None:
        """Add stretch to layout.

        Args:
            stretch: Stretch factor
        """
        self.addStretch(stretch)


class GridLayout(QtGridLayout):
    """Enhanced grid layout."""

    def __init__(
        self,
        *,
        spacing: int = 8,
        margins: int | tuple[int, int, int, int] = 8,
        column_stretch: list[int] | None = None,
        row_stretch: list[int] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize grid layout.

        Args:
            spacing: Spacing between items
            margins: Layout margins
            column_stretch: Column stretch factors
            row_stretch: Row stretch factors
            parent: Parent widget
        """
        super().__init__(parent)

        self.setSpacing(spacing)

        if isinstance(margins, int):
            self.setContentsMargins(margins, margins, margins, margins)
        else:
            self.setContentsMargins(*margins)

        if column_stretch:
            for i, stretch in enumerate(column_stretch):
                self.setColumnStretch(i, stretch)

        if row_stretch:
            for i, stretch in enumerate(row_stretch):
                self.setRowStretch(i, stretch)

    def add_widget(
        self,
        widget: QWidget,
        row: int,
        column: int,
        row_span: int = 1,
        column_span: int = 1,
        alignment: Qt.AlignmentFlag | None = None,
    ) -> None:
        """Add widget to grid.

        Args:
            widget: Widget to add
            row: Row position
            column: Column position
            row_span: Number of rows to span
            column_span: Number of columns to span
            alignment: Widget alignment
        """
        if alignment:
            self.addWidget(widget, row, column, row_span, column_span, alignment)
        else:
            self.addWidget(widget, row, column, row_span, column_span)

    def set_column_stretch(self, column: int, stretch: int) -> None:
        """Set column stretch factor.

        Args:
            column: Column index
            stretch: Stretch factor
        """
        self.setColumnStretch(column, stretch)

    def set_row_stretch(self, row: int, stretch: int) -> None:
        """Set row stretch factor.

        Args:
            row: Row index
            stretch: Stretch factor
        """
        self.setRowStretch(row, stretch)

    def set_column_minimum_width(self, column: int, width: int) -> None:
        """Set column minimum width.

        Args:
            column: Column index
            width: Minimum width
        """
        self.setColumnMinimumWidth(column, width)

    def set_row_minimum_height(self, row: int, height: int) -> None:
        """Set row minimum height.

        Args:
            row: Row index
            height: Minimum height
        """
        self.setRowMinimumHeight(row, height)
