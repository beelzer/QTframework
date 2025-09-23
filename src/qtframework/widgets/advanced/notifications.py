"""Notification system widgets."""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable

from PySide6.QtCore import QObject, QPropertyAnimation, QRect, Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPainter, QPalette
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from qtframework.widgets.buttons import CloseButton
from qtframework.themes.manager import ThemeManager


class NotificationType(Enum):
    """Notification types."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationPosition(Enum):
    """Notification position."""

    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"


class Notification(QFrame):
    """Notification widget."""

    closed = Signal()
    clicked = Signal()

    def __init__(
        self,
        title: str = "",
        message: str = "",
        notification_type: NotificationType = NotificationType.INFO,
        duration: int = 5000,
        closable: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize notification.

        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            duration: Display duration in ms (0 for persistent)
            closable: Show close button
            parent: Parent widget
        """
        super().__init__(parent)

        self._title = title
        self._message = message
        self._type = notification_type
        self._duration = duration
        self._closable = closable

        self._setup_ui()
        self._apply_style()

        if duration > 0:
            QTimer.singleShot(duration, self.close)

    def _setup_ui(self) -> None:
        """Setup UI components."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        # Removed WA_TranslucentBackground to ensure background is visible
        self.setAutoFillBackground(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel()
        icon_text = {
            NotificationType.INFO: "ℹ",
            NotificationType.SUCCESS: "✓",
            NotificationType.WARNING: "⚠",
            NotificationType.ERROR: "✕",
        }
        icon_label.setText(icon_text.get(self._type, ""))
        icon_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        layout.addWidget(icon_label)

        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)

        if self._title:
            title_label = QLabel(self._title)
            title_font = QFont()
            title_font.setBold(True)
            title_label.setFont(title_font)
            content_layout.addWidget(title_label)

        if self._message:
            message_label = QLabel(self._message)
            message_label.setWordWrap(True)
            content_layout.addWidget(message_label)

        layout.addLayout(content_layout, 1)

        # Close button
        if self._closable:
            close_btn = CloseButton(size=20, style="light")
            close_btn.clicked.connect(self.close)
            layout.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignTop)

    def _apply_style(self) -> None:
        """Apply style based on notification type."""
        # Get current theme from application if available
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()

        theme = None
        theme_name = "light"
        if hasattr(app, 'theme_manager'):
            theme = app.theme_manager.get_theme()
            theme_name = app.theme_manager.get_current_theme_name()

        # Use basic colors for notification types
        if "dark" in theme_name or "monokai" in theme_name:
            # Dark theme colors
            color_map = {
                NotificationType.INFO: "#2196f3",
                NotificationType.SUCCESS: "#4caf50",
                NotificationType.WARNING: "#ff9800",
                NotificationType.ERROR: "#f44336",
            }
            text_color = "#ffffff"
        else:
            # Light theme colors
            color_map = {
                NotificationType.INFO: "#0288d1",
                NotificationType.SUCCESS: "#388e3c",
                NotificationType.WARNING: "#f57c00",
                NotificationType.ERROR: "#d32f2f",
            }
            text_color = "#ffffff"

        bg_color = color_map.get(self._type, "#2196f3")

        # Simple consistent styling
        self.setStyleSheet(f"""
            Notification {{
                background-color: {bg_color};
                border: none;
                border-radius: 8px;
                min-width: 300px;
                max-width: 500px;
                min-height: 60px;
                padding: 12px;
            }}
            QLabel {{
                color: {text_color};
                background: transparent;
            }}
        """)

    def show_at(self, position: NotificationPosition, offset: tuple[int, int] = (20, 20)) -> None:
        """Show notification at specific position.

        Args:
            position: Position to show at
            offset: Offset from edge (x, y)
        """
        self.adjustSize()  # Ensure proper sizing
        self.show()
        self.raise_()

        parent = self.parent()
        if not parent:
            return

        parent_rect = parent.rect()
        x, y = offset

        if position == NotificationPosition.TOP_LEFT:
            self.move(x, y)
        elif position == NotificationPosition.TOP_CENTER:
            self.move((parent_rect.width() - self.width()) // 2, y)
        elif position == NotificationPosition.TOP_RIGHT:
            self.move(parent_rect.width() - self.width() - x, y)
        elif position == NotificationPosition.BOTTOM_LEFT:
            self.move(x, parent_rect.height() - self.height() - y)
        elif position == NotificationPosition.BOTTOM_CENTER:
            self.move(
                (parent_rect.width() - self.width()) // 2,
                parent_rect.height() - self.height() - y,
            )
        elif position == NotificationPosition.BOTTOM_RIGHT:
            self.move(
                parent_rect.width() - self.width() - x,
                parent_rect.height() - self.height() - y,
            )

    def animate_in(self) -> None:
        """Animate notification appearance."""
        from PySide6.QtCore import QEasingCurve
        from PySide6.QtWidgets import QGraphicsOpacityEffect

        # Create opacity effect
        self._opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self._opacity_effect)

        # Animate opacity from 0 to 1
        self._animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._animation.setDuration(200)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.start()

    def animate_out(self) -> None:
        """Animate notification disappearance."""
        from PySide6.QtCore import QEasingCurve

        if hasattr(self, '_opacity_effect'):
            # Animate opacity from 1 to 0
            self._animation = QPropertyAnimation(self._opacity_effect, b"opacity")
            self._animation.setDuration(200)
            self._animation.setStartValue(1.0)
            self._animation.setEndValue(0.0)
            self._animation.setEasingCurve(QEasingCurve.Type.InCubic)
            self._animation.finished.connect(self.deleteLater)
            self._animation.start()
        else:
            # If no opacity effect, just delete
            self.deleteLater()

    def close(self) -> None:
        """Close notification."""
        self.closed.emit()
        self.animate_out()

    def mousePressEvent(self, event: Any) -> None:
        """Handle mouse press.

        Args:
            event: Mouse event
        """
        self.clicked.emit()
        super().mousePressEvent(event)


class NotificationManager(QObject):
    """Manager for handling notifications."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize notification manager.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._parent = parent
        self._notifications: list[Notification] = []
        self._position = NotificationPosition.TOP_RIGHT
        self._offset = (20, 20)
        self._spacing = 10
        self._max_notifications = 5

    def set_position(self, position: NotificationPosition) -> None:
        """Set default notification position.

        Args:
            position: Notification position
        """
        self._position = position

    def set_offset(self, x: int, y: int) -> None:
        """Set notification offset.

        Args:
            x: X offset
            y: Y offset
        """
        self._offset = (x, y)

    def notify(
        self,
        title: str = "",
        message: str = "",
        notification_type: NotificationType = NotificationType.INFO,
        duration: int = 5000,
        closable: bool = True,
        on_click: Callable[[], None] | None = None,
    ) -> Notification:
        """Show a notification.

        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            duration: Display duration
            closable: Show close button
            on_click: Click callback

        Returns:
            Notification widget
        """
        # Remove oldest if at max
        if len(self._notifications) >= self._max_notifications:
            oldest = self._notifications.pop(0)
            oldest.close()

        notification = Notification(
            title=title,
            message=message,
            notification_type=notification_type,
            duration=duration,
            closable=closable,
            parent=self._parent,
        )

        if on_click:
            notification.clicked.connect(on_click)

        notification.closed.connect(lambda: self._remove_notification(notification))
        self._notifications.append(notification)

        self._position_notifications()
        notification.show()
        notification.animate_in()

        return notification

    def _remove_notification(self, notification: Notification) -> None:
        """Remove notification from list.

        Args:
            notification: Notification to remove
        """
        if notification in self._notifications:
            self._notifications.remove(notification)
            self._position_notifications()

    def _position_notifications(self) -> None:
        """Reposition all notifications."""
        if not self._parent:
            return

        x, y = self._offset
        current_y = y

        for notification in self._notifications:
            if self._position in [
                NotificationPosition.TOP_LEFT,
                NotificationPosition.TOP_CENTER,
                NotificationPosition.TOP_RIGHT,
            ]:
                notification.show_at(self._position, (x, current_y))
                current_y += notification.height() + self._spacing
            else:
                # Bottom positions - stack upward
                notification.show_at(self._position, (x, current_y))
                current_y += notification.height() + self._spacing

    def info(self, title: str, message: str, **kwargs: Any) -> Notification:
        """Show info notification."""
        return self.notify(title, message, NotificationType.INFO, **kwargs)

    def success(self, title: str, message: str, **kwargs: Any) -> Notification:
        """Show success notification."""
        return self.notify(title, message, NotificationType.SUCCESS, **kwargs)

    def warning(self, title: str, message: str, **kwargs: Any) -> Notification:
        """Show warning notification."""
        return self.notify(title, message, NotificationType.WARNING, **kwargs)

    def error(self, title: str, message: str, **kwargs: Any) -> Notification:
        """Show error notification."""
        return self.notify(title, message, NotificationType.ERROR, **kwargs)

    def clear_all(self) -> None:
        """Clear all notifications."""
        for notification in self._notifications[:]:
            notification.close()