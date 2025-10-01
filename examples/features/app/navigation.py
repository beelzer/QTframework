"""
Navigation panel for the showcase.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QFrame, QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout


class NavigationPanel(QFrame):
    """Navigation panel with feature categories."""

    page_selected = Signal(str)

    def __init__(self, parent=None):
        """Initialize the navigation panel."""
        super().__init__(parent)
        self.parent_window = parent
        self.setObjectName("navigationPanel")
        self.setMaximumWidth(350)
        self.current_search = ""
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Feature Categories")
        title.setProperty("heading", "h2")
        layout.addWidget(title)

        # Search box with embedded clear action
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search features...")
        self.search_box.textChanged.connect(self._filter_tree)

        # Add clear action inside the search box with icon
        self.clear_action = QAction(self.search_box)
        self.clear_action.setIcon(self._create_clear_icon())
        self.clear_action.setToolTip("Clear search")
        self.clear_action.triggered.connect(self._clear_search)
        self.search_box.addAction(self.clear_action, QLineEdit.ActionPosition.TrailingPosition)
        self.clear_action.setVisible(False)  # Hide initially

        layout.addWidget(self.search_box)

        # Navigation tree
        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderHidden(True)
        self.nav_tree.itemClicked.connect(self._on_item_clicked)
        self._populate_tree()
        layout.addWidget(self.nav_tree)

    def _create_clear_icon(self):
        """Load the clear icon from SVG file."""
        # Get the resources directory
        resources_dir = Path(__file__).parent.parent.parent.parent / "resources" / "icons"

        # Try to detect theme and use appropriate icon
        # For now, use the light icon and create both variants
        icon_path = resources_dir / "clear-search.svg"

        if icon_path.exists():
            return QIcon(str(icon_path))
        else:
            # Fallback to empty icon if file not found
            return QIcon()

    def _populate_tree(self):
        """Populate the navigation tree."""
        categories = self._get_categories()

        for category, items in categories.items():
            cat_item = QTreeWidgetItem(self.nav_tree, [category])
            cat_item.setExpanded(True)

            for item in items:
                QTreeWidgetItem(cat_item, [item])

    def _get_categories(self):
        """Get feature categories."""
        return {
            "Core Components": ["Buttons", "Inputs", "Selections", "Display"],
            "Advanced Widgets": ["Tables", "Trees & Lists", "Dialogs", "Notifications"],
            "Layouts": ["Grid Layout", "Flex Layout", "Card Layout", "Sidebar Layout"],
            "Theming": ["Theme Switcher", "Color Palette", "Typography", "Spacing"],
            "Forms": ["Basic Form", "Validation", "Complex Form"],
            "State": ["State Demo", "Actions", "Reducers"],
            "Configuration": ["Config Overview", "Config Editor"],
            "Navigation": ["Router", "Breadcrumbs", "Tabs"],
            "Animations": ["Transitions", "Progress", "Effects"],
            "Internationalization": ["i18n"],
        }

    def _get_page_searchable_content(self, page_name: str) -> str:
        """Get searchable content for a page (sections + text content)."""
        if not self.parent_window or not hasattr(self.parent_window, "content_area"):
            return ""

        content_area = self.parent_window.content_area
        if page_name not in content_area.pages:
            return ""

        # Get the page widget
        page_index = content_area.pages[page_name]
        page_widget = content_area.widget(page_index)

        # Collect searchable text
        from PySide6.QtWidgets import (
            QGroupBox,
            QLabel,
            QPushButton,
            QLineEdit,
            QCheckBox,
            QRadioButton,
        )

        searchable_text = []

        # Add section titles from QGroupBox
        for group_box in page_widget.findChildren(QGroupBox):
            if group_box.title():
                searchable_text.append(group_box.title())

        # Add text from labels
        for label in page_widget.findChildren(QLabel):
            text = label.text()
            if text and not text.startswith("h1"):  # Skip page title
                searchable_text.append(text)

        # Add button text
        for button in page_widget.findChildren(QPushButton):
            if button.text():
                searchable_text.append(button.text())

        # Add placeholder text from line edits
        for line_edit in page_widget.findChildren(QLineEdit):
            if line_edit.placeholderText():
                searchable_text.append(line_edit.placeholderText())

        # Add checkbox/radio button text
        for checkbox in page_widget.findChildren(QCheckBox):
            if checkbox.text():
                searchable_text.append(checkbox.text())

        for radio in page_widget.findChildren(QRadioButton):
            if radio.text():
                searchable_text.append(radio.text())

        return " ".join(searchable_text).lower()

    def _clear_search(self):
        """Clear the search box and highlights."""
        self.search_box.clear()
        # Clear highlights when search is cleared
        self.current_search = ""
        self._highlight_current_page()

    def _filter_tree(self, text: str):
        """Filter tree based on search text."""
        search_text = text.lower()

        # Show/hide clear action
        self.clear_action.setVisible(bool(text))

        # Store current search text for highlighting
        self.current_search = search_text

        for i in range(self.nav_tree.topLevelItemCount()):
            category = self.nav_tree.topLevelItem(i)
            category_matches = search_text in category.text(0).lower()
            has_matching_items = False

            for j in range(category.childCount()):
                item = category.child(j)
                page_name = item.text(0)
                item_matches = search_text in page_name.lower()

                # Also check page content (sections + text)
                content_matches = False
                if search_text and not item_matches:
                    page_content = self._get_page_searchable_content(page_name)
                    content_matches = search_text in page_content

                # Show item if it matches, category matches, or content matches
                matches = item_matches or category_matches or content_matches
                item.setHidden(not matches and text != "")
                if matches or text == "":
                    has_matching_items = True

            # Show category only if it matches OR has matching items
            category_visible = category_matches or has_matching_items
            category.setHidden(not category_visible and text != "")
            if category_visible and text:
                category.setExpanded(True)

        # Trigger highlight update on current page
        if self.parent_window and hasattr(self.parent_window, "content_area"):
            self._highlight_current_page()

    def _highlight_current_page(self):
        """Highlight matching content on the current page."""
        if not self.parent_window or not hasattr(self.parent_window, "content_area"):
            return

        current_widget = self.parent_window.content_area.currentWidget()
        if not current_widget:
            return

        self._apply_search_highlight(current_widget, self.current_search)

    def _apply_search_highlight(self, widget, search_text: str):
        """Apply highlight styling to widgets that match the search text."""
        from PySide6.QtWidgets import QGroupBox, QLabel, QPushButton

        # Clear ALL previous highlights first
        for child in widget.findChildren(QGroupBox):
            child.setProperty("search-match", False)
            child.style().unpolish(child)
            child.style().polish(child)
            child.update()

        for child in widget.findChildren(QLabel):
            child.setProperty("search-match", False)
            child.style().unpolish(child)
            child.style().polish(child)
            child.update()

        for child in widget.findChildren(QPushButton):
            child.setProperty("search-match", False)
            child.style().unpolish(child)
            child.style().polish(child)
            child.update()

        if not search_text:
            widget.update()
            return

        # Apply highlights to matching widgets
        for group_box in widget.findChildren(QGroupBox):
            if group_box.title() and search_text in group_box.title().lower():
                group_box.setProperty("search-match", True)
                group_box.style().unpolish(group_box)
                group_box.style().polish(group_box)
                group_box.update()

        for label in widget.findChildren(QLabel):
            if label.text() and search_text in label.text().lower():
                label.setProperty("search-match", True)
                label.style().unpolish(label)
                label.style().polish(label)
                label.update()

        for button in widget.findChildren(QPushButton):
            if button.text() and search_text in button.text().lower():
                button.setProperty("search-match", True)
                button.style().unpolish(button)
                button.style().polish(button)
                button.update()

        widget.update()

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click."""
        if item.parent():  # Only handle child items
            page_name = item.text(0)
            if self.parent_window and hasattr(self.parent_window, "content_area"):
                self.parent_window.content_area.show_page(page_name)
                self.parent_window.status_bar.showMessage(f"Viewing: {page_name}", 2000)

                # Update properties panel
                from .dockwidgets import log_output, update_properties_for_page

                update_properties_for_page(self.parent_window, page_name)
                log_output(self.parent_window, f"Navigated to: {page_name}")

                # Apply search highlighting to the new page
                self._highlight_current_page()
