"""Application core module."""

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

from PySide6.QtCore import QMessageLogContext, QSettings, QtMsgType, Signal, qInstallMessageHandler
from PySide6.QtGui import QGuiApplication, QPalette
from PySide6.QtWidgets import QApplication

from qtframework.core.context import Context
from qtframework.themes import ThemeManager
from qtframework.utils.logger import get_logger


if TYPE_CHECKING:
    from qtframework.core.window import BaseWindow

logger = get_logger(__name__)
_MessageHandler = Callable[[QtMsgType, QMessageLogContext, str], None]


_original_qt_message_handler: _MessageHandler | None = None


def _qt_message_filter(mode: QtMsgType, context: QMessageLogContext, message: str) -> None:
    """Filter Qt messages to suppress stylesheet parsing warnings.

    Args:
        mode: Message type (debug, warning, critical, etc.)
        context: Context information about the message
        message: The log message
    """
    if message != "Could not parse application stylesheet" and _original_qt_message_handler:
        _original_qt_message_handler(mode, context, message)


class Application(QApplication):
    """Enhanced QApplication with built-in theme and context management."""

    theme_changed = Signal(str)
    context_changed = Signal()

    def __init__(
        self,
        argv: list[str] | None = None,
        *,
        app_name: str = "QtFrameworkApp",
        org_name: str = "QtFramework",
        org_domain: str = "qtframework.local",
    ) -> None:
        """Initialize the application.

        Args:
            argv: Command line arguments
            app_name: Application name
            org_name: Organization name
            org_domain: Organization domain
        """
        super().__init__(argv or sys.argv)

        self.setApplicationName(app_name)
        self.setOrganizationName(org_name)
        self.setOrganizationDomain(org_domain)

        self._context = Context()
        self._theme_manager = ThemeManager()
        self._current_stylesheet: str = ""
        self._settings = QSettings()
        self._windows: list[BaseWindow] = []

        self._initialize()

    def _install_stylesheet_warning_filter(self) -> None:
        """Install Qt message handler to filter stylesheet warnings."""
        global _original_qt_message_handler
        if _original_qt_message_handler is None:
            handler = qInstallMessageHandler(_qt_message_filter)
            _original_qt_message_handler = cast("_MessageHandler", handler)

    def _initialize(self) -> None:
        """Initialize application components."""
        logger.info(f"Initializing {self.applicationName()}")
        self._install_stylesheet_warning_filter()

        self._load_settings()
        self._setup_theme()
        self._connect_signals()

        logger.info("Application initialized successfully")

    def _load_settings(self) -> None:
        """Load application settings."""
        saved_theme = self._settings.value("theme", None)
        if saved_theme:
            theme = str(saved_theme)
        else:
            theme = self._detect_os_theme()
        self._context.set("theme", theme)

    def _setup_theme(self) -> None:
        """Setup initial theme."""
        theme_name = self._context.get("theme", "light")
        self._theme_manager.set_theme(theme_name)
        self._apply_stylesheet(self._theme_manager.get_stylesheet())

    def _apply_stylesheet(self, stylesheet: str | None) -> None:
        """Apply stylesheet if it changed to avoid redundant parsing."""
        if stylesheet is None:
            stylesheet = ""
        if stylesheet == self._current_stylesheet:
            return
        self.setStyleSheet(stylesheet)
        self._current_stylesheet = self.styleSheet()

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        self._theme_manager.theme_changed.connect(self._on_theme_changed)
        self.aboutToQuit.connect(self._on_about_to_quit)

    def _on_theme_changed(self, theme_name: str) -> None:
        """Handle theme change.

        Args:
            theme_name: New theme name
        """
        logger.info("Changing theme to: %s", theme_name)
        self._context.set("theme", theme_name)
        self._apply_stylesheet(self._theme_manager.get_stylesheet())
        self.theme_changed.emit(theme_name)

    def _on_about_to_quit(self) -> None:
        """Handle application quit."""
        logger.info("Application shutting down")
        self._save_settings()

    def _save_settings(self) -> None:
        """Save application settings."""
        self._settings.setValue("theme", self._context.get("theme", "light"))
        self._settings.sync()

    def _detect_os_theme(self) -> str:
        """Detect OS dark mode preference.

        Returns:
            "dark" if OS is in dark mode, "light" otherwise
        """
        # Qt 6.5+ supports direct color scheme detection
        try:
            style_hints = QGuiApplication.styleHints()
            if hasattr(style_hints, "colorScheme"):
                from PySide6.QtCore import Qt

                if style_hints.colorScheme() == Qt.ColorScheme.Dark:
                    logger.info("OS dark mode detected via styleHints")
                    return "dark"
        except (AttributeError, ImportError):
            pass

        # Fallback: Infer from palette luminance
        palette = QGuiApplication.palette()
        window_color = palette.color(QPalette.ColorRole.Window)
        luminance = (
            0.299 * window_color.red() + 0.587 * window_color.green() + 0.114 * window_color.blue()
        ) / 255

        if luminance < 0.5:
            logger.info("Dark theme detected via palette luminance")
            return "dark"

        logger.info("Light theme detected")
        return "light"

    @property
    def context(self) -> Context:
        """Get application context."""
        return self._context

    @property
    def theme_manager(self) -> ThemeManager:
        """Get theme manager."""
        return self._theme_manager

    @property
    def settings(self) -> QSettings:
        """Get settings object."""
        return self._settings

    def register_window(self, window: BaseWindow) -> None:
        """Register a window with the application.

        Args:
            window: Window to register
        """
        if window not in self._windows:
            self._windows.append(window)
            logger.debug(f"Registered window: {window.windowTitle()}")

    def unregister_window(self, window: BaseWindow) -> None:
        """Unregister a window from the application.

        Args:
            window: Window to unregister
        """
        if window in self._windows:
            self._windows.remove(window)
            logger.debug(f"Unregistered window: {window.windowTitle()}")

    @staticmethod
    def exec() -> int:
        """Execute the application."""
        app = QApplication.instance()
        if isinstance(app, Application):
            logger.info(f"Starting {app.applicationName()}")
        return int(QApplication.exec())

    @classmethod
    def create_and_run(
        cls,
        window_class: type[BaseWindow],
        *,
        argv: list[str] | None = None,
        app_name: str = "QtFrameworkApp",
        org_name: str = "QtFramework",
        org_domain: str = "qtframework.local",
        **window_kwargs: Any,
    ) -> int:
        """Create and run application with main window.

        Args:
            window_class: Main window class
            argv: Command line arguments
            app_name: Application name
            org_name: Organization name
            org_domain: Organization domain
            **window_kwargs: Keyword arguments for window

        Returns:
            Application exit code
        """
        app = cls(
            argv=argv,
            app_name=app_name,
            org_name=org_name,
            org_domain=org_domain,
        )
        window = window_class(application=app, **window_kwargs)
        window.show()
        return app.exec()
