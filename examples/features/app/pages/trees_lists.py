"""
Trees and lists demonstration page.
"""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QListWidget, QTreeWidget, QTreeWidgetItem, QWidget

from qtframework.widgets import ScrollablePage as DemoPage


class TreesListsPage(DemoPage):
    """Page demonstrating tree and list components."""

    def __init__(self):
        """Initialize the trees and lists page."""
        super().__init__("Trees & Lists")
        self._create_content()

    def _create_content(self):
        """Create the page content."""
        # Create horizontal layout for tree and list
        container = QWidget()
        layout = QHBoxLayout(container)

        # Tree widget
        tree = self._create_tree()
        layout.addWidget(tree)

        # List widget
        list_widget = self._create_list()
        layout.addWidget(list_widget)

        self.add_section("", container)
        self.add_stretch()

    def _create_tree(self):
        """Create a tree widget."""
        tree = QTreeWidget()
        tree.setHeaderLabels(["Name", "Type", "Size", "Modified"])

        # Root folder
        root = QTreeWidgetItem(tree, ["Project", "Folder", "", "Today"])

        # Source folder
        src = QTreeWidgetItem(root, ["src", "Folder", "", "Today"])
        QTreeWidgetItem(src, ["main.py", "Python", "2.5 KB", "Yesterday"])
        QTreeWidgetItem(src, ["utils.py", "Python", "1.2 KB", "2 days ago"])
        QTreeWidgetItem(src, ["config.json", "JSON", "0.8 KB", "Last week"])

        # Components folder
        components = QTreeWidgetItem(src, ["components", "Folder", "", "Today"])
        QTreeWidgetItem(components, ["button.py", "Python", "3.1 KB", "Today"])
        QTreeWidgetItem(components, ["input.py", "Python", "2.7 KB", "Today"])

        # Tests folder
        tests = QTreeWidgetItem(root, ["tests", "Folder", "", "Yesterday"])
        QTreeWidgetItem(tests, ["test_main.py", "Python", "3.1 KB", "Yesterday"])
        QTreeWidgetItem(tests, ["test_utils.py", "Python", "2.4 KB", "Yesterday"])

        # Docs folder
        docs = QTreeWidgetItem(root, ["docs", "Folder", "", "Last week"])
        QTreeWidgetItem(docs, ["README.md", "Markdown", "4.2 KB", "Last week"])
        QTreeWidgetItem(docs, ["API.md", "Markdown", "8.5 KB", "Last week"])

        # Expand folders
        root.setExpanded(True)
        src.setExpanded(True)

        return tree

    def _create_list(self):
        """Create a list widget."""
        list_widget = QListWidget()

        items = [
            "📄 Document.pdf",
            "🖼️ Image.png",
            "📊 Spreadsheet.xlsx",
            "📹 Video.mp4",
            "🎵 Audio.mp3",
            "📦 Archive.zip",
            "📝 Notes.txt",
            "🎨 Design.psd",
            "💾 Database.db",
            "⚙️ Settings.ini",
            "🔒 Secure.key",
            "📈 Report.csv",
        ]

        list_widget.addItems(items)
        list_widget.setCurrentRow(0)

        return list_widget
