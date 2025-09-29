from __future__ import annotations

import random
import string
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

from PySide6.QtCore import QRect, QSize, Qt

# from PySide6.QtGui import QColor, QFont  # Unused imports
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QWidget,
)


class WidgetFactory:
    """Factory for creating test widgets."""

    @staticmethod
    def create_button(
        text: str = "Button",
        enabled: bool = True,
        checkable: bool = False,
        checked: bool = False,
    ) -> QPushButton:
        """Create a test button."""
        button = QPushButton(text)
        button.setEnabled(enabled)
        button.setCheckable(checkable)
        button.setChecked(checked)
        return button

    @staticmethod
    def create_label(
        text: str = "Label",
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
    ) -> QLabel:
        """Create a test label."""
        label = QLabel(text)
        label.setAlignment(alignment)
        return label

    @staticmethod
    def create_line_edit(
        text: str = "",
        placeholder: str = "Enter text...",
        max_length: int = 100,
        read_only: bool = False,
    ) -> QLineEdit:
        """Create a test line edit."""
        line_edit = QLineEdit(text)
        line_edit.setPlaceholderText(placeholder)
        line_edit.setMaxLength(max_length)
        line_edit.setReadOnly(read_only)
        return line_edit

    @staticmethod
    def create_text_edit(
        text: str = "",
        read_only: bool = False,
        word_wrap: bool = True,
    ) -> QTextEdit:
        """Create a test text edit."""
        text_edit = QTextEdit()
        text_edit.setText(text)
        text_edit.setReadOnly(read_only)
        text_edit.setWordWrapMode(
            Qt.TextWordWrapMode.WordWrap if word_wrap else Qt.TextWordWrapMode.NoWrap
        )
        return text_edit

    @staticmethod
    def create_dialog(
        title: str = "Test Dialog",
        modal: bool = True,
        size: tuple[int, int] = (400, 300),
    ) -> QDialog:
        """Create a test dialog."""
        dialog = QDialog()
        dialog.setWindowTitle(title)
        dialog.setModal(modal)
        dialog.resize(*size)
        return dialog

    @staticmethod
    def create_main_window(
        title: str = "Test Window",
        size: tuple[int, int] = (800, 600),
        position: tuple[int, int] = (100, 100),
    ) -> QMainWindow:
        """Create a test main window."""
        window = QMainWindow()
        window.setWindowTitle(title)
        window.resize(*size)
        window.move(*position)
        return window


class ConfigFactory:
    """Factory for creating test configurations."""

    @staticmethod
    def create_minimal_config() -> dict[str, Any]:
        """Create minimal configuration."""
        return {
            "application": {
                "name": "TestApp",
            }
        }

    @staticmethod
    def create_standard_config() -> dict[str, Any]:
        """Create standard configuration."""
        return {
            "application": {
                "name": "TestApplication",
                "version": "1.0.0",
                "organization": "TestOrg",
                "description": "A test application",
            },
            "window": {
                "title": "Test Window",
                "width": 1024,
                "height": 768,
                "x": 100,
                "y": 100,
                "maximized": False,
                "fullscreen": False,
            },
            "theme": {
                "style": "fusion",
                "dark_mode": False,
                "accent_color": "#0078d4",
                "font_family": "Arial",
                "font_size": 10,
            },
            "i18n": {
                "default_locale": "en",
                "available_locales": ["en", "es", "fr", "de"],
                "locale_dir": "locales",
                "domain": "messages",
            },
            "features": {
                "auto_save": True,
                "auto_save_interval": 300,
                "show_tooltips": True,
                "enable_animations": True,
            },
        }

    @staticmethod
    def create_database_config() -> dict[str, Any]:
        """Create database configuration."""
        return {
            "database": {
                "engine": "sqlite",
                "url": "sqlite:///test.db",
                "pool_size": 5,
                "echo": False,
                "options": {
                    "check_same_thread": False,
                },
            }
        }

    @staticmethod
    def create_logging_config() -> dict[str, Any]:
        """Create logging configuration."""
        return {
            "logging": {
                "level": "DEBUG",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "level": "DEBUG",
                        "stream": "sys.stdout",
                    },
                    "file": {
                        "class": "logging.FileHandler",
                        "level": "INFO",
                        "filename": "app.log",
                        "mode": "a",
                    },
                },
            }
        }


class DataFactory:
    """Factory for creating test data."""

    @staticmethod
    def create_user(
        user_id: int | None = None,
        username: str | None = None,
        email: str | None = None,
    ) -> dict[str, Any]:
        """Create user test data."""
        if user_id is None:
            user_id = random.randint(1, 10000)
        if username is None:
            username = f"user_{random.randint(1000, 9999)}"
        if email is None:
            email = f"{username}@example.com"

        return {
            "id": user_id,
            "username": username,
            "email": email,
            "full_name": f"Test User {user_id}",
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "last_login": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
        }

    @staticmethod
    def create_users(count: int = 5) -> list[dict[str, Any]]:
        """Create multiple users."""
        return [DataFactory.create_user(user_id=i + 1) for i in range(count)]

    @staticmethod
    def create_project() -> dict[str, Any]:
        """Create project test data."""
        project_id = random.randint(1, 1000)
        return {
            "id": project_id,
            "name": f"Project {project_id}",
            "description": f"Description for project {project_id}",
            "status": random.choice(["active", "inactive", "archived"]),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "tags": random.sample(["python", "qt", "gui", "desktop", "framework"], 3),
        }

    @staticmethod
    def create_file_info(path: str | None = None) -> dict[str, Any]:
        """Create file information test data."""
        if path is None:
            filename = f"file_{random.randint(1000, 9999)}.txt"
            path = f"/test/path/{filename}"

        return {
            "path": path,
            "name": Path(path).name,
            "size": random.randint(100, 1000000),
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "is_directory": False,
            "permissions": "rw-r--r--",
        }

    @staticmethod
    def create_random_string(length: int = 10) -> str:
        """Create random string."""
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def create_translation_data(locale: str = "en") -> dict[str, str]:
        """Create translation test data."""
        translations = {
            "en": {
                "app.title": "Application",
                "menu.file": "File",
                "menu.edit": "Edit",
                "menu.view": "View",
                "menu.help": "Help",
                "action.open": "Open",
                "action.save": "Save",
                "action.close": "Close",
                "dialog.confirm": "Are you sure?",
            },
            "es": {
                "app.title": "Aplicación",
                "menu.file": "Archivo",
                "menu.edit": "Editar",
                "menu.view": "Ver",
                "menu.help": "Ayuda",
                "action.open": "Abrir",
                "action.save": "Guardar",
                "action.close": "Cerrar",
                "dialog.confirm": "¿Está seguro?",
            },
        }
        return translations.get(locale, translations["en"])


class MockFactory:
    """Factory for creating mock objects."""

    @staticmethod
    def create_mock_config(data: dict[str, Any] | None = None) -> MagicMock:
        """Create mock configuration object."""
        if data is None:
            data = ConfigFactory.create_standard_config()

        mock_config = MagicMock()

        def get_value(key: str, default: Any = None) -> Any:
            keys = key.split(".")
            value = data
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value

        mock_config.get.side_effect = get_value
        mock_config.to_dict.return_value = data
        return mock_config

    @staticmethod
    def create_mock_window() -> MagicMock:
        """Create mock window object."""
        mock_window = MagicMock(spec=QMainWindow)
        mock_window.isVisible.return_value = True
        mock_window.isMinimized.return_value = False
        mock_window.isMaximized.return_value = False
        mock_window.width.return_value = 800
        mock_window.height.return_value = 600
        mock_window.x.return_value = 100
        mock_window.y.return_value = 100
        mock_window.windowTitle.return_value = "Mock Window"
        return mock_window

    @staticmethod
    def create_mock_widget() -> MagicMock:
        """Create mock widget object."""
        mock_widget = MagicMock(spec=QWidget)
        mock_widget.isEnabled.return_value = True
        mock_widget.isVisible.return_value = True
        mock_widget.size.return_value = QSize(200, 100)
        mock_widget.rect.return_value = QRect(0, 0, 200, 100)
        return mock_widget

    @staticmethod
    def create_mock_event(event_type: str = "mouse_click") -> MagicMock:
        """Create mock event object."""
        mock_event = MagicMock()

        if event_type == "mouse_click":
            mock_event.button.return_value = Qt.MouseButton.LeftButton
            mock_event.pos.return_value.x.return_value = 10
            mock_event.pos.return_value.y.return_value = 20
        elif event_type == "key_press":
            mock_event.key.return_value = Qt.Key.Key_Return
            mock_event.text.return_value = "\n"
            mock_event.modifiers.return_value = Qt.KeyboardModifier.NoModifier
        elif event_type == "close":
            mock_event.accept = MagicMock()
            mock_event.ignore = MagicMock()
            mock_event.isAccepted.return_value = False

        return mock_event


@dataclass
class TestContext:
    """Container for test context and utilities."""

    config: dict[str, Any] = field(default_factory=ConfigFactory.create_standard_config)
    users: list[dict[str, Any]] = field(default_factory=lambda: DataFactory.create_users(3))
    translations: dict[str, str] = field(default_factory=DataFactory.create_translation_data)
    temp_dir: Path | None = None
    mocks: dict[str, MagicMock] = field(default_factory=dict)

    def create_mock(self, name: str, mock_type: str = "widget") -> MagicMock:
        """Create and store a mock object."""
        if mock_type == "widget":
            mock = MockFactory.create_mock_widget()
        elif mock_type == "window":
            mock = MockFactory.create_mock_window()
        elif mock_type == "config":
            mock = MockFactory.create_mock_config(self.config)
        else:
            mock = MagicMock()

        self.mocks[name] = mock
        return mock

    def get_mock(self, name: str) -> MagicMock | None:
        """Get a stored mock by name."""
        return self.mocks.get(name)
