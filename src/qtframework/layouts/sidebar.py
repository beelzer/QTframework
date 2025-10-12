"""Sidebar layout implementation.

This module provides a collapsible sidebar layout with support for left/right
positioning, resizing, and smooth animations.

Layout Structure:
    The sidebar layout creates a two-panel interface::

        Left Sidebar:
        ┌──────────┬─────────────────────────┐
        │          │                         │
        │ Sidebar  │   Main Content Area     │
        │  Panel   │                         │
        │          │   [Toggle Button]       │
        │          │                         │
        └──────────┴─────────────────────────┘

        Right Sidebar:
        ┌─────────────────────────┬──────────┐
        │                         │          │
        │   Main Content Area     │ Sidebar  │
        │                         │  Panel   │
        │   [Toggle Button]       │          │
        │                         │          │
        └─────────────────────────┴──────────┘

        Collapsed State (Left):
        ┌─┬────────────────────────────────┐
        │ │                                │
        │ │    Main Content Area           │
        │ │                                │
        │ │    [Toggle Button]             │
        │ │                                │
        └─┴────────────────────────────────┘

Example:
    Create a sidebar layout with navigation::

        from qtframework.layouts.sidebar import SidebarLayout, SidebarPosition
        from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

        # Create sidebar layout
        sidebar_layout = SidebarLayout(
            sidebar_width=250,
            position=SidebarPosition.LEFT,
            collapsible=True,
            resizable=True,
        )

        # Create sidebar content (navigation)
        nav_panel = QWidget()
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.addWidget(QLabel("Navigation"))
        nav_layout.addWidget(QPushButton("Home"))
        nav_layout.addWidget(QPushButton("Settings"))
        nav_layout.addWidget(QPushButton("Profile"))

        # Create main content
        content_panel = QWidget()
        content_layout = QVBoxLayout(content_panel)
        content_layout.addWidget(QLabel("Main Content Area"))

        # Set widgets
        sidebar_layout.set_sidebar_widget(nav_panel)
        sidebar_layout.set_content_widget(content_panel)

        # Listen for sidebar toggle
        sidebar_layout.sidebar_toggled.connect(
            lambda visible: print(f"Sidebar visible: {visible}")
        )

        # Programmatically toggle
        sidebar_layout.toggle_sidebar()  # Collapse/expand

See Also:
    :class:`FlowLayout`: Flow layout for wrapping widgets
    :mod:`qtframework.layouts`: Other layout components
"""

from __future__ import annotations

from enum import Enum

from PySide6.QtCore import QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QSplitter, QVBoxLayout, QWidget


class SidebarPosition(Enum):
    """Sidebar position."""

    LEFT = "left"
    RIGHT = "right"


class SidebarLayout(QWidget):
    """Layout with collapsible sidebar."""

    sidebar_toggled = Signal(bool)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        sidebar_width: int = 250,
        position: SidebarPosition = SidebarPosition.LEFT,
        collapsible: bool = True,
        resizable: bool = True,
    ) -> None:
        """Initialize sidebar layout.

        Args:
            parent: Parent widget
            sidebar_width: Sidebar width in pixels
            position: Sidebar position
            collapsible: Allow sidebar to collapse
            resizable: Allow sidebar resize
        """
        super().__init__(parent)

        self._sidebar_width = sidebar_width
        self._position = position
        self._collapsible = collapsible
        self._resizable = resizable
        self._is_collapsed = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if self._resizable:
            self._splitter = QSplitter(Qt.Orientation.Horizontal)
            layout.addWidget(self._splitter)

            self._sidebar_frame = QFrame()
            self._content_frame = QFrame()

            if self._position == SidebarPosition.LEFT:
                self._splitter.addWidget(self._sidebar_frame)
                self._splitter.addWidget(self._content_frame)
            else:
                self._splitter.addWidget(self._content_frame)
                self._splitter.addWidget(self._sidebar_frame)

            self._splitter.setSizes([self._sidebar_width, 10000])
            self._splitter.setCollapsible(0, False)
            self._splitter.setCollapsible(1, False)
        else:
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(0)

            self._sidebar_frame = QFrame()
            self._sidebar_frame.setFixedWidth(self._sidebar_width)
            self._content_frame = QFrame()

            if self._position == SidebarPosition.LEFT:
                container_layout.addWidget(self._sidebar_frame)
                container_layout.addWidget(self._content_frame)
            else:
                container_layout.addWidget(self._content_frame)
                container_layout.addWidget(self._sidebar_frame)

            layout.addWidget(container)

        self._sidebar_frame.setProperty("class", "sidebar")
        self._content_frame.setProperty("class", "sidebar-content")

        self._sidebar_layout = QVBoxLayout(self._sidebar_frame)
        self._sidebar_layout.setContentsMargins(0, 0, 0, 0)

        self._content_layout = QVBoxLayout(self._content_frame)
        self._content_layout.setContentsMargins(0, 0, 0, 0)

        if self._collapsible:
            self._setup_toggle_button()

    def _setup_toggle_button(self) -> None:
        """Setup toggle button."""
        self._toggle_btn = QPushButton()
        self._toggle_btn.setProperty("class", "sidebar-toggle")
        self._toggle_btn.setFixedSize(36, 36)
        self._toggle_btn.clicked.connect(self.toggle_sidebar)
        self._toggle_btn.setText("☰")

        # Create a container for the toggle button positioned in the content area
        toggle_container = QWidget()
        toggle_layout = QHBoxLayout(toggle_container)
        toggle_layout.setContentsMargins(8, 8, 8, 0)
        toggle_layout.setSpacing(0)

        if self._position == SidebarPosition.LEFT:
            toggle_layout.addWidget(self._toggle_btn)
            toggle_layout.addStretch()
        else:
            toggle_layout.addStretch()
            toggle_layout.addWidget(self._toggle_btn)

        self._content_layout.insertWidget(0, toggle_container)

    def set_sidebar_widget(self, widget: QWidget) -> None:
        """Set sidebar widget.

        Args:
            widget: Widget to set in sidebar
        """
        while self._sidebar_layout.count() > (1 if self._collapsible else 0):
            item = self._sidebar_layout.takeAt(1 if self._collapsible else 0)
            old_widget = item.widget() if item else None
            if old_widget:
                old_widget.setParent(None)

        self._sidebar_layout.addWidget(widget)

    def set_content_widget(self, widget: QWidget) -> None:
        """Set content widget.

        Args:
            widget: Widget to set in content area
        """
        # Keep the toggle button if it exists (at index 0)
        start_index = 1 if self._collapsible else 0

        while self._content_layout.count() > start_index:
            item = self._content_layout.takeAt(start_index)
            old_widget = item.widget() if item else None
            if old_widget:
                old_widget.setParent(None)

        self._content_layout.addWidget(widget)

    def toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        self._is_collapsed = not self._is_collapsed

        if self._is_collapsed:
            self._collapse_sidebar()
        else:
            self._expand_sidebar()

        self.sidebar_toggled.emit(not self._is_collapsed)

    def _collapse_sidebar(self) -> None:
        """Collapse sidebar."""
        self._animation = QPropertyAnimation(self._sidebar_frame, b"maximumWidth")
        self._animation.setDuration(200)
        self._animation.setStartValue(self._sidebar_frame.width())
        self._animation.setEndValue(40 if self._collapsible else 0)
        self._animation.start()

    def _expand_sidebar(self) -> None:
        """Expand sidebar."""
        self._animation = QPropertyAnimation(self._sidebar_frame, b"maximumWidth")
        self._animation.setDuration(200)
        self._animation.setStartValue(self._sidebar_frame.width())
        self._animation.setEndValue(self._sidebar_width)
        self._animation.start()

    def is_collapsed(self) -> bool:
        """Check if sidebar is collapsed.

        Returns:
            True if collapsed
        """
        return self._is_collapsed

    def set_sidebar_width(self, width: int) -> None:
        """Set sidebar width.

        Args:
            width: Width in pixels
        """
        self._sidebar_width = width
        if not self._is_collapsed:
            if self._resizable:
                sizes = self._splitter.sizes()
                sizes[0 if self._position == SidebarPosition.LEFT else 1] = width
                self._splitter.setSizes(sizes)
            else:
                self._sidebar_frame.setFixedWidth(width)
