"""
Content area manager for the showcase.
"""

from __future__ import annotations

from PySide6.QtWidgets import QStackedWidget

from .pages.animations import AnimationsPage
from .pages.buttons import ButtonsPage
from .pages.dialogs import DialogsPage
from .pages.display import DisplayPage
from .pages.forms import FormsPage
from .pages.inputs import InputsPage
from .pages.layouts import LayoutsPage
from .pages.selections import SelectionsPage
from .pages.state import StatePage
from .pages.tables import TablesPage
from .pages.theming import ThemingPage
from .pages.trees_lists import TreesListsPage


class ContentArea(QStackedWidget):
    """Content area with stacked pages."""

    def __init__(self, parent=None):
        """Initialize the content area."""
        super().__init__(parent)
        self.parent_window = parent
        self.pages = {}
        self._init_pages()

    def _init_pages(self):
        """Initialize all content pages."""
        # Core components
        self.add_page("Buttons", ButtonsPage())
        self.add_page("Inputs", InputsPage())
        self.add_page("Selections", SelectionsPage())
        self.add_page("Display", DisplayPage())

        # Advanced widgets
        self.add_page("Tables", TablesPage())
        self.add_page("Trees & Lists", TreesListsPage())
        self.add_page("Dialogs", DialogsPage(self.parent_window))

        # Layouts
        self.add_page("Grid Layout", LayoutsPage("grid"))
        self.add_page("Flex Layout", LayoutsPage("flex"))
        self.add_page("Card Layout", LayoutsPage("card"))
        self.add_page("Sidebar Layout", LayoutsPage("sidebar"))

        # Theming
        self.add_page("Theme Switcher", ThemingPage(self.parent_window))
        self.add_page("Color Palette", ThemingPage(self.parent_window, "palette"))
        self.add_page("Typography", ThemingPage(self.parent_window, "typography"))

        # Forms
        self.add_page("Basic Form", FormsPage("basic"))
        self.add_page("Validation", FormsPage("validation"))
        self.add_page("Complex Form", FormsPage("complex"))

        # State
        self.add_page("State Demo", StatePage(self.parent_window))

        # Animations
        self.add_page("Transitions", AnimationsPage("transitions"))
        self.add_page("Progress", AnimationsPage("progress"))
        self.add_page("Effects", AnimationsPage("effects"))

        # Show first page (Buttons) by default
        self.setCurrentIndex(0)

    def add_page(self, name: str, widget):
        """Add a page to the stack."""
        index = self.addWidget(widget)
        self.pages[name] = index

    def show_page(self, name: str):
        """Show a specific page by name."""
        if name in self.pages:
            self.setCurrentIndex(self.pages[name])
