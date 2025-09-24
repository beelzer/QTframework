"""
Navigation panel for the showcase.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
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
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Feature Categories")
        title.setProperty("heading", "h2")
        layout.addWidget(title)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search features...")
        self.search_box.textChanged.connect(self._filter_tree)
        layout.addWidget(self.search_box)

        # Navigation tree
        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderHidden(True)
        self.nav_tree.itemClicked.connect(self._on_item_clicked)
        self._populate_tree()
        layout.addWidget(self.nav_tree)

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
            "Navigation": ["Router", "Breadcrumbs", "Tabs"],
            "Animations": ["Transitions", "Progress", "Effects"],
        }

    def _filter_tree(self, text: str):
        """Filter tree based on search text."""
        for i in range(self.nav_tree.topLevelItemCount()):
            category = self.nav_tree.topLevelItem(i)
            category_visible = False

            for j in range(category.childCount()):
                item = category.child(j)
                matches = text.lower() in item.text(0).lower()
                item.setHidden(not matches and text != "")
                if matches or text == "":
                    category_visible = True

            category.setHidden(not category_visible and text != "")
            if category_visible and text:
                category.setExpanded(True)

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
