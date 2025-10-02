"""Page management widgets.

This module provides widgets for managing multiple pages with
stacked layouts and transitions.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QStackedWidget, QWidget


if TYPE_CHECKING:
    from collections.abc import Callable


class PageTransition(Enum):
    """Page transition animation types."""

    NONE = 0
    FADE = 1
    SLIDE_LEFT = 2
    SLIDE_RIGHT = 3


class PageManager(QStackedWidget):
    """Manages multiple pages with name-based access and lifecycle hooks.

    Provides a clean API for adding, removing, and switching between pages,
    with support for page lifecycle events and special layout handling.

    Example:
        ```python
        manager = PageManager()
        manager.add_page("home", HomePage())
        manager.add_page("settings", SettingsPage())
        manager.show_page("home")
        manager.page_changed.connect(lambda old, new: print(f"{old} -> {new}"))
        ```
    """

    page_changed = Signal(str, str)  # (old_page_name, new_page_name)

    def __init__(self, parent: QWidget | None = None):
        """Initialize the page manager.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.pages: dict[str, int] = {}
        self.page_instances: dict[str, QWidget] = {}
        self._lazy_factories: dict[str, Callable] = {}
        self._transition = PageTransition.NONE
        self._navigation_history: list[str] = []
        self._history_index = -1

        # Connect to index changed signal
        self.currentChanged.connect(self._on_current_changed)

    def add_page(
        self,
        name: str,
        widget_or_factory: QWidget | Callable,
        show_immediately: bool = False,
        lazy_load: bool = False,
    ) -> None:
        """Add a page with a unique name.

        Args:
            name: Unique name for the page
            widget_or_factory: Either a QWidget instance or a factory function that creates one
            show_immediately: Whether to show this page immediately
            lazy_load: Whether to defer widget creation until first shown
        """
        if name in self.pages:
            raise ValueError(f"Page '{name}' already exists")

        if lazy_load and callable(widget_or_factory):
            # Store factory for lazy loading
            self._lazy_factories[name] = widget_or_factory
            # Add placeholder
            placeholder = QWidget()
            index = self.addWidget(placeholder)
            self.pages[name] = index
        else:
            # Immediate loading
            if callable(widget_or_factory):
                widget = widget_or_factory()
            else:
                widget = widget_or_factory

            index = self.addWidget(widget)
            self.pages[name] = index
            self.page_instances[name] = widget

        if show_immediately:
            self.show_page(name)

    def show_page(self, name: str) -> bool:
        """Show a specific page by name.

        Args:
            name: Name of the page to show

        Returns:
            True if page was shown, False if page doesn't exist
        """
        if name not in self.pages:
            return False

        # Handle lazy loading
        if name in self._lazy_factories:
            # Replace placeholder with actual widget
            factory = self._lazy_factories.pop(name)
            widget = factory()
            index = self.pages[name]

            # Remove placeholder
            placeholder = self.widget(index)
            self.removeWidget(placeholder)
            placeholder.deleteLater()

            # Insert actual widget at same index
            self.insertWidget(index, widget)
            self.page_instances[name] = widget

        old_name = self.current_page_name()

        # Set current index
        self.setCurrentIndex(self.pages[name])

        # Update navigation history
        if not self._navigation_history or self._navigation_history[-1] != name:
            # Truncate forward history if we're not at the end
            if self._history_index < len(self._navigation_history) - 1:
                self._navigation_history = self._navigation_history[: self._history_index + 1]
            self._navigation_history.append(name)
            self._history_index = len(self._navigation_history) - 1

        # Handle page lifecycle and layout updates
        current_widget = self.currentWidget()
        if current_widget:
            # Notify page that it's being shown
            if hasattr(current_widget, "page_shown"):
                # Check if it's a signal (has emit method) vs a regular method
                if hasattr(current_widget.page_shown, "emit"):
                    # It's a signal
                    current_widget.page_shown.emit()
                elif callable(current_widget.page_shown):
                    # It's a method
                    current_widget.page_shown()

            # Schedule deferred layout update for FlowLayouts
            QTimer.singleShot(0, lambda: self._update_page_layouts(current_widget))

        # Emit page changed signal
        if old_name != name:
            self.page_changed.emit(old_name or "", name)

        return True

    def _update_page_layouts(self, widget: QWidget) -> None:
        """Update FlowLayout instances in the page."""
        try:
            from qtframework.layouts import FlowLayout

            def update_flow_layouts(w: QWidget):
                if w.layout() and isinstance(w.layout(), FlowLayout):
                    w.layout().invalidate()
                    w.layout().activate()
                    w.adjustSize()

                for child in w.findChildren(QWidget):
                    if child.layout() and isinstance(child.layout(), FlowLayout):
                        child.layout().invalidate()
                        child.layout().activate()
                        child.adjustSize()

            update_flow_layouts(widget)
            widget.updateGeometry()
        except ImportError:
            # FlowLayout not available, skip
            pass

    def remove_page(self, name: str) -> bool:
        """Remove a page by name.

        Args:
            name: Name of the page to remove

        Returns:
            True if page was removed, False if page doesn't exist
        """
        if name not in self.pages:
            return False

        index = self.pages[name]
        widget = self.widget(index)

        # Remove from stack
        self.removeWidget(widget)

        # Clean up
        del self.pages[name]
        if name in self.page_instances:
            del self.page_instances[name]
        if name in self._lazy_factories:
            del self._lazy_factories[name]

        # Update indices for remaining pages
        self.pages = {n: i for i, (n, _) in enumerate(self.pages.items())}

        # Remove from history
        self._navigation_history = [h for h in self._navigation_history if h != name]
        if self._history_index >= len(self._navigation_history):
            self._history_index = len(self._navigation_history) - 1

        widget.deleteLater()
        return True

    def get_page(self, name: str) -> QWidget | None:
        """Get page widget by name.

        Args:
            name: Name of the page

        Returns:
            The page widget or None if not found
        """
        return self.page_instances.get(name)

    def current_page_name(self) -> str | None:
        """Get name of currently visible page.

        Returns:
            Name of current page or None if no pages
        """
        current_index = self.currentIndex()
        for name, index in self.pages.items():
            if index == current_index:
                return name
        return None

    def page_names(self) -> list[str]:
        """Get list of all page names."""
        return list(self.pages.keys())

    def set_transition(self, transition: PageTransition) -> None:
        """Set page transition animation (future enhancement).

        Args:
            transition: The transition type
        """
        self._transition = transition

    def go_back(self) -> bool:
        """Navigate to previous page in history.

        Returns:
            True if navigation succeeded, False otherwise
        """
        if self._history_index > 0:
            self._history_index -= 1
            page_name = self._navigation_history[self._history_index]
            # Show page without adding to history again
            self.setCurrentIndex(self.pages[page_name])
            return True
        return False

    def go_forward(self) -> bool:
        """Navigate to next page in history.

        Returns:
            True if navigation succeeded, False otherwise
        """
        if self._history_index < len(self._navigation_history) - 1:
            self._history_index += 1
            page_name = self._navigation_history[self._history_index]
            # Show page without adding to history again
            self.setCurrentIndex(self.pages[page_name])
            return True
        return False

    def can_go_back(self) -> bool:
        """Check if backward navigation is possible."""
        return self._history_index > 0

    def can_go_forward(self) -> bool:
        """Check if forward navigation is possible."""
        return self._history_index < len(self._navigation_history) - 1

    def clear_history(self) -> None:
        """Clear navigation history."""
        current = self.current_page_name()
        self._navigation_history = [current] if current else []
        self._history_index = 0 if current else -1

    def _on_current_changed(self, index: int) -> None:
        """Handle current index changed."""
        # This is called by both show_page and manual navigation
