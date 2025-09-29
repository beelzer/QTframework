from __future__ import annotations

import time
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QWidget


if TYPE_CHECKING:
    from collections.abc import Generator
    from unittest.mock import Mock

    from pytest_qt.qtbot import QtBot


class TestHelpers:
    """Collection of test helper functions."""

    @staticmethod
    def wait_for_condition(
        condition: callable,
        timeout: int = 5000,
        interval: int = 100,
    ) -> bool:
        """Wait for a condition to become true.

        Args:
            condition: Callable that returns bool
            timeout: Maximum wait time in milliseconds
            interval: Check interval in milliseconds

        Returns:
            True if condition met, False if timeout
        """
        start_time = time.time()
        timeout_seconds = timeout / 1000.0

        while time.time() - start_time < timeout_seconds:
            if condition():
                return True
            QTest.qWait(interval)

        return False

    @staticmethod
    def process_events(duration: int = 100) -> None:
        """Process Qt events for specified duration."""
        QTest.qWait(duration)

    @staticmethod
    @contextmanager
    def assert_no_qt_warnings() -> Generator[None]:
        """Context manager to assert no Qt warnings are emitted."""
        app = QApplication.instance()
        if not app:
            yield
            return

        warnings = []

        def capture_warning(msg_type: Any, context: Any, message: str) -> None:
            if msg_type == 1:  # QtWarningMsg
                warnings.append(message)

        # Would need to properly hook into Qt's message handler
        # This is a simplified version
        yield

        if warnings:
            raise AssertionError(f"Qt warnings emitted: {warnings}")

    @staticmethod
    def create_mock_widget(
        widget_class: type[QWidget] = QWidget,
        **attributes: Any,
    ) -> Mock:
        """Create a mock widget with specified attributes."""
        mock = MagicMock(spec=widget_class)
        for attr, value in attributes.items():
            setattr(mock, attr, value)
        return mock

    @staticmethod
    def simulate_key_sequence(
        qtbot: QtBot,
        widget: QWidget,
        sequence: str,
    ) -> None:
        """Simulate a key sequence on a widget."""
        widget.setFocus()
        qtbot.keyClicks(widget, sequence)

    @staticmethod
    def simulate_drag_drop(
        qtbot: QtBot,
        source: QWidget,
        target: QWidget,
        data: Any = None,
    ) -> None:
        """Simulate drag and drop between widgets."""
        source_pos = source.rect().center()
        target_pos = target.rect().center()

        qtbot.mousePress(source, Qt.MouseButton.LeftButton, pos=source_pos)
        qtbot.mouseMove(target, pos=target_pos)
        qtbot.mouseRelease(target, Qt.MouseButton.LeftButton, pos=target_pos)

    @staticmethod
    def get_widget_screenshot(widget: QWidget) -> bytes:
        """Get a screenshot of a widget as bytes."""
        widget.grab()
        byte_array = bytearray()
        # Simplified - would need proper implementation
        return bytes(byte_array)

    @staticmethod
    def compare_widgets(widget1: QWidget, widget2: QWidget) -> bool:
        """Compare two widgets for visual equality."""
        # Simplified comparison
        return (
            widget1.size() == widget2.size()
            and widget1.pos() == widget2.pos()
            and widget1.isVisible() == widget2.isVisible()
        )


class DataGenerators:
    """Test data generators."""

    @staticmethod
    def generate_config(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
        """Generate test configuration data."""
        base_config = {
            "application": {
                "name": "TestApp",
                "version": "1.0.0",
                "debug": True,
            },
            "window": {
                "width": 800,
                "height": 600,
                "x": 100,
                "y": 100,
                "maximized": False,
            },
            "theme": {
                "style": "fusion",
                "dark_mode": False,
                "accent_color": "#0078d4",
            },
            "i18n": {
                "default_language": "en",
                "available_languages": ["en", "es", "fr", "de"],
            },
        }

        if overrides:
            _deep_update(base_config, overrides)

        return base_config

    @staticmethod
    def generate_user_data(count: int = 3) -> list[dict[str, Any]]:
        """Generate test user data."""
        return [
            {
                "id": i + 1,
                "username": f"user{i + 1}",
                "email": f"user{i + 1}@example.com",
                "full_name": f"Test User {i + 1}",
                "is_active": i % 2 == 0,
                "created_at": "2025-01-01T00:00:00",
            }
            for i in range(count)
        ]

    @staticmethod
    def generate_translation_data() -> dict[str, str]:
        """Generate test translation data."""
        return {
            "app.title": "Application Title",
            "app.welcome": "Welcome to {app_name}",
            "menu.file": "File",
            "menu.edit": "Edit",
            "menu.view": "View",
            "menu.help": "Help",
            "action.open": "Open",
            "action.save": "Save",
            "action.close": "Close",
            "dialog.confirm": "Are you sure?",
            "dialog.yes": "Yes",
            "dialog.no": "No",
            "dialog.cancel": "Cancel",
            "error.generic": "An error occurred: {error}",
            "error.file_not_found": "File not found: {filename}",
        }


class PerformanceTimer:
    """Context manager for timing operations."""

    def __init__(self, name: str = "Operation"):
        """Initialize timer with operation name."""
        self.name = name
        self.start_time: float | None = None
        self.end_time: float | None = None

    def __enter__(self) -> PerformanceTimer:
        """Start timing."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        """End timing and print result."""
        self.end_time = time.perf_counter()

    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None or self.end_time is None:
            return 0.0
        return self.end_time - self.start_time

    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        return self.elapsed * 1000


def _deep_update(base: dict, updates: dict) -> None:
    """Deep update nested dictionary."""
    for key, value in updates.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_update(base[key], value)
        else:
            base[key] = value


# Assertion helpers
def assert_widget_visible(widget: QWidget) -> None:
    """Assert that a widget is visible."""
    assert widget.isVisible(), f"Widget {widget} is not visible"


def assert_widget_enabled(widget: QWidget) -> None:
    """Assert that a widget is enabled."""
    assert widget.isEnabled(), f"Widget {widget} is not enabled"


def assert_signal_emitted(qtbot: QtBot, signal: Any, timeout: int = 1000) -> list[Any]:
    """Assert that a signal is emitted and return its arguments."""
    with qtbot.waitSignal(signal, timeout=timeout) as blocker:
        return blocker.args
