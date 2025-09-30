"""Flow layout that automatically wraps widgets based on available width.

This module provides a flow layout that arranges widgets in a flowing manner,
similar to how text wraps in a word processor. Widgets automatically wrap to
the next line when they exceed the available width.

Layout Structure:
    Widgets flow left to right and wrap when necessary::

        Available Width
        ┌─────────────────────────────────┐
        │ ┌────┐ ┌────┐ ┌────┐ ┌────┐    │
        │ │ W1 │ │ W2 │ │ W3 │ │ W4 │    │
        │ └────┘ └────┘ └────┘ └────┘    │
        │ ┌────┐ ┌────┐ ┌────┐           │
        │ │ W5 │ │ W6 │ │ W7 │           │
        │ └────┘ └────┘ └────┘           │
        │ ┌────┐                          │
        │ │ W8 │                          │
        │ └────┘                          │
        └─────────────────────────────────┘

        When Width Decreases:
        ┌───────────────┐
        │ ┌────┐ ┌────┐│
        │ │ W1 │ │ W2 ││
        │ └────┘ └────┘│
        │ ┌────┐ ┌────┐│
        │ │ W3 │ │ W4 ││
        │ └────┘ └────┘│
        │ ┌────┐ ┌────┐│
        │ │ W5 │ │ W6 ││
        │ └────┘ └────┘│
        └───────────────┘

Example:
    Create a flow layout with tags or chips::

        from qtframework.layouts.flow import FlowLayout
        from qtframework.widgets import Badge
        from PySide6.QtWidgets import QWidget

        # Create container with flow layout
        container = QWidget()
        flow_layout = FlowLayout(parent=container, margin=10, h_spacing=8, v_spacing=8)

        # Add tags/chips that will wrap automatically
        tags = [
            "Python",
            "JavaScript",
            "React",
            "Qt",
            "Django",
            "FastAPI",
            "PostgreSQL",
            "Redis",
            "Docker",
        ]

        for tag in tags:
            badge = Badge(text=tag, variant="primary")
            flow_layout.addWidget(badge)

        # Layout automatically reflows on window resize

    Use with button groups::

        from qtframework.widgets import Button

        # Create action buttons that wrap on small screens
        actions = ["Save", "Cancel", "Delete", "Export", "Print"]

        for action in actions:
            button = Button(text=action)
            flow_layout.addWidget(button)

    Custom spacing based on widget properties::

        # Create layout with tight spacing
        tight_flow = FlowLayout(h_spacing=4, v_spacing=4)

        # Create layout with generous spacing
        loose_flow = FlowLayout(h_spacing=16, v_spacing=16)

Key Features:
    - **Automatic Wrapping**: Widgets wrap to next line when width exceeded
    - **Dynamic Reflow**: Automatically adjusts on window resize
    - **Custom Spacing**: Configure horizontal and vertical spacing
    - **Height for Width**: Properly calculates height based on width
    - **Smart Spacing**: Uses platform-appropriate spacing when not specified

See Also:
    :class:`SidebarLayout`: Sidebar layout with collapsible panel
    :class:`qtframework.widgets.Badge`: Badge widget often used with flow layout
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout, QStyle, QWidget


if TYPE_CHECKING:
    from PySide6.QtWidgets import QLayoutItem


class FlowLayout(QLayout):
    """A layout that arranges widgets in a flowing manner, wrapping to new lines as needed."""

    def __init__(
        self,
        parent: QWidget | None = None,
        margin: int = -1,
        h_spacing: int = -1,
        v_spacing: int = -1,
    ) -> None:
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

    def __del__(self) -> None:
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
        return self._smart_spacing(horizontal=True)

    def verticalSpacing(self) -> int:
        """Get vertical spacing between widgets."""
        if self._v_space >= 0:
            return self._v_space
        return self._smart_spacing(horizontal=False)

    def count(self) -> int:
        """Return the number of items in the layout."""
        return len(self._item_list)

    def itemAt(self, index: int) -> QLayoutItem | None:
        """Return the item at the given index."""
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index: int) -> QLayoutItem:
        """Remove and return the item at the given index."""
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return cast("QLayoutItem", None)

    def expandingDirections(self) -> Qt.Orientation:
        """Return the expanding directions."""
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        """Return whether the layout has height for width."""
        return True

    def heightForWidth(self, width: int) -> int:
        """Calculate the height needed for a given width."""
        if width <= 0:
            return int(self.minimumSize().height())
        height = self._do_layout(QRect(0, 0, width, 0), test=True)
        return int(max(height, self.minimumSize().height()))

    def setGeometry(self, rect: QRect) -> None:
        """Set the geometry of the layout."""
        super().setGeometry(rect)
        self._do_layout(rect, test=False)

    def invalidate(self) -> None:
        """Invalidate the layout to force recalculation.

        Triggers immediate re-layout if geometry is already valid to ensure
        proper widget positioning after invalidation.
        """
        super().invalidate()
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
        left = top = right = bottom = 0
        margins = cast("tuple[int, int, int, int]", self.getContentsMargins())
        if margins:
            left, top, right, bottom = margins
        effective_rect = rect.adjusted(left, top, -right, -bottom)

        # Fallback to parent width if layout width not yet determined
        if effective_rect.width() <= 0:
            parent_widget = self.parentWidget()
            if parent_widget is not None:
                effective_rect.setWidth(parent_widget.width() - left - right)
            if effective_rect.width() <= 0:
                return 0

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
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item_size.width() + space_x
                line_height = 0

            if not test:
                item.setGeometry(QRect(QPoint(x, y), item_size))
                if widget:
                    widget.show()
                    widget.raise_()

            x = next_x
            line_height = max(line_height, item_size.height())

        return int(y + line_height - rect.y() + bottom)

    def _smart_spacing(self, *, horizontal: bool) -> int:
        """Calculate smart spacing based on parent widget style."""
        parent = self.parent()
        if not isinstance(parent, QWidget):
            return -1

        style = parent.style()
        if horizontal:
            metric = style.pixelMetric(
                QStyle.PixelMetric.PM_LayoutHorizontalSpacing,
                None,
                parent,
            )
        else:
            metric = style.pixelMetric(
                QStyle.PixelMetric.PM_LayoutVerticalSpacing,
                None,
                parent,
            )
        return int(metric)
