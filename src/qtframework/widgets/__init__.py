"""Reusable widget components.

This module provides a comprehensive collection of modern, themeable UI widgets
for building Qt applications. All widgets support the framework's theming system
and follow consistent design patterns.

Quick Start:
    Creating and using widgets::

        from qtframework.widgets import Button, Input, Badge
        from PySide6.QtWidgets import QVBoxLayout, QWidget

        # Create a container
        container = QWidget()
        layout = QVBoxLayout(container)

        # Add themed button
        button = Button(text="Click Me", variant="primary", size="medium")
        button.clicked.connect(lambda: print("Button clicked!"))
        layout.addWidget(button)

        # Add input with validation
        email_input = Input(
            label="Email", placeholder="Enter your email", required=True
        )
        layout.addWidget(email_input)

        # Add status badge
        badge = Badge(text="New", variant="success")
        layout.addWidget(badge)

Architecture Overview:
    Widget Hierarchy::

        Widget (base class)
        ├── Button
        │   ├── IconButton
        │   ├── ToggleButton
        │   └── CloseButton
        ├── Input
        │   ├── PasswordInput
        │   ├── SearchInput
        │   └── TextArea
        ├── Badge
        │   └── CountBadge
        └── [other widgets...]

    All widgets inherit from the base :class:`Widget` class which provides:
    - Theme integration and automatic style updates
    - Consistent API and properties
    - Accessibility support
    - Signal/slot infrastructure

Widget Categories:
    - **Buttons**: Interactive action triggers (Button, IconButton, ToggleButton)
    - **Inputs**: Text entry and forms (Input, TextArea, PasswordInput)
    - **Display**: Information display (Badge, CountBadge, Label)
    - **Layout**: Container widgets (Card, Panel, Container)
    - **Navigation**: Navigation components (Tabs, Breadcrumb, Menu)
    - **Feedback**: User feedback (ProgressBar, Spinner, Toast)

See Also:
    :mod:`qtframework.themes`: Theming system for styling widgets
    :mod:`qtframework.layouts`: Layout components for organizing widgets
    :mod:`qtframework.utils.validation`: Input validation framework
"""

from __future__ import annotations

from qtframework.widgets.badge import Badge, BadgeVariant
from qtframework.widgets.base import Widget
from qtframework.widgets.buttons import Button, CloseButton, IconButton, ToggleButton
from qtframework.widgets.code_display import (
    CodeDisplay,
    CodeHighlighter,
    JavaScriptHighlighter,
    PythonHighlighter,
)
from qtframework.widgets.color_swatch import (
    ColorPaletteWidget,
    ColorSwatch,
    LargeColorSwatch,
)
from qtframework.widgets.config_editor import ConfigEditorWidget, ConfigFieldDescriptor
from qtframework.widgets.containers import Card, CollapsibleCard, InfoCard, StatCard
from qtframework.widgets.count_badge import CountBadge
from qtframework.widgets.inputs import Input, PasswordInput, SearchInput, TextArea
from qtframework.widgets.pages import NonScrollablePage, ScrollablePage


__all__ = [
    "Badge",
    "BadgeVariant",
    "Button",
    "Card",
    "CloseButton",
    "CodeDisplay",
    "CodeHighlighter",
    "CollapsibleCard",
    "ColorPaletteWidget",
    "ColorSwatch",
    "ConfigEditorWidget",
    "ConfigFieldDescriptor",
    "CountBadge",
    "IconButton",
    "InfoCard",
    "Input",
    "JavaScriptHighlighter",
    "LargeColorSwatch",
    "NonScrollablePage",
    "PasswordInput",
    "PythonHighlighter",
    "ScrollablePage",
    "SearchInput",
    "StatCard",
    "TextArea",
    "ToggleButton",
    "Widget",
]
