"""Layouts demonstration page."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from qtframework.widgets import ScrollablePage as DemoPage


class LayoutsPage(DemoPage):
    """Page demonstrating layout systems."""

    def __init__(self, layout_type: str = "grid"):
        """Initialize the layouts page."""
        self.layout_type = layout_type
        title = f"{layout_type.capitalize()} Layout"
        super().__init__(title)
        self._create_content()

    def _create_content(self):
        """Create the page content based on layout type."""
        if self.layout_type == "grid":
            self._create_grid_layout()
        elif self.layout_type == "flex":
            self._create_flex_layout()
        elif self.layout_type == "card":
            self._create_card_layout()
        elif self.layout_type == "sidebar":
            self._create_sidebar_layout()

        self.add_stretch()

    def _create_grid_layout(self):
        """Create grid layout example."""
        group = QGroupBox("Grid Layout Example")
        layout = QGridLayout()

        # Create grid items
        for i in range(3):
            for j in range(4):
                card = self._create_card(f"Cell [{i},{j}]", f"Grid item at position {i},{j}")
                layout.addWidget(card, i, j)

        group.setLayout(layout)
        self.content_layout.addWidget(group)

        # Spanning example
        span_group = QGroupBox("Grid with Spanning")
        span_layout = QGridLayout()

        # Header spanning full width
        header = self._create_card("Header", "Spans full width")
        span_layout.addWidget(header, 0, 0, 1, 3)

        # Sidebar spanning 2 rows
        sidebar = self._create_card("Sidebar", "Spans 2 rows")
        span_layout.addWidget(sidebar, 1, 0, 2, 1)

        # Content area
        content = self._create_card("Content", "Main content area")
        span_layout.addWidget(content, 1, 1, 1, 2)

        # Footer
        footer = self._create_card("Footer", "Bottom section")
        span_layout.addWidget(footer, 2, 1, 1, 2)

        span_group.setLayout(span_layout)
        self.content_layout.addWidget(span_group)

    def _create_flex_layout(self):
        """Create flex layout example."""
        # Horizontal flex
        h_group = QGroupBox("Horizontal Flex Layout")
        h_layout = QHBoxLayout()

        for i in range(4):
            card = self._create_card(f"Flex {i + 1}", "Flexible width")
            h_layout.addWidget(card)

        h_group.setLayout(h_layout)
        self.content_layout.addWidget(h_group)

        # Vertical flex
        v_group = QGroupBox("Vertical Flex Layout")
        v_layout = QVBoxLayout()

        for i in range(3):
            card = self._create_card(f"Item {i + 1}", "Stacked vertically")
            v_layout.addWidget(card)

        v_group.setLayout(v_layout)
        self.content_layout.addWidget(v_group)

    def _create_card_layout(self):
        """Create card layout example."""
        group = QGroupBox("Card Layout")
        layout = QHBoxLayout()

        for i in range(3):
            card = QFrame()
            card.setProperty("card", "true")
            card_layout = QVBoxLayout(card)

            # Card header
            header = QLabel(f"Card {i + 1}")
            header.setProperty("heading", "h3")
            card_layout.addWidget(header)

            # Card content
            content = QLabel("This is a card component with header, content, and actions.")
            content.setWordWrap(True)
            card_layout.addWidget(content)

            # Card actions
            actions_layout = QHBoxLayout()
            primary_btn = QPushButton("Primary")
            primary_btn.setProperty("variant", "primary")
            secondary_btn = QPushButton("Secondary")
            actions_layout.addWidget(primary_btn)
            actions_layout.addWidget(secondary_btn)
            card_layout.addLayout(actions_layout)

            layout.addWidget(card)

        group.setLayout(layout)
        self.content_layout.addWidget(group)

    def _create_sidebar_layout(self):
        """Create sidebar layout example."""
        group = QGroupBox("Sidebar Layout")
        layout = QHBoxLayout()

        # Sidebar
        sidebar = QFrame()
        sidebar.setProperty("card", "true")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)

        sidebar_title = QLabel("Sidebar")
        sidebar_title.setProperty("heading", "h3")
        sidebar_layout.addWidget(sidebar_title)

        # Sidebar items
        for i in range(5):
            item = QPushButton(f"Menu Item {i + 1}")
            item.setProperty("variant", "ghost")
            sidebar_layout.addWidget(item)

        sidebar_layout.addStretch()
        layout.addWidget(sidebar)

        # Main content
        content = QFrame()
        content.setProperty("card", "true")
        content_layout = QVBoxLayout(content)

        content_title = QLabel("Main Content")
        content_title.setProperty("heading", "h2")
        content_layout.addWidget(content_title)

        content_text = QLabel(
            "This is the main content area. It takes up the remaining space "
            "after the sidebar. The sidebar has a fixed width while the content "
            "area is flexible and responsive."
        )
        content_text.setWordWrap(True)
        content_layout.addWidget(content_text)

        content_layout.addStretch()
        layout.addWidget(content, 1)  # Stretch factor 1

        group.setLayout(layout)
        self.content_layout.addWidget(group)

    def _create_card(self, title: str, description: str):
        """Create a simple card widget."""
        card = QFrame()
        card.setProperty("card", "true")
        layout = QVBoxLayout(card)

        title_label = QLabel(title)
        title_label.setProperty("heading", "h3")
        layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setProperty("secondary", "true")
        layout.addWidget(desc_label)

        return card
