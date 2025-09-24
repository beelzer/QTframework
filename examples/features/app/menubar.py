"""
Menu bar configuration for the showcase.
"""

from __future__ import annotations

from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QMessageBox


def create_menu_bar(window):
    """Create the application menu bar."""
    menubar = window.menuBar()

    # File menu
    file_menu = menubar.addMenu("&File")
    _create_file_menu(window, file_menu)

    # Edit menu
    edit_menu = menubar.addMenu("&Edit")
    _create_edit_menu(window, edit_menu)

    # View menu
    view_menu = menubar.addMenu("&View")
    _create_view_menu(window, view_menu)

    # Theme menu
    theme_menu = menubar.addMenu("&Theme")
    _create_theme_menu(window, theme_menu)

    # Help menu
    help_menu = menubar.addMenu("&Help")
    _create_help_menu(window, help_menu)


def _create_file_menu(window, menu):
    """Create file menu actions."""
    new_action = QAction("&New", window)
    new_action.setShortcut("Ctrl+N")
    menu.addAction(new_action)

    open_action = QAction("&Open", window)
    open_action.setShortcut("Ctrl+O")
    menu.addAction(open_action)

    save_action = QAction("&Save", window)
    save_action.setShortcut("Ctrl+S")
    menu.addAction(save_action)

    menu.addSeparator()

    exit_action = QAction("E&xit", window)
    exit_action.setShortcut("Ctrl+Q")
    exit_action.triggered.connect(window.close)
    menu.addAction(exit_action)


def _create_edit_menu(window, menu):
    """Create edit menu actions."""
    undo_action = QAction("&Undo", window)
    undo_action.setShortcut("Ctrl+Z")
    menu.addAction(undo_action)

    redo_action = QAction("&Redo", window)
    redo_action.setShortcut("Ctrl+Y")
    menu.addAction(redo_action)

    menu.addSeparator()

    cut_action = QAction("Cu&t", window)
    cut_action.setShortcut("Ctrl+X")
    menu.addAction(cut_action)

    copy_action = QAction("&Copy", window)
    copy_action.setShortcut("Ctrl+C")
    menu.addAction(copy_action)

    paste_action = QAction("&Paste", window)
    paste_action.setShortcut("Ctrl+V")
    menu.addAction(paste_action)


def _create_view_menu(window, menu):
    """Create view menu actions."""
    fullscreen_action = QAction("&Fullscreen", window)
    fullscreen_action.setShortcut("F11")
    fullscreen_action.setCheckable(True)
    fullscreen_action.triggered.connect(
        lambda checked: window.showFullScreen() if checked else window.showNormal()
    )
    menu.addAction(fullscreen_action)

    menu.addSeparator()

    zoom_in_action = QAction("Zoom &In", window)
    zoom_in_action.setShortcut("Ctrl++")
    menu.addAction(zoom_in_action)

    zoom_out_action = QAction("Zoom &Out", window)
    zoom_out_action.setShortcut("Ctrl+-")
    menu.addAction(zoom_out_action)

    reset_zoom_action = QAction("&Reset Zoom", window)
    reset_zoom_action.setShortcut("Ctrl+0")
    menu.addAction(reset_zoom_action)


def _create_theme_menu(window, menu):
    """Create theme menu actions."""
    theme_group = QActionGroup(window)

    for theme in window.theme_manager.list_themes():
        theme_action = QAction(theme.capitalize(), window)
        theme_action.setCheckable(True)
        theme_action.triggered.connect(
            lambda checked, t=theme: window.apply_theme(t) if checked else None
        )
        theme_group.addAction(theme_action)
        menu.addAction(theme_action)

        # Check the light theme by default
        if theme == "light":
            theme_action.setChecked(True)


def _create_help_menu(window, menu):
    """Create help menu actions."""
    docs_action = QAction("&Documentation", window)
    docs_action.setShortcut("F1")
    menu.addAction(docs_action)

    menu.addSeparator()

    about_action = QAction("&About", window)
    about_action.triggered.connect(lambda: _show_about(window))
    menu.addAction(about_action)


def _show_about(window):
    """Show about dialog."""
    QMessageBox.about(
        window,
        "About Qt Framework Showcase",
        "Qt Framework Showcase v1.0.0\n\n"
        "A comprehensive demonstration application showcasing "
        "all features and capabilities of our Qt Framework.\n\n"
        "Built with PySide6 and modern design principles.",
    )
