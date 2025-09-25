"""Flow layout that automatically wraps widgets based on available width."""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout, QLayoutItem, QSizePolicy, QWidget


class FlowLayout(QLayout):
    """A layout that arranges widgets in a flowing manner, wrapping to new lines as needed."""

    def __init__(
        self,
        parent: QWidget | None = None,
        margin: int = -1,
        h_spacing: int = -1,
        v_spacing: int = -1,
    ):
        """Initialize the flow layout.

        Args:
            parent: Parent widget
            margin: Margin around the layout
            h_spacing: Horizontal spacing between widgets
            v_spacing: Vertical spacing between widgets
        """
        super().__init__(parent)
        self._item_list: list[QLayoutItem] = []
        self._h_space = h_spacing
        self._v_space = v_spacing

        if margin != -1:
            self.setContentsMargins(margin, margin, margin, margin)

    def __del__(self):
        """Clean up layout items."""
        while self._item_list:
            self.takeAt(0)

    def addItem(self, item: QLayoutItem) -> None:
        """Add an item to the layout."""
        self._item_list.append(item)

    def horizontalSpacing(self) -> int:
        """Get horizontal spacing between widgets."""
        if self._h_space >= 0:
            return self._h_space
        return self._smart_spacing(QSizePolicy.Horizontal)

    def verticalSpacing(self) -> int:
        """Get vertical spacing between widgets."""
        if self._v_space >= 0:
            return self._v_space
        return self._smart_spacing(QSizePolicy.Vertical)

    def count(self) -> int:
        """Return the number of items in the layout."""
        return len(self._item_list)

    def itemAt(self, index: int) -> QLayoutItem | None:
        """Return the item at the given index."""
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index: int) -> QLayoutItem | None:
        """Remove and return the item at the given index."""
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def expandingDirections(self) -> Qt.Orientation:
        """Return the expanding directions."""
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        """Return whether the layout has height for width."""
        return True

    def heightForWidth(self, width: int) -> int:
        """Calculate the height needed for a given width."""
        # Ensure we have valid width
        if width <= 0:
            return self.minimumSize().height()
        height = self._do_layout(QRect(0, 0, width, 0), test=True)
        return max(height, self.minimumSize().height())

    def setGeometry(self, rect: QRect) -> None:
        """Set the geometry of the layout."""
        super().setGeometry(rect)
        self._do_layout(rect, test=False)

    def invalidate(self) -> None:
        """Invalidate the layout to force recalculation."""
        super().invalidate()
        # Force immediate re-layout if we have a valid geometry
        if self.geometry().isValid():
            self._do_layout(self.geometry(), test=False)

    def sizeHint(self) -> QSize:
        """Return the preferred size of the layout."""
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        """Calculate the minimum size of the layout."""
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect: QRect, test: bool = False) -> int:
        """Perform the actual layout of items.

        Args:
            rect: The rectangle to layout within
            test: If True, don't actually move widgets, just calculate height

        Returns:
            The height used by the layout
        """
        margins = self.getContentsMargins()
        left: int = margins[0] if margins else 0
        top: int = margins[1] if margins else 0
        right: int = margins[2] if margins else 0
        bottom: int = margins[3] if margins else 0
        effective_rect = rect.adjusted(left, top, -right, -bottom)

        # Ensure we have a valid rect to work with
        if effective_rect.width() <= 0:
            # If we don't have a valid width yet, use parent's width if available
            if self.parent():
                effective_rect.setWidth(self.parent().width() - left - right)
            if effective_rect.width() <= 0:
                return 0  # Can't layout without valid width

        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0

        h_space = self.horizontalSpacing()
        v_space = self.verticalSpacing()

        for item in self._item_list:
            widget = item.widget()
            if widget and not widget.isVisible():
                continue

            space_x = h_space
            space_y = v_space

            item_size = item.sizeHint()
            next_x = x + item_size.width() + space_x

            if next_x - space_x > effective_rect.right() and line_height > 0:
                # Start a new line
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item_size.width() + space_x
                line_height = 0

            if not test:
                item.setGeometry(QRect(QPoint(x, y), item_size))
                # Ensure the widget is shown and properly updated
                if widget:
                    widget.show()
                    widget.raise_()

            x = next_x
            line_height = max(line_height, item_size.height())

        return y + line_height - rect.y() + bottom

    def _smart_spacing(self, orientation: QSizePolicy.ControlType) -> int:
        """Calculate smart spacing based on parent widget style."""
        parent = self.parent()
        if not parent:
            return -1

        if orientation == QSizePolicy.Horizontal:
            return parent.style().pixelMetric(
                parent.style().PM_LayoutHorizontalSpacing, None, parent
            )
        return parent.style().pixelMetric(parent.style().PM_LayoutVerticalSpacing, None, parent)
