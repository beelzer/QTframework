"""
Toolbar configuration for the showcase.
"""

from __future__ import annotations

from PySide6.QtWidgets import QToolBar


def create_toolbars(window):
    """Create application toolbars."""
    # Main toolbar
    main_toolbar = _create_main_toolbar(window)
    window.addToolBar(main_toolbar)

    # Format toolbar
    format_toolbar = _create_format_toolbar(window)
    window.addToolBar(format_toolbar)


def _create_main_toolbar(window):
    """Create the main toolbar."""
    toolbar = QToolBar("Main")

    toolbar.addAction("New")
    toolbar.addAction("Open")
    toolbar.addAction("Save")
    toolbar.addSeparator()
    toolbar.addAction("Cut")
    toolbar.addAction("Copy")
    toolbar.addAction("Paste")
    toolbar.addSeparator()
    toolbar.addAction("Undo")
    toolbar.addAction("Redo")

    return toolbar


def _create_format_toolbar(window):
    """Create the format toolbar."""
    toolbar = QToolBar("Format")

    toolbar.addAction("Bold")
    toolbar.addAction("Italic")
    toolbar.addAction("Underline")
    toolbar.addSeparator()
    toolbar.addAction("Align Left")
    toolbar.addAction("Align Center")
    toolbar.addAction("Align Right")

    return toolbar
