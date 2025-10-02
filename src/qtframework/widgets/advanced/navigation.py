"""Navigation widgets for building application navigation.

This module provides widgets for creating hierarchical navigation
with search and filtering capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

# SearchHighlighter and collect_searchable_text are available for use
from qtframework.utils.styling import set_heading_level


if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import (
        QWidget,
    )


@dataclass
class NavigationItem:
    """Data class for navigation items."""

    name: str
    icon: QIcon | None = None
    children: list[NavigationItem] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class NavigationPanel(QFrame):
    """Tree-based navigation panel with search and content matching.

    Provides hierarchical navigation with categories and items, real-time search
    with content matching, and visual highlighting of results.

    Example:
        ```python
        nav = NavigationPanel()
        nav.set_items([
            NavigationItem(
                "Settings",
                children=[
                    NavigationItem("General"),
                    NavigationItem("Advanced"),
                ],
            ),
        ])
        nav.item_selected.connect(lambda name: print(f"Selected: {name}"))
        ```
    """

    item_selected = Signal(str)  # Emits item name when selected

    def __init__(
        self,
        parent: QWidget | None = None,
        title: str = "Navigation",
        max_width: int = 350,
    ):
        """Initialize the navigation panel.

        Args:
            parent: Parent widget
            title: Panel title
            max_width: Maximum width of the panel
        """
        super().__init__(parent)
        self.setObjectName("navigationPanel")
        self.setMaximumWidth(max_width)
        self.current_search = ""
        self._content_provider: Callable[[str], str] | None = None
        self._selection_callback: Callable[[str], None] | None = None
        self._clear_icon: QIcon | None = None
        self._title = title
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel(self._title)
        set_heading_level(title, 2)
        layout.addWidget(title)

        # Search box with embedded clear action
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.textChanged.connect(self._filter_tree)

        # Add clear action inside the search box
        self.clear_action = QAction(self.search_box)
        if self._clear_icon:
            self.clear_action.setIcon(self._clear_icon)
        self.clear_action.setToolTip("Clear search")
        self.clear_action.triggered.connect(self._clear_search)
        self.search_box.addAction(self.clear_action, QLineEdit.ActionPosition.TrailingPosition)
        self.clear_action.setVisible(False)  # Hide initially

        layout.addWidget(self.search_box)

        # Navigation tree
        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderHidden(True)
        self.nav_tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.nav_tree)

    def set_clear_icon(self, icon: QIcon) -> None:
        """Set the clear button icon.

        Args:
            icon: The icon to use for the clear button
        """
        self._clear_icon = icon
        if self.clear_action:
            self.clear_action.setIcon(icon)

    def set_items(self, items: list[NavigationItem]) -> None:
        """Set navigation items from data structure.

        Args:
            items: List of top-level navigation items
        """
        self.nav_tree.clear()
        for item in items:
            self._add_tree_item(None, item)

        # Expand all top-level items by default
        for i in range(self.nav_tree.topLevelItemCount()):
            self.nav_tree.topLevelItem(i).setExpanded(True)

    def _add_tree_item(
        self, parent: QTreeWidgetItem | None, item: NavigationItem
    ) -> QTreeWidgetItem:
        """Add a navigation item to the tree."""
        if parent:
            tree_item = QTreeWidgetItem(parent, [item.name])
        else:
            tree_item = QTreeWidgetItem(self.nav_tree, [item.name])

        if item.icon:
            tree_item.setIcon(0, item.icon)

        # Store metadata
        if item.metadata:
            for key, value in item.metadata.items():
                tree_item.setData(0, Qt.UserRole + hash(key) % 100, value)

        # Add children recursively
        for child in item.children:
            self._add_tree_item(tree_item, child)

        return tree_item

    def set_content_provider(self, provider: Callable[[str], str]) -> None:
        """Set a content provider function for deep content search.

        The provider should return searchable text content for a given item name.

        Args:
            provider: Function that takes item name and returns searchable content
        """
        self._content_provider = provider

    def set_selection_callback(self, callback: Callable[[str], None]) -> None:
        """Set a callback to be called when an item is selected.

        Args:
            callback: Function to call with the selected item name
        """
        self._selection_callback = callback

    def _clear_search(self) -> None:
        """Clear the search box and highlights."""
        self.search_box.clear()
        self.current_search = ""

    def _filter_tree(self, text: str) -> None:
        """Filter tree based on search text."""
        search_text = text.lower()

        # Show/hide clear action
        self.clear_action.setVisible(bool(text))

        # Store current search text
        self.current_search = search_text

        for i in range(self.nav_tree.topLevelItemCount()):
            category = self.nav_tree.topLevelItem(i)
            self._filter_item(category, search_text, text)

    def _filter_item(self, item: QTreeWidgetItem, search_text: str, original_text: str) -> bool:
        """Filter a tree item and its children.

        Returns True if item or any child matches.
        """
        item_matches = search_text in item.text(0).lower()
        has_matching_children = False

        # Check children recursively
        for i in range(item.childCount()):
            child = item.child(i)
            child_matches = self._filter_item(child, search_text, original_text)
            if child_matches:
                has_matching_children = True

        # Check content if provider is available and item doesn't match by name
        content_matches = False
        if (
            search_text
            and not item_matches
            and self._content_provider
            and item.childCount() == 0  # Only check leaf items
        ):
            content = self._content_provider(item.text(0))
            content_matches = search_text in content.lower()

        # Item is visible if it matches, has matching children, or content matches
        matches = item_matches or has_matching_children or content_matches
        item.setHidden(not matches and original_text != "")

        # Expand categories that have matches
        if matches and original_text and item.childCount() > 0:
            item.setExpanded(True)

        return matches

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle item click."""
        # Only handle leaf items (no children)
        if item.childCount() == 0:
            item_name = item.text(0)
            self.item_selected.emit(item_name)

            if self._selection_callback:
                self._selection_callback(item_name)

    def expand_all(self) -> None:
        """Expand all tree items."""
        self.nav_tree.expandAll()

    def collapse_all(self) -> None:
        """Collapse all tree items."""
        self.nav_tree.collapseAll()

    def save_state(self) -> dict:
        """Save navigation state for persistence.

        Returns:
            Dictionary containing expanded states
        """
        state = {"expanded": []}

        def collect_expanded(item: QTreeWidgetItem, path: str = ""):
            current_path = f"{path}/{item.text(0)}" if path else item.text(0)
            if item.isExpanded():
                state["expanded"].append(current_path)

            for i in range(item.childCount()):
                collect_expanded(item.child(i), current_path)

        for i in range(self.nav_tree.topLevelItemCount()):
            collect_expanded(self.nav_tree.topLevelItem(i))

        return state

    def restore_state(self, state: dict) -> None:
        """Restore navigation state.

        Args:
            state: Dictionary containing expanded states from save_state()
        """
        expanded_paths = state.get("expanded", [])

        def restore_expanded(item: QTreeWidgetItem, path: str = ""):
            current_path = f"{path}/{item.text(0)}" if path else item.text(0)
            if current_path in expanded_paths:
                item.setExpanded(True)

            for i in range(item.childCount()):
                restore_expanded(item.child(i), current_path)

        for i in range(self.nav_tree.topLevelItemCount()):
            restore_expanded(self.nav_tree.topLevelItem(i))
