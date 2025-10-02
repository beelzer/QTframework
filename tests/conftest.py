from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget


if TYPE_CHECKING:
    from collections.abc import Generator

    from pytestqt.qtbot import QtBot

    # from qtframework.core.application import Application
    # from qtframework.core.window import MainWindow


# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session")
def qapp() -> Generator[QApplication]:
    """Session-scoped Application instance."""
    from qtframework.core.application import Application

    app = QApplication.instance()
    if app is None:
        # Create our custom Application instance
        app = Application(
            app_name="QtFrameworkTest",
            org_name="QtFrameworkTestOrg",
            org_domain="test.qtframework.org"
        )
    return app
    # Don't quit the app, pytest-qt manages it


@pytest.fixture
def qtbot(qapp: QApplication, qtbot: QtBot) -> QtBot:
    """Enhanced qtbot fixture with our QApplication."""
    return qtbot


@pytest.fixture
def main_window(qtbot: QtBot) -> Generator[QMainWindow]:
    """Create a main window for testing."""
    window = QMainWindow()
    window.setWindowTitle("Test Window")
    window.resize(800, 600)
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    yield window
    window.close()


@pytest.fixture
def test_widget(qtbot: QtBot) -> Generator[QWidget]:
    """Create a generic widget for testing."""
    widget = QWidget()
    qtbot.addWidget(widget)
    widget.show()
    qtbot.waitExposed(widget)
    yield widget
    widget.close()


@pytest.fixture
def mock_settings(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Mock QSettings for testing."""
    mock = MagicMock(spec=QSettings)
    mock.value.return_value = None
    mock.setValue.return_value = None
    mock.sync.return_value = None
    monkeypatch.setattr("PySide6.QtCore.QSettings", lambda *args, **kwargs: mock)
    return mock


@pytest.fixture
def temp_config_file(tmp_path: Path) -> Path:
    """Create a temporary config file."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
application:
  name: TestApp
  version: 1.0.0
  debug: true

window:
  width: 1024
  height: 768
  title: Test Application

theme:
  style: fusion
  dark_mode: false
"""
    )
    return config_file


@pytest.fixture
def temp_translations_dir(tmp_path: Path) -> Path:
    """Create a temporary translations directory with test files."""
    trans_dir = tmp_path / "translations"
    trans_dir.mkdir()

    # Create a test .po file
    po_file = trans_dir / "messages.po"
    po_file.write_text(
        """
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\\n"
"Language: en\\n"

msgid "Hello"
msgstr "Hello"

msgid "Welcome"
msgstr "Welcome to the application"
"""
    )
    return trans_dir


@pytest.fixture
def mock_qt_application(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Mock the Application class."""
    from qtframework.core import application

    mock_app = MagicMock(spec=application.Application)
    mock_app.run.return_value = 0
    mock_app.quit.return_value = None
    mock_app.is_running = True

    monkeypatch.setattr(application, "Application", lambda *args, **kwargs: mock_app)
    return mock_app


@pytest.fixture
def sample_data() -> dict[str, Any]:
    """Provide sample data for testing."""
    return {
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
            {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
        ],
        "settings": {
            "theme": "dark",
            "language": "en",
            "auto_save": True,
            "interval": 300,
        },
        "metadata": {
            "version": "1.0.0",
            "created": "2025-01-01",
            "modified": "2025-01-30",
        },
    }


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    # Import and reset any singleton classes here
    # This prevents state leakage between tests
    return
    # Cleanup code if needed


@pytest.fixture
def mock_database(tmp_path: Path) -> Path:
    """Create a temporary SQLite database for testing."""
    return tmp_path / "test.db"
    # Initialize with basic schema if needed


# Markers for different test categories
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "gui: Tests requiring GUI")
    config.addinivalue_line("markers", "network: Tests requiring network access")
    config.addinivalue_line("markers", "database: Tests requiring database")


# Helper functions for tests
def click_button(qtbot: QtBot, button: QWidget) -> None:
    """Helper to click a button."""
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)


def enter_text(qtbot: QtBot, widget: QWidget, text: str) -> None:
    """Helper to enter text into a widget."""
    widget.clear()
    widget.setFocus()
    qtbot.keyClicks(widget, text)


def wait_for_signal(qtbot: QtBot, signal: Any, timeout: int = 1000) -> Any:
    """Helper to wait for a signal with timeout."""
    with qtbot.waitSignal(signal, timeout=timeout) as blocker:
        return blocker.args
