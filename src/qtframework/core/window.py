"""Base window implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QMainWindow

from qtframework.utils.logger import get_logger


if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

    from qtframework.core.application import Application

logger = get_logger(__name__)


class BaseWindow(QMainWindow):
    """Base window class with framework integration."""

    window_closed = Signal()

    def __init__(
        self,
        application: Application | None = None,
        *,
        parent: QWidget | None = None,
        title: str = "Qt Framework Window",
    ) -> None:
        """Initialize base window.

        Args:
            application: Parent application
            parent: Parent widget
            title: Window title
        """
        super().__init__(parent)
        self._app = application
        self.setWindowTitle(title)

        self._initialize()
        if self._app:
            self._app.register_window(self)

    def _initialize(self) -> None:
        """Initialize window components."""
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Setup UI components."""
        self.setMinimumSize(800, 600)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        if self._app:
            self._app.theme_changed.connect(self._on_theme_changed)
            self._app.context_changed.connect(self._on_context_changed)

    def _on_theme_changed(self, theme_name: str) -> None:
        """Handle theme change.

        Args:
            theme_name: New theme name
        """
        logger.debug(f"Theme changed to {theme_name} in {self.windowTitle()}")

    def _on_context_changed(self) -> None:
        """Handle context change."""
        logger.debug(f"Context changed in {self.windowTitle()}")

    @property
    def application(self) -> Application | None:
        """Get parent application."""
        return self._app

    def closeEvent(self, event: Any) -> None:
        """Handle window close event.

        Args:
            event: Close event
        """
        logger.debug(f"Closing window: {self.windowTitle()}")
        if self._app:
            self._app.unregister_window(self)
        self.window_closed.emit()
        super().closeEvent(event)
