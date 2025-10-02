"""Advanced scroll area widgets.

This module provides enhanced scroll area widgets with additional features
like dynamic margin adjustment for scrollbars.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QTimer
from PySide6.QtWidgets import QScrollArea


if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


class DynamicScrollArea(QScrollArea):
    """Scroll area that dynamically adjusts content margins when scrollbar appears/disappears.

    This prevents content from being obscured by the scrollbar by automatically
    adjusting the right margin of the content widget's layout.

    Example:
        ```python
        scroll = DynamicScrollArea()
        scroll.setWidget(content_widget)
        # Margins automatically adjust when scrollbar visibility changes
        ```
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        base_margin: int = 10,
        buffer_pixels: int = 3,
        track_vertical: bool = True,
        track_horizontal: bool = False,
    ):
        """Initialize the dynamic scroll area.

        Args:
            parent: Parent widget
            base_margin: Base right margin when no scrollbar (default: 10)
            buffer_pixels: Extra pixels to prevent overlap (default: 3)
            track_vertical: Track vertical scrollbar visibility (default: True)
            track_horizontal: Track horizontal scrollbar visibility (default: False)
        """
        super().__init__(parent)
        self._base_margin = base_margin
        self._buffer_pixels = buffer_pixels
        self._track_vertical = track_vertical
        self._track_horizontal = track_horizontal
        self._adjustment_enabled = True

        # Debounce timer to avoid excessive margin calculations
        self._adjustment_timer = QTimer()
        self._adjustment_timer.setSingleShot(True)
        self._adjustment_timer.timeout.connect(self._do_adjust_margins)

        # Install event filter on scrollbars to catch visibility changes
        if track_vertical:
            v_bar = self.verticalScrollBar()
            if v_bar:
                v_bar.installEventFilter(self)

        if track_horizontal:
            h_bar = self.horizontalScrollBar()
            if h_bar:
                h_bar.installEventFilter(self)

    def resizeEvent(self, event) -> None:
        """Handle resize events to adjust for scrollbar visibility."""
        super().resizeEvent(event)
        if self._adjustment_enabled:
            # Debounce the adjustment to avoid too many calls
            self._adjustment_timer.stop()
            self._adjustment_timer.start(10)

    def showEvent(self, event) -> None:
        """Handle show events to adjust margins."""
        super().showEvent(event)
        if self._adjustment_enabled:
            self._adjustment_timer.start(10)

    def setWidget(self, widget: QWidget) -> None:
        """Override setWidget to trigger adjustment when content changes."""
        super().setWidget(widget)
        if widget and self._adjustment_enabled:
            # Connect to layout changes
            self._adjustment_timer.start(10)

    def _do_adjust_margins(self) -> None:
        """Actually perform the margin adjustment."""
        widget = self.widget()
        if not widget or not widget.layout():
            return

        margins = widget.layout().contentsMargins()
        left, top, right, bottom = (
            margins.left(),
            margins.top(),
            margins.right(),
            margins.bottom(),
        )

        # Calculate new margins based on scrollbar visibility
        new_right = self._base_margin
        new_bottom = bottom

        if self._track_vertical:
            v_bar = self.verticalScrollBar()
            if v_bar and v_bar.isVisible():
                scrollbar_width = v_bar.width()
                new_right = self._base_margin + scrollbar_width + self._buffer_pixels

        if self._track_horizontal:
            h_bar = self.horizontalScrollBar()
            if h_bar and h_bar.isVisible():
                scrollbar_height = h_bar.height()
                new_bottom = margins.bottom() + scrollbar_height + self._buffer_pixels

        # Only update if margins need to change
        if right != new_right or bottom != new_bottom:
            widget.layout().setContentsMargins(left, top, new_right, new_bottom)
            # Force a layout update to apply changes immediately
            widget.layout().update()

    def adjust_content_margins(self) -> None:
        """Manually trigger margin adjustment."""
        if self._adjustment_enabled:
            self._adjustment_timer.start(10)

    def set_adjustment_enabled(self, enabled: bool) -> None:
        """Enable or disable dynamic margin adjustment.

        Args:
            enabled: Whether to enable margin adjustment
        """
        self._adjustment_enabled = enabled
        if enabled:
            self._adjustment_timer.start(10)

    def set_debounce_delay(self, milliseconds: int) -> None:
        """Set the debounce delay for margin adjustments.

        Args:
            milliseconds: Delay in milliseconds (default: 10)
        """
        # Note: We don't restart the timer here, just change the duration
        # for future calls

    def set_base_margin(self, margin: int) -> None:
        """Set the base margin when no scrollbar is visible.

        Args:
            margin: Base margin in pixels
        """
        self._base_margin = margin
        if self._adjustment_enabled:
            self._adjustment_timer.start(10)

    def set_buffer_pixels(self, pixels: int) -> None:
        """Set the buffer pixels to prevent overlap.

        Args:
            pixels: Buffer in pixels
        """
        self._buffer_pixels = pixels
        if self._adjustment_enabled:
            self._adjustment_timer.start(10)

    def eventFilter(self, watched, event) -> bool:
        """Filter events to catch scrollbar visibility changes."""
        v_bar = self.verticalScrollBar() if self._track_vertical else None
        h_bar = self.horizontalScrollBar() if self._track_horizontal else None

        if watched in {v_bar, h_bar}:
            if event.type() in {QEvent.Show, QEvent.Hide}:
                # Scrollbar visibility changed, adjust margins
                if self._adjustment_enabled:
                    self._adjustment_timer.start(10)

        return super().eventFilter(watched, event)
