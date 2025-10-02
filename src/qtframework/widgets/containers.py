"""Container widgets for organizing UI elements.

This module provides reusable container widgets like Cards for creating
structured, visually consistent layouts.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from qtframework.utils.styling import set_heading_level, set_widget_property


class Card(QFrame):
    """A styled card container widget.

    Cards are a common UI pattern for grouping related content with
    consistent styling and optional title/actions.

    Example:
        ```python
        card = Card("Settings")
        card.add_content(QLabel("Your settings here"))
        card.add_action(QPushButton("Save"))
        ```
    """

    def __init__(self, title: str = "", parent: QWidget | None = None):
        """Initialize a card widget.

        Args:
            title: Optional title for the card
            parent: Parent widget
        """
        super().__init__(parent)
        set_widget_property(self, "card", "true")

        self._layout = QVBoxLayout(self)
        self._title_label: QLabel | None = None
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._actions_widget: QWidget | None = None
        self._actions_layout: QHBoxLayout | None = None

        if title:
            self._title_label = QLabel(title)
            set_heading_level(self._title_label, 3)
            self._layout.addWidget(self._title_label)

        self._layout.addWidget(self._content_widget)

    def set_title(self, title: str) -> None:
        """Set or update the card title.

        Args:
            title: The title text
        """
        if not self._title_label:
            self._title_label = QLabel()
            set_heading_level(self._title_label, 3)
            self._layout.insertWidget(0, self._title_label)
        self._title_label.setText(title)

    def add_content(self, widget: QWidget) -> None:
        """Add content to the card.

        Args:
            widget: The widget to add
        """
        self._content_layout.addWidget(widget)

    def add_stretch(self) -> None:
        """Add a stretch to the content layout."""
        self._content_layout.addStretch()

    def add_action(self, button: QPushButton) -> None:
        """Add an action button to the card footer.

        Args:
            button: The button to add
        """
        if not self._actions_widget:
            self._actions_widget = QWidget()
            self._actions_layout = QHBoxLayout(self._actions_widget)
            self._actions_layout.setContentsMargins(0, 0, 0, 0)
            self._actions_layout.addStretch()
            self._layout.addWidget(self._actions_widget)

        if self._actions_layout:
            self._actions_layout.addWidget(button)

    def set_elevated(self, elevated: bool = True) -> None:
        """Set elevated style for shadow effect.

        Args:
            elevated: Whether the card should appear elevated
        """
        set_widget_property(self, "elevated", "true" if elevated else "false")

    def content_layout(self) -> QVBoxLayout:
        """Get the content layout for direct manipulation."""
        return self._content_layout


class InfoCard(Card):
    """A card with an icon and info layout.

    Example:
        ```python
        card = InfoCard("Status", icon_text="✓")
        card.set_info("All systems operational")
        ```
    """

    def __init__(
        self,
        title: str = "",
        icon_text: str = "",
        parent: QWidget | None = None,
    ):
        """Initialize an info card.

        Args:
            title: Card title
            icon_text: Icon character or emoji
            parent: Parent widget
        """
        super().__init__(title, parent)

        self._info_widget = QWidget()
        info_layout = QHBoxLayout(self._info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)

        if icon_text:
            self._icon_label = QLabel(icon_text)
            self._icon_label.setProperty("heading", "h1")
            info_layout.addWidget(self._icon_label)

        self._info_label = QLabel()
        self._info_label.setWordWrap(True)
        info_layout.addWidget(self._info_label, 1)

        self.add_content(self._info_widget)

    def set_info(self, text: str) -> None:
        """Set the info text.

        Args:
            text: The information text to display
        """
        self._info_label.setText(text)

    def set_icon(self, icon_text: str) -> None:
        """Update the icon.

        Args:
            icon_text: Icon character or emoji
        """
        if hasattr(self, "_icon_label"):
            self._icon_label.setText(icon_text)


class StatCard(Card):
    """A card for displaying statistics.

    Example:
        ```python
        card = StatCard("Users", "1,234", "↑ 12% from last month")
        ```
    """

    def __init__(
        self,
        title: str = "",
        value: str = "",
        subtitle: str = "",
        parent: QWidget | None = None,
    ):
        """Initialize a stat card.

        Args:
            title: Card title
            value: The main statistic value
            subtitle: Optional subtitle or description
            parent: Parent widget
        """
        super().__init__(title, parent)

        self._value_label = QLabel(value)
        self._value_label.setProperty("heading", "h1")
        self.add_content(self._value_label)

        if subtitle:
            self._subtitle_label = QLabel(subtitle)
            self._subtitle_label.setProperty("secondary", "true")
            self.add_content(self._subtitle_label)

    def set_value(self, value: str) -> None:
        """Update the statistic value.

        Args:
            value: The new value
        """
        self._value_label.setText(value)

    def set_subtitle(self, subtitle: str) -> None:
        """Update the subtitle.

        Args:
            subtitle: The new subtitle
        """
        if hasattr(self, "_subtitle_label"):
            self._subtitle_label.setText(subtitle)


class CollapsibleCard(Card):
    """A card that can be collapsed and expanded.

    Example:
        ```python
        card = CollapsibleCard("Advanced Settings")
        card.add_content(settings_widget)
        card.expanded_changed.connect(lambda e: print(f"Expanded: {e}"))
        ```
    """

    expanded_changed = Signal(bool)

    def __init__(
        self,
        title: str = "",
        expanded: bool = True,
        parent: QWidget | None = None,
    ):
        """Initialize a collapsible card.

        Args:
            title: Card title
            expanded: Initial expanded state
            parent: Parent widget
        """
        super().__init__(title, parent)

        self._expanded = expanded
        self._toggle_button = QPushButton("▼" if expanded else "▶")
        self._toggle_button.setFixedSize(20, 20)
        self._toggle_button.clicked.connect(self._toggle)

        # Insert toggle button in title area
        if self._title_label:
            title_widget = QWidget()
            title_layout = QHBoxLayout(title_widget)
            title_layout.setContentsMargins(0, 0, 0, 0)

            # Remove title label from main layout and add to horizontal layout
            self._layout.removeWidget(self._title_label)
            title_layout.addWidget(self._title_label)
            title_layout.addStretch()
            title_layout.addWidget(self._toggle_button)

            self._layout.insertWidget(0, title_widget)

        self._content_widget.setVisible(expanded)

    def _toggle(self) -> None:
        """Toggle the collapsed state."""
        self._expanded = not self._expanded
        self._content_widget.setVisible(self._expanded)
        self._toggle_button.setText("▼" if self._expanded else "▶")
        self.expanded_changed.emit(self._expanded)

    def set_collapsed(self, collapsed: bool) -> None:
        """Set the collapsed state.

        Args:
            collapsed: True to collapse, False to expand
        """
        if collapsed == self._expanded:
            self._toggle()

    def is_expanded(self) -> bool:
        """Check if the card is expanded."""
        return self._expanded
