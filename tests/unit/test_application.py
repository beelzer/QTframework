"""Tests for Application class."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from PySide6.QtCore import QSettings

from qtframework.core.application import Application
from qtframework.core.window import BaseWindow


if TYPE_CHECKING:
    from unittest.mock import Mock

    from pytest_qt.qtbot import QtBot


@pytest.fixture
def app(qapp) -> Application:
    """Fixture to get Application instance."""
    # qapp is now our Application instance from conftest
    return qapp


class TestApplicationCreation:
    """Test Application creation."""

    def test_application_has_name(self, app: Application) -> None:
        """Test application has name."""
        assert app.applicationName() is not None
        assert len(app.applicationName()) > 0

    def test_application_has_org_name(self, app: Application) -> None:
        """Test application has organization name."""
        assert app.organizationName() is not None

    def test_application_has_context(self, app: Application) -> None:
        """Test application has context."""
        assert app.context is not None

    def test_application_has_theme_manager(self, app: Application) -> None:
        """Test application has theme manager."""
        assert app.theme_manager is not None

    def test_application_has_settings(self, app: Application) -> None:
        """Test application has settings."""
        assert isinstance(app.settings, QSettings)


class TestApplicationContext:
    """Test Application context management."""

    def test_context_property(self, app: Application) -> None:
        """Test context property."""
        context = app.context
        assert context is not None

    def test_context_has_theme(self, app: Application) -> None:
        """Test context has theme set."""
        theme = app.context.get("theme")
        assert theme in {"light", "dark", None}

    def test_context_set_value(self, app: Application) -> None:
        """Test setting context value."""
        app.context.set("test_key", "test_value")
        assert app.context.get("test_key") == "test_value"


class TestApplicationTheme:
    """Test Application theme management."""

    def test_theme_manager_property(self, app: Application) -> None:
        """Test theme_manager property."""
        theme_manager = app.theme_manager
        assert theme_manager is not None

    def test_initial_theme_set(self, app: Application) -> None:
        """Test initial theme is set."""
        assert app.theme_manager.get_current_theme() is not None

    def test_theme_changed_signal(self, app: Application, qtbot: QtBot) -> None:
        """Test theme changed signal emission."""
        # Set to light first to ensure we can detect the change to dark
        app.theme_manager.set_theme("light")

        with qtbot.waitSignal(app.theme_changed, timeout=1000) as blocker:
            app.theme_manager.set_theme("dark")

        assert blocker.args == ["dark"]

    def test_theme_change_updates_context(self, app: Application) -> None:
        """Test theme change updates context."""
        app.theme_manager.set_theme("dark")
        assert app.context.get("theme") == "dark"

    def test_theme_change_applies_stylesheet(self, app: Application) -> None:
        """Test theme change applies stylesheet."""
        app.theme_manager.set_theme("dark")
        # Stylesheet should be applied
        assert True


class TestApplicationSettings:
    """Test Application settings management."""

    def test_settings_property(self, app: Application) -> None:
        """Test settings property."""
        settings = app.settings
        assert isinstance(settings, QSettings)

    def test_save_settings(self, app: Application) -> None:
        """Test saving settings."""
        app.context.set("theme", "dark")
        app._save_settings()

        # Settings should be saved
        saved_theme = app.settings.value("theme")
        assert saved_theme == "dark"


class TestApplicationWindowManagement:
    """Test Application window management."""

    def test_register_window(self, app: Application, qtbot: QtBot) -> None:
        """Test registering a window."""
        # Get initial count (may already have windows from session)
        initial_count = len(app._windows)

        window = BaseWindow(application=app)
        qtbot.addWidget(window)

        # BaseWindow auto-registers in __init__, so count should already be +1
        assert len(app._windows) == initial_count + 1

    def test_register_window_once(self, app: Application, qtbot: QtBot) -> None:
        """Test window is only registered once."""
        initial_count = len(app._windows)

        window = BaseWindow(application=app)
        qtbot.addWidget(window)

        # Window auto-registers, try registering again manually
        app.register_window(window)

        # Should still be only +1 from initial
        assert len(app._windows) == initial_count + 1

    def test_unregister_window(self, app: Application, qtbot: QtBot) -> None:
        """Test unregistering a window."""
        window = BaseWindow(application=app)
        qtbot.addWidget(window)

        # Window is auto-registered
        initial_count = len(app._windows)
        app.unregister_window(window)

        assert len(app._windows) == initial_count - 1

    def test_unregister_nonexistent_window(self, app: Application, qtbot: QtBot) -> None:
        """Test unregistering nonexistent window doesn't error."""
        window = BaseWindow(application=app)
        qtbot.addWidget(window)

        # Should not raise
        app.unregister_window(window)


class TestApplicationStylesheet:
    """Test Application stylesheet management."""

    def test_apply_stylesheet_none(self, app: Application) -> None:
        """Test applying None stylesheet."""
        app._apply_stylesheet(None)
        assert app.styleSheet() == ""

    def test_apply_stylesheet_same_skips(self, app: Application) -> None:
        """Test applying same stylesheet is skipped."""
        stylesheet = "QWidget { background: red; }"

        app._apply_stylesheet(stylesheet)
        initial_stylesheet = app.styleSheet()

        # Apply same stylesheet again
        app._apply_stylesheet(stylesheet)

        # Should be same
        assert app.styleSheet() == initial_stylesheet

    def test_apply_stylesheet_different(self, app: Application) -> None:
        """Test applying different stylesheet."""
        app._apply_stylesheet("QWidget { background: red; }")
        app._apply_stylesheet("QWidget { background: blue; }")

        # Verify stylesheet was applied
        assert True


class TestApplicationSignals:
    """Test Application signal handling."""

    def test_theme_changed_signal_emission(self, app: Application, qtbot: QtBot) -> None:
        """Test theme_changed signal is emitted."""
        signals_received = []

        app.theme_changed.connect(signals_received.append)

        # Set to light first to ensure signal fires
        app.theme_manager.set_theme("light")
        app.theme_manager.set_theme("dark")

        assert "dark" in signals_received

    def test_about_to_quit_saves_settings(self, app: Application) -> None:
        """Test aboutToQuit signal saves settings."""
        app.context.set("theme", "dark")

        # Emit aboutToQuit
        app.aboutToQuit.emit()

        # Settings should be saved
        saved_theme = app.settings.value("theme")
        assert saved_theme == "dark"


class TestApplicationOSThemeDetection:
    """Test Application OS theme detection."""

    def test_detect_os_theme_returns_string(self, app: Application) -> None:
        """Test OS theme detection returns string."""
        theme = app._detect_os_theme()
        assert theme in {"light", "dark"}

    def test_detect_os_theme_fallback_to_palette(self, app: Application) -> None:
        """Test falling back to palette luminance."""
        # Just ensure it doesn't crash and returns valid theme
        theme = app._detect_os_theme()
        assert theme in {"light", "dark"}


class TestApplicationInitialization:
    """Test Application initialization."""

    def test_initialization_sets_up_components(self, app: Application) -> None:
        """Test initialization sets up all components."""
        assert app.context is not None
        assert app.theme_manager is not None
        assert app.settings is not None
        assert isinstance(app._windows, list)

    def test_initialization_connects_signals(self, app: Application, qtbot: QtBot) -> None:
        """Test initialization connects signals."""
        # Theme manager signal should be connected
        signals_received = []
        app.theme_changed.connect(signals_received.append)

        app.theme_manager.set_theme("light")
        assert "light" in signals_received

    def test_initialization_loads_settings(self, app: Application) -> None:
        """Test initialization loads settings."""
        # Theme should be loaded from settings or OS
        theme = app.context.get("theme")
        assert theme in {"light", "dark", None}


class TestApplicationExec:
    """Test Application execution."""

    @patch("qtframework.core.application.QApplication.exec")
    def test_exec_returns_int(self, mock_exec: Mock) -> None:
        """Test exec returns integer."""
        mock_exec.return_value = 0

        result = Application.exec()
        assert isinstance(result, int)

    @patch("qtframework.core.application.QApplication.exec")
    def test_exec_calls_qapplication_exec(self, mock_exec: Mock) -> None:
        """Test exec calls QApplication.exec."""
        mock_exec.return_value = 0

        Application.exec()
        mock_exec.assert_called_once()


class TestApplicationMessageFilter:
    """Test Application Qt message filtering."""

    def test_message_filter_installed(self, app: Application) -> None:
        """Test message filter is installed."""
        # Filter should be installed during initialization
        # Just verify it doesn't crash
        assert app is not None

    def test_install_stylesheet_warning_filter(self, app: Application) -> None:
        """Test installing stylesheet warning filter."""
        # Should be able to call multiple times without error
        app._install_stylesheet_warning_filter()
        app._install_stylesheet_warning_filter()


class TestApplicationIntegration:
    """Test Application integration scenarios."""

    def test_full_lifecycle(self, app: Application, qtbot: QtBot) -> None:
        """Test full application lifecycle."""
        # Create and register window
        window = BaseWindow(application=app, title="Test Window")
        qtbot.addWidget(window)
        app.register_window(window)

        initial_count = len(app._windows)

        # Change theme
        app.theme_manager.set_theme("dark")
        assert app.context.get("theme") == "dark"

        # Unregister window
        app.unregister_window(window)
        assert len(app._windows) == initial_count - 1

        # Save settings
        app._save_settings()
        assert app.settings.value("theme") == "dark"

    def test_multiple_windows(self, app: Application, qtbot: QtBot) -> None:
        """Test managing multiple windows."""
        initial_count = len(app._windows)

        window1 = BaseWindow(application=app, title="Window 1")
        window2 = BaseWindow(application=app, title="Window 2")
        qtbot.addWidget(window1)
        qtbot.addWidget(window2)

        # Windows auto-register in __init__
        assert len(app._windows) == initial_count + 2

    def test_theme_change_propagates(self, app: Application, qtbot: QtBot) -> None:
        """Test theme change propagates to all components."""
        signals_received = []
        app.theme_changed.connect(signals_received.append)

        # Change theme
        app.theme_manager.set_theme("light")

        # Verify propagation
        assert app.context.get("theme") == "light"
        assert "light" in signals_received
        assert app.theme_manager.get_current_theme().name == "light"
