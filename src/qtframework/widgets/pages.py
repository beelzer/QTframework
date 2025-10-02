"""Page widgets for building application content.

This module provides base classes for creating structured page layouts
with scrolling, sections, and consistent styling.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from qtframework.utils.styling import set_heading_level


class ScrollablePage(QWidget):
    """Base class for scrollable content pages with sections.

    This widget provides a consistent structure for building pages with:
    - Optional scrolling
    - Title with heading style
    - Section management with titles
    - Stretch management

    Example:
        ```python
        page = ScrollablePage("Settings")
        page.add_section("General", general_settings_widget)
        page.add_section("Advanced", advanced_settings_widget)
        page.add_stretch()
        ```
    """

    page_shown = Signal()
    page_hidden = Signal()

    def __init__(
        self,
        title: str = "",
        scrollable: bool = True,
        parent: QWidget | None = None,
    ):
        """Initialize the scrollable page.

        Args:
            title: Optional page title
            scrollable: Whether the page should be scrollable
            parent: Parent widget
        """
        super().__init__(parent)
        self.title = title
        self._init_ui(scrollable)

    def _init_ui(self, scrollable: bool) -> None:
        """Initialize the UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        if scrollable:
            # Create scroll area
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setObjectName("pageScrollArea")

            # Create content widget
            self.content_widget = QWidget()
            self.content_layout = QVBoxLayout(self.content_widget)

            # Add title if provided
            if self.title:
                title_label = QLabel(self.title)
                set_heading_level(title_label, 1)
                self.content_layout.addWidget(title_label)

            scroll.setWidget(self.content_widget)
            main_layout.addWidget(scroll)
        else:
            self.content_widget = self
            self.content_layout = main_layout

            # Add title if provided
            if self.title:
                title_label = QLabel(self.title)
                set_heading_level(title_label, 1)
                self.content_layout.addWidget(title_label)

    def add_section(
        self,
        title: str,
        widget: QWidget,
        collapsible: bool = False,
    ) -> None:
        """Add a section to the page.

        Args:
            title: Section title (optional)
            widget: The widget to add in this section
            collapsible: Whether the section should be collapsible (future enhancement)
        """
        if title:
            section_title = QLabel(title)
            set_heading_level(section_title, 2)
            self.content_layout.addWidget(section_title)

        self.content_layout.addWidget(widget)

    def add_stretch(self) -> None:
        """Add stretch to push content to the top."""
        self.content_layout.addStretch()

    def add_spacing(self, spacing: int) -> None:
        """Add vertical spacing to the layout.

        Args:
            spacing: Amount of spacing in pixels
        """
        self.content_layout.addSpacing(spacing)

    def showEvent(self, event) -> None:
        """Override to emit page_shown signal."""
        super().showEvent(event)
        self.page_shown.emit()

    def hideEvent(self, event) -> None:
        """Override to emit page_hidden signal."""
        super().hideEvent(event)
        self.page_hidden.emit()


class NonScrollablePage(ScrollablePage):
    """Convenience class for non-scrollable pages.

    Example:
        ```python
        page = NonScrollablePage("Dashboard")
        page.add_section("", dashboard_widget)
        ```
    """

    def __init__(self, title: str = "", parent: QWidget | None = None):
        """Initialize a non-scrollable page.

        Args:
            title: Optional page title
            parent: Parent widget
        """
        super().__init__(title, scrollable=False, parent=parent)
