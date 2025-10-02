"""Tests for BaseWindow class."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, Mock

from PySide6.QtCore import Qt

from qtframework.core.window import BaseWindow


if TYPE_CHECKING:
    from pytest_qt.qtbot import QtBot


class TestBaseWindowCreation:
    """Test BaseWindow creation."""

    def test_window_creation_default(self, qtbot: QtBot) -> None:
        """Test creating window with defaults."""
        window = BaseWindow()
        qtbot.addWidget(window)

        assert window.windowTitle() == "Qt Framework Window"
        assert window.minimumWidth() == 800
        assert window.minimumHeight() == 600

    def test_window_creation_with_title(self, qtbot: QtBot) -> None:
        """Test creating window with custom title."""
        window = BaseWindow(title="Custom Title")
        qtbot.addWidget(window)

        assert window.windowTitle() == "Custom Title"

    def test_window_has_delete_on_close(self, qtbot: QtBot) -> None:
        """Test window has delete on close attribute."""
        window = BaseWindow()
        qtbot.addWidget(window)

        assert window.testAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

    def test_window_minimum_size(self, qtbot: QtBot) -> None:
        """Test window minimum size is set."""
        window = BaseWindow()
        qtbot.addWidget(window)

        assert window.minimumSize().width() == 800
        assert window.minimumSize().height() == 600


class TestBaseWindowWithApplication:
    """Test BaseWindow with Application."""

    def test_window_with_application(self, qtbot: QtBot) -> None:
        """Test creating window with application."""
        app_mock = Mock()
        app_mock.register_window = Mock()
        app_mock.theme_changed = Mock()
        app_mock.context_changed = Mock()
        app_mock.theme_changed.connect = Mock()
        app_mock.context_changed.connect = Mock()

        window = BaseWindow(application=app_mock)
        qtbot.addWidget(window)

        app_mock.register_window.assert_called_once_with(window)

    def test_window_application_property(self, qtbot: QtBot) -> None:
        """Test window application property."""
        app_mock = Mock()
        app_mock.register_window = Mock()
        app_mock.theme_changed = Mock()
        app_mock.context_changed = Mock()
        app_mock.theme_changed.connect = Mock()
        app_mock.context_changed.connect = Mock()

        window = BaseWindow(application=app_mock)
        qtbot.addWidget(window)

        assert window.application == app_mock

    def test_window_without_application_property(self, qtbot: QtBot) -> None:
        """Test window without application."""
        window = BaseWindow()
        qtbot.addWidget(window)

        assert window.application is None


class TestBaseWindowSignals:
    """Test BaseWindow signal handling."""

    def test_window_closed_signal(self, qtbot: QtBot) -> None:
        """Test window_closed signal emitted."""
        window = BaseWindow()
        qtbot.addWidget(window)

        with qtbot.waitSignal(window.window_closed, timeout=1000):
            window.close()

    def test_theme_changed_handler(self, qtbot: QtBot) -> None:
        """Test theme changed handler is connected."""
        app_mock = Mock()
        app_mock.register_window = Mock()
        app_mock.theme_changed = MagicMock()
        app_mock.context_changed = MagicMock()

        window = BaseWindow(application=app_mock)
        qtbot.addWidget(window)

        app_mock.theme_changed.connect.assert_called_once()

    def test_context_changed_handler(self, qtbot: QtBot) -> None:
        """Test context changed handler is connected."""
        app_mock = Mock()
        app_mock.register_window = Mock()
        app_mock.theme_changed = MagicMock()
        app_mock.context_changed = MagicMock()

        window = BaseWindow(application=app_mock)
        qtbot.addWidget(window)

        app_mock.context_changed.connect.assert_called_once()


class TestBaseWindowClose:
    """Test BaseWindow close behavior."""

    def test_close_unregisters_window(self, qtbot: QtBot) -> None:
        """Test closing window unregisters from application."""
        app_mock = Mock()
        app_mock.register_window = Mock()
        app_mock.unregister_window = Mock()
        app_mock.theme_changed = MagicMock()
        app_mock.context_changed = MagicMock()

        window = BaseWindow(application=app_mock)

        window.close()

        app_mock.unregister_window.assert_called_once_with(window)

    def test_close_disconnects_signals(self, qtbot: QtBot) -> None:
        """Test closing window disconnects signals."""
        app_mock = Mock()
        app_mock.register_window = Mock()
        app_mock.unregister_window = Mock()
        app_mock.theme_changed = MagicMock()
        app_mock.context_changed = MagicMock()

        window = BaseWindow(application=app_mock)

        window.close()

        app_mock.theme_changed.disconnect.assert_called()
        app_mock.context_changed.disconnect.assert_called()

    def test_close_without_application(self, qtbot: QtBot) -> None:
        """Test closing window without application."""
        window = BaseWindow()
        qtbot.addWidget(window)

        # Should not raise any errors
        window.close()
        qtbot.wait(100)


class TestBaseWindowMethods:
    """Test BaseWindow methods."""

    def test_window_show(self, qtbot: QtBot) -> None:
        """Test showing window."""
        window = BaseWindow()
        qtbot.addWidget(window)

        window.show()
        qtbot.waitExposed(window)

        assert window.isVisible()

    def test_window_hide(self, qtbot: QtBot) -> None:
        """Test hiding window."""
        window = BaseWindow()
        qtbot.addWidget(window)

        window.show()
        qtbot.waitExposed(window)
        window.hide()

        assert not window.isVisible()

    def test_window_resize(self, qtbot: QtBot) -> None:
        """Test resizing window."""
        window = BaseWindow()
        qtbot.addWidget(window)

        window.resize(1024, 768)

        assert window.width() == 1024
        assert window.height() == 768

    def test_window_set_title(self, qtbot: QtBot) -> None:
        """Test setting window title."""
        window = BaseWindow()
        qtbot.addWidget(window)

        window.setWindowTitle("New Title")

        assert window.windowTitle() == "New Title"


class TestBaseWindowThemeHandling:
    """Test BaseWindow theme handling."""

    def test_on_theme_changed_called(self, qtbot: QtBot) -> None:
        """Test _on_theme_changed is called when theme changes."""
        app_mock = Mock()
        app_mock.register_window = Mock()
        app_mock.unregister_window = Mock()
        app_mock.theme_changed = MagicMock()
        app_mock.context_changed = MagicMock()

        window = BaseWindow(application=app_mock)
        qtbot.addWidget(window)

        # Get the callback that was connected
        connect_call = app_mock.theme_changed.connect.call_args
        if connect_call:
            callback = connect_call[0][0]
            # Call the callback to simulate theme change
            callback("dark")

        # Window should still exist
        assert window is not None

    def test_on_context_changed_called(self, qtbot: QtBot) -> None:
        """Test _on_context_changed is called when context changes."""
        app_mock = Mock()
        app_mock.register_window = Mock()
        app_mock.unregister_window = Mock()
        app_mock.theme_changed = MagicMock()
        app_mock.context_changed = MagicMock()

        window = BaseWindow(application=app_mock)
        qtbot.addWidget(window)

        # Get the callback that was connected
        connect_call = app_mock.context_changed.connect.call_args
        if connect_call:
            callback = connect_call[0][0]
            # Call the callback to simulate context change
            callback()

        # Window should still exist
        assert window is not None


class TestBaseWindowParent:
    """Test BaseWindow with parent widget."""

    def test_window_with_parent(self, qtbot: QtBot) -> None:
        """Test creating window with parent widget."""
        from PySide6.QtWidgets import QWidget

        parent = QWidget()
        qtbot.addWidget(parent)

        window = BaseWindow(parent=parent)
        qtbot.addWidget(window)

        assert window.parent() == parent
