"""Styling utilities for Qt widgets.

This module provides helper functions for working with Qt's dynamic property
system and stylesheets, making it easier to apply theme-aware styles to widgets.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


def set_widget_property(
    widget: QWidget, property_name: str, value: Any, refresh: bool = True
) -> None:
    """Set a dynamic property on a widget and optionally refresh its style.

    Args:
        widget: The widget to set the property on
        property_name: The name of the property
        value: The value to set
        refresh: Whether to refresh the widget's style after setting the property

    Example:
        ```python
        # Set a variant property for styling
        set_widget_property(button, "variant", "primary")

        # Set heading level
        set_widget_property(label, "heading", "h1")

        # Set custom property without refresh
        set_widget_property(widget, "custom", "value", refresh=False)
        ```
    """
    widget.setProperty(property_name, value)
    if refresh:
        refresh_widget_style(widget)


def refresh_widget_style(widget: QWidget) -> None:
    """Force a widget to refresh its stylesheet.

    This is necessary when dynamic properties change to ensure the
    stylesheet is re-evaluated with the new property values.

    Args:
        widget: The widget to refresh

    Example:
        ```python
        widget.setProperty("state", "active")
        refresh_widget_style(widget)
        ```
    """
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def set_widget_properties(
    widget: QWidget, properties: dict[str, Any], refresh: bool = True
) -> None:
    """Set multiple dynamic properties on a widget at once.

    Args:
        widget: The widget to set properties on
        properties: Dictionary of property names and values
        refresh: Whether to refresh the widget's style after setting properties

    Example:
        ```python
        set_widget_properties(
            button, {"variant": "primary", "size": "large", "state": "active"}
        )
        ```
    """
    for name, value in properties.items():
        widget.setProperty(name, value)
    if refresh:
        refresh_widget_style(widget)


def set_widget_variant(widget: QWidget, variant: str) -> None:
    """Set the variant property on a widget for styling.

    Common variants: primary, secondary, success, danger, warning, info

    Args:
        widget: The widget to set the variant on
        variant: The variant name

    Example:
        ```python
        set_widget_variant(button, "primary")
        set_widget_variant(label, "danger")
        ```
    """
    set_widget_property(widget, "variant", variant)


def set_heading_level(widget: QWidget, level: int) -> None:
    """Set the heading level property on a widget for styling.

    Args:
        widget: The widget to set the heading level on
        level: The heading level (1-6)

    Example:
        ```python
        set_heading_level(title_label, 1)  # h1
        set_heading_level(subtitle_label, 2)  # h2
        ```
    """
    if not 1 <= level <= 6:
        raise ValueError(f"Heading level must be between 1 and 6, got {level}")
    set_widget_property(widget, "heading", f"h{level}")


@contextmanager
def batch_style_updates(widget: QWidget):
    """Context manager for efficient batch style updates.

    Disables updates during property changes and refreshes the style once at the end.

    Args:
        widget: The widget to batch update

    Example:
        ```python
        with batch_style_updates(widget):
            widget.setProperty("variant", "primary")
            widget.setProperty("size", "large")
            widget.setProperty("state", "active")
        # Style is refreshed here automatically
        ```
    """
    widget.setUpdatesEnabled(False)
    try:
        yield widget
    finally:
        refresh_widget_style(widget)
        widget.setUpdatesEnabled(True)
