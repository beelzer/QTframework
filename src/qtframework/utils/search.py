"""Search and highlighting utilities.

This module provides utilities for searching and highlighting content
in widget hierarchies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
)

from qtframework.utils.styling import refresh_widget_style


if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtWidgets import (
        QWidget,
    )


class SearchHighlighter:
    """Utility for highlighting search matches in widget hierarchies.

    Example:
        ```python
        highlighter = SearchHighlighter()
        highlighter.highlight(my_widget, "search text")
        # Later...
        highlighter.clear(my_widget)
        ```
    """

    def __init__(self, property_name: str = "search-match"):
        """Initialize the search highlighter.

        Args:
            property_name: The property name to set for styling (default: "search-match")
        """
        self.property_name = property_name
        self.supported_widgets = {
            QGroupBox: lambda w: w.title(),
            QLabel: lambda w: w.text(),
            QPushButton: lambda w: w.text(),
            QLineEdit: lambda w: w.placeholderText(),
            QCheckBox: lambda w: w.text(),
            QRadioButton: lambda w: w.text(),
        }

    def add_widget_support(self, widget_type: type, text_getter: Callable[[QWidget], str]) -> None:
        """Add support for custom widget types.

        Args:
            widget_type: The widget class to support
            text_getter: Function that extracts searchable text from the widget
        """
        self.supported_widgets[widget_type] = text_getter

    def highlight(
        self,
        root_widget: QWidget,
        search_text: str,
        case_sensitive: bool = False,
        fuzzy: bool = False,
    ) -> int:
        """Highlight matching widgets in the hierarchy.

        Args:
            root_widget: The root widget to search within
            search_text: The text to search for
            case_sensitive: Whether the search should be case-sensitive
            fuzzy: Whether to use fuzzy matching (future enhancement)

        Returns:
            Number of matches found
        """
        if not search_text:
            self.clear(root_widget)
            return 0

        match_count = 0
        search_lower = search_text if case_sensitive else search_text.lower()

        for widget_type, text_getter in self.supported_widgets.items():
            for widget in root_widget.findChildren(widget_type):
                text = text_getter(widget)
                if text:
                    text_to_match = text if case_sensitive else text.lower()
                    if search_lower in text_to_match:
                        widget.setProperty(self.property_name, True)
                        refresh_widget_style(widget)
                        match_count += 1

        return match_count

    def clear(self, root_widget: QWidget) -> None:
        """Clear all highlights in the widget hierarchy.

        Args:
            root_widget: The root widget to clear highlights from
        """
        for widget_type in self.supported_widgets:
            for widget in root_widget.findChildren(widget_type):
                widget.setProperty(self.property_name, False)
                refresh_widget_style(widget)

        root_widget.update()


class SearchableMixin:
    """Mixin to make any widget searchable and highlightable.

    Example:
        ```python
        class MyWidget(QWidget, SearchableMixin):
            def __init__(self):
                super().__init__()
                self.enable_search_highlighting()

            def search(self, text):
                return self._search_highlighter.highlight(self, text)
        ```
    """

    def enable_search_highlighting(self, property_name: str = "search-match") -> None:
        """Enable search highlighting for this widget.

        Args:
            property_name: The property name to use for styling
        """
        self._search_highlighter = SearchHighlighter(property_name)

    def search(self, text: str, case_sensitive: bool = False, fuzzy: bool = False) -> int:
        """Search and highlight matches in this widget.

        Args:
            text: The text to search for
            case_sensitive: Whether the search should be case-sensitive
            fuzzy: Whether to use fuzzy matching

        Returns:
            Number of matches found
        """
        if not hasattr(self, "_search_highlighter"):
            self.enable_search_highlighting()
        return self._search_highlighter.highlight(self, text, case_sensitive, fuzzy)

    def clear_search(self) -> None:
        """Clear search highlights."""
        if hasattr(self, "_search_highlighter"):
            self._search_highlighter.clear(self)


def collect_searchable_text(widget: QWidget, include_placeholders: bool = True) -> str:
    """Collect all searchable text from a widget hierarchy.

    Args:
        widget: The root widget to collect text from
        include_placeholders: Whether to include placeholder text from inputs

    Returns:
        Concatenated searchable text
    """
    # Add section titles from QGroupBox
    searchable_text = [
        group_box.title() for group_box in widget.findChildren(QGroupBox) if group_box.title()
    ]

    # Add text from labels
    for label in widget.findChildren(QLabel):
        text = label.text()
        if text:
            searchable_text.append(text)

    # Add button text
    searchable_text.extend(
        button.text() for button in widget.findChildren(QPushButton) if button.text()
    )

    if include_placeholders:
        # Add placeholder text from line edits
        searchable_text.extend(
            line_edit.placeholderText()
            for line_edit in widget.findChildren(QLineEdit)
            if line_edit.placeholderText()
        )

    # Add checkbox/radio button text
    searchable_text.extend(
        checkbox.text() for checkbox in widget.findChildren(QCheckBox) if checkbox.text()
    )

    searchable_text.extend(
        radio.text() for radio in widget.findChildren(QRadioButton) if radio.text()
    )

    return " ".join(searchable_text)
