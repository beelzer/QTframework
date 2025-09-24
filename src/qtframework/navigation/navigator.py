"""Navigator widget for managing view transitions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPropertyAnimation, Signal
from PySide6.QtWidgets import QStackedWidget, QWidget


if TYPE_CHECKING:
    from qtframework.navigation.router import Router


class Navigator(QStackedWidget):
    """Navigator widget for managing view transitions."""

    view_changed = Signal(int)

    def __init__(
        self,
        router: Router | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize navigator.

        Args:
            router: Router instance
            parent: Parent widget
        """
        super().__init__(parent)
        self._router = router
        self._views: dict[str, QWidget] = {}
        self._transitions_enabled = True

        if router:
            router.route_changed.connect(self._on_route_changed)

    def add_view(self, path: str, widget: QWidget) -> None:
        """Add a view to the navigator.

        Args:
            path: Route path
            widget: View widget
        """
        self._views[path] = widget
        self.addWidget(widget)

    def remove_view(self, path: str) -> None:
        """Remove a view from the navigator.

        Args:
            path: Route path
        """
        if path in self._views:
            widget = self._views.pop(path)
            self.removeWidget(widget)

    def navigate_to(self, path: str) -> bool:
        """Navigate to a view.

        Args:
            path: Route path

        Returns:
            True if navigation successful
        """
        if path in self._views:
            widget = self._views[path]
            index = self.indexOf(widget)

            if self._transitions_enabled:
                self._animate_transition(index)
            else:
                self.setCurrentIndex(index)

            self.view_changed.emit(index)
            return True

        return False

    def _on_route_changed(self, path: str, params: dict) -> None:
        """Handle route change from router.

        Args:
            path: New route path
            params: Route parameters
        """
        self.navigate_to(path)

    def _animate_transition(self, index: int) -> None:
        """Animate transition to new view.

        Args:
            index: Target widget index
        """
        # Simple fade transition
        current = self.currentWidget()
        if current:
            fade_out = QPropertyAnimation(current, b"windowOpacity")
            fade_out.setDuration(150)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.0)
            fade_out.finished.connect(lambda: self.setCurrentIndex(index))
            fade_out.start()

            next_widget = self.widget(index)
            if next_widget:
                fade_in = QPropertyAnimation(next_widget, b"windowOpacity")
                fade_in.setDuration(150)
                fade_in.setStartValue(0.0)
                fade_in.setEndValue(1.0)
                fade_in.start()
        else:
            self.setCurrentIndex(index)

    def enable_transitions(self, enable: bool = True) -> None:
        """Enable or disable view transitions.

        Args:
            enable: Enable transitions
        """
        self._transitions_enabled = enable

    def back(self) -> bool:
        """Go back in navigation history.

        Returns:
            True if successful
        """
        if self._router:
            return self._router.back()
        return False

    def forward(self) -> bool:
        """Go forward in navigation history.

        Returns:
            True if successful
        """
        if self._router:
            return self._router.forward()
        return False

    def get_current_path(self) -> str | None:
        """Get current view path.

        Returns:
            Current path or None
        """
        widget = self.currentWidget()
        for path, view in self._views.items():
            if view == widget:
                return path
        return None
