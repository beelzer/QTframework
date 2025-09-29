"""Card layout components."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class Card(QFrame):
    """Card container widget."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str = "",
        elevated: bool = True,
        padding: int = 16,
        object_name: str | None = None,
    ) -> None:
        """Initialize card.

        Args:
            parent: Parent widget
            title: Card title
            elevated: Show elevation shadow
            padding: Content padding
            object_name: Object name for styling
        """
        super().__init__(parent)

        if object_name:
            self.setObjectName(object_name)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(padding, padding, padding, padding)
        self._layout.setSpacing(12)

        self._title_label: QLabel | None = None
        if title:
            self.set_title(title)

        self.setProperty("class", "card elevated" if elevated else "card")

        self.setFrameStyle(QFrame.Shape.Box)

    def set_title(self, title: str) -> None:
        """Set card title.

        Args:
            title: Title text
        """
        if not self._title_label:
            self._title_label = QLabel()
            self._title_label.setProperty("class", "card-title")
            self._layout.insertWidget(0, self._title_label)

        self._title_label.setText(title)

    def add_widget(self, widget: QWidget, stretch: int = 0) -> None:
        """Add widget to card.

        Args:
            widget: Widget to add
            stretch: Stretch factor
        """
        self._layout.addWidget(widget, stretch)

    def add_stretch(self, stretch: int = 1) -> None:
        """Add stretch to card.

        Args:
            stretch: Stretch factor
        """
        self._layout.addStretch(stretch)

    def set_content_margins(self, left: int, top: int, right: int, bottom: int) -> None:
        """Set content margins.

        Args:
            left: Left margin
            top: Top margin
            right: Right margin
            bottom: Bottom margin
        """
        self._layout.setContentsMargins(left, top, right, bottom)

    def set_spacing(self, spacing: int) -> None:
        """Set content spacing.

        Args:
            spacing: Spacing between widgets
        """
        self._layout.setSpacing(spacing)


class CardLayout(QWidget):
    """Layout for arranging cards."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        columns: int = 3,
        spacing: int = 16,
        responsive: bool = True,
    ) -> None:
        """Initialize card layout.

        Args:
            parent: Parent widget
            columns: Number of columns
            spacing: Spacing between cards
            responsive: Enable responsive layout
        """
        super().__init__(parent)

        self._columns = columns
        self._spacing = spacing
        self._responsive = responsive
        self._cards: list[Card] = []

        self._setup_layout()

    def _setup_layout(self) -> None:
        """Setup layout."""
        from qtframework.layouts.base import GridLayout

        self._layout = GridLayout(spacing=self._spacing, parent=self)
        self._update_layout()

    def add_card(
        self,
        card: Card | None = None,
        *,
        title: str = "",
        content: QWidget | None = None,
    ) -> Card:
        """Add a card to the layout.

        Args:
            card: Existing card or None to create new
            title: Card title (if creating new)
            content: Card content (if creating new)

        Returns:
            Added card
        """
        if card is None:
            card = Card(title=title)
            if content:
                card.add_widget(content)

        self._cards.append(card)
        self._update_layout()
        return card

    def remove_card(self, card: Card) -> None:
        """Remove a card from the layout.

        Args:
            card: Card to remove
        """
        if card in self._cards:
            self._cards.remove(card)
            self._layout.removeWidget(card)
            card.setParent(None)
            self._update_layout()

    def clear_cards(self) -> None:
        """Remove all cards."""
        for card in self._cards[:]:
            self.remove_card(card)

    def _update_layout(self) -> None:
        """Update card positions in layout."""
        for i, card in enumerate(self._cards):
            row = i // self._columns
            col = i % self._columns
            self._layout.add_widget(card, row, col)

        for col in range(self._columns):
            self._layout.set_column_stretch(col, 1)

    def resizeEvent(self, event: Any) -> None:
        """Handle resize event.

        Args:
            event: Resize event
        """
        super().resizeEvent(event)

        if self._responsive:
            width = self.width()
            if width < 600:
                new_columns = 1
            elif width < 900:
                new_columns = 2
            elif width < 1200:
                new_columns = 3
            else:
                new_columns = 4

            if new_columns != self._columns:
                self._columns = new_columns
                self._update_layout()
