"""Color swatch widgets for displaying and selecting colors.

This module provides widgets for displaying color palettes, swatches,
and color information.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


if TYPE_CHECKING:
    from PySide6.QtWidgets import QLayout

from qtframework.utils.styling import set_heading_level, set_widget_property


class ColorSwatch(QFrame):
    """Widget displaying a color swatch with metadata.

    Shows a color preview with optional name, hex value, and description.
    Can be made interactive to allow color copying or selection.

    Example:
        ```python
        swatch = ColorSwatch("#FF5733", "Primary Red", "Main brand color")
        swatch.color_clicked.connect(lambda hex: print(f"Clicked: {hex}"))
        ```
    """

    color_clicked = Signal(str)  # Emits hex color when clicked

    def __init__(
        self,
        color: str,
        name: str = "",
        description: str = "",
        size: int = 50,
        interactive: bool = True,
        parent: QWidget | None = None,
    ):
        """Initialize the color swatch.

        Args:
            color: Hex color code (e.g., "#FF5733")
            name: Optional color name
            description: Optional color description
            size: Size of the color swatch in pixels
            interactive: Whether the swatch is clickable
            parent: Parent widget
        """
        super().__init__(parent)
        self.color = color
        self._interactive = interactive
        self._size = size
        self._name = name
        self._description = description
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Color swatch
        self.swatch_frame = QFrame()
        self.swatch_frame.setStyleSheet(
            f"background-color: {self.color}; "
            f"border: 1px solid rgba(0,0,0,0.1); "
            f"border-radius: 4px;"
        )
        self.swatch_frame.setFixedSize(self._size, self._size)
        layout.addWidget(self.swatch_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # Name
        if self._name:
            name_label = QLabel(self._name)
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setWordWrap(True)
            set_heading_level(name_label, 4)
            layout.addWidget(name_label)

        # Color value
        self.color_label = QLabel(self.color)
        self.color_label.setStyleSheet("font-family: monospace; font-size: 10px;")
        self.color_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.color_label)

        # Description
        if self._description:
            desc_label = QLabel(self._description)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setWordWrap(True)
            set_widget_property(desc_label, "secondary", "true")
            layout.addWidget(desc_label)

        if self._interactive:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setToolTip(f"Click to copy {self.color}")

    def mousePressEvent(self, event) -> None:
        """Handle mouse press for interactive swatches."""
        if self._interactive and event.button() == Qt.MouseButton.LeftButton:
            # Copy to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(self.color)
            self.color_clicked.emit(self.color)

            # Visual feedback
            self.setToolTip(f"Copied {self.color}!")

        super().mousePressEvent(event)

    def set_color(self, color: str) -> None:
        """Update the displayed color.

        Args:
            color: New hex color code
        """
        self.color = color
        self.swatch_frame.setStyleSheet(
            f"background-color: {color}; border: 1px solid rgba(0,0,0,0.1); border-radius: 4px;"
        )
        self.color_label.setText(color)

    def get_color(self) -> str:
        """Get the current color."""
        return self.color


class LargeColorSwatch(QWidget):
    """Large color swatch with detailed information displayed horizontally.

    Example:
        ```python
        swatch = LargeColorSwatch("#FF5733", "Primary Red", "Main brand color for CTAs")
        ```
    """

    def __init__(
        self,
        color: str,
        name: str = "",
        description: str = "",
        parent: QWidget | None = None,
    ):
        """Initialize the large color swatch.

        Args:
            color: Hex color code
            name: Color name
            description: Color description
            parent: Parent widget
        """
        super().__init__(parent)
        self.color = color
        self._init_ui(name, description)

    def _init_ui(self, name: str, description: str) -> None:
        """Initialize the UI."""
        self.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 10, 0)
        layout.setSpacing(10)

        # Large color swatch
        swatch = QFrame()
        swatch.setStyleSheet(
            f"background-color: {self.color}; "
            f"border: 1px solid rgba(0,0,0,0.1); "
            f"border-radius: 4px;"
        )
        swatch.setFixedSize(80, 80)
        layout.addWidget(swatch)

        # Color info
        info_widget = QWidget()
        info_widget.setStyleSheet("background: transparent;")
        info_widget.setFixedWidth(150)
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)

        if name:
            name_label = QLabel(name)
            set_heading_level(name_label, 3)
            info_layout.addWidget(name_label)

        color_label = QLabel(self.color)
        color_label.setStyleSheet("font-family: monospace;")
        info_layout.addWidget(color_label)

        if description:
            desc_label = QLabel(description)
            set_widget_property(desc_label, "secondary", "true")
            desc_label.setWordWrap(True)
            info_layout.addWidget(desc_label)

        info_layout.addStretch()
        layout.addWidget(info_widget)


class ColorPaletteWidget(QWidget):
    """Widget displaying multiple color swatches in a palette.

    Example:
        ```python
        palette = ColorPaletteWidget()
        palette.add_color_group(
            "Primary Colors",
            [
                ("#FF5733", "Red", "Main brand color"),
                ("#3357FF", "Blue", "Secondary color"),
            ],
        )
        ```
    """

    def __init__(self, parent: QWidget | None = None):
        """Initialize the color palette widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the UI."""
        self.main_layout = QVBoxLayout(self)

    def add_color(
        self,
        color: str,
        name: str = "",
        description: str = "",
        large: bool = False,
    ) -> None:
        """Add a single color to the palette.

        Args:
            color: Hex color code
            name: Color name
            description: Color description
            large: Whether to use large swatch format
        """
        swatch: ColorSwatch | LargeColorSwatch
        if large:
            swatch = LargeColorSwatch(color, name, description)
        else:
            swatch = ColorSwatch(color, name, description)

        self.main_layout.addWidget(swatch)

    def add_color_group(
        self,
        title: str,
        colors: list[tuple[str, str, str]],
        use_flow_layout: bool = True,
    ) -> None:
        """Add a group of related colors.

        Args:
            title: Group title
            colors: List of (color, name, description) tuples
            use_flow_layout: Whether to use flow layout (requires qtframework.layouts)
        """
        group = QGroupBox(title)

        layout: QLayout
        if use_flow_layout:
            try:
                from qtframework.layouts import FlowLayout

                layout = FlowLayout()
            except ImportError:
                # Fallback to horizontal layout
                layout = QHBoxLayout()
        else:
            layout = QVBoxLayout()

        for color, name, _description in colors:
            item_widget = QWidget()
            item_widget.setStyleSheet("background: transparent;")
            item_widget.setFixedSize(100, 100)
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(4)

            # Small swatch
            swatch = QFrame()
            swatch.setStyleSheet(
                f"background-color: {color}; border: 1px solid rgba(0,0,0,0.1); border-radius: 3px;"
            )
            swatch.setFixedSize(50, 50)
            item_layout.addWidget(swatch, alignment=Qt.AlignmentFlag.AlignCenter)

            # Name
            if name:
                name_label = QLabel(name)
                name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                name_label.setWordWrap(True)
                item_layout.addWidget(name_label)

            # Color value
            color_label = QLabel(color)
            color_label.setStyleSheet("font-family: monospace; font-size: 10px;")
            color_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item_layout.addWidget(color_label)

            layout.addWidget(item_widget)

        group.setLayout(layout)
        self.main_layout.addWidget(group)

    def clear_colors(self) -> None:
        """Clear all colors from the palette."""
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def load_from_theme(self, theme) -> None:
        """Load colors from a theme object.

        Args:
            theme: Theme object with color tokens
        """
        self.clear_colors()

        if not hasattr(theme, "tokens"):
            return

        tokens = theme.tokens

        # Add main colors if available
        if hasattr(tokens, "primary"):
            self.add_color(tokens.primary, "Primary", "Main brand color", large=True)

        # Add semantic colors if available
        if hasattr(tokens, "semantic"):
            semantic = tokens.semantic
            bg_colors = []
            fg_colors = []

            if hasattr(semantic, "bg_primary"):
                bg_colors.append((semantic.bg_primary, "Primary", ""))
            if hasattr(semantic, "bg_secondary"):
                bg_colors.append((semantic.bg_secondary, "Secondary", ""))
            if hasattr(semantic, "fg_primary"):
                fg_colors.append((semantic.fg_primary, "Primary", ""))
            if hasattr(semantic, "fg_secondary"):
                fg_colors.append((semantic.fg_secondary, "Secondary", ""))

            if bg_colors:
                self.add_color_group("Background Colors", bg_colors)
            if fg_colors:
                self.add_color_group("Text Colors", fg_colors)
