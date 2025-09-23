"""Base theme classes and interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field


class ColorPalette(BaseModel):
    """Color palette for theming."""

    primary: str = Field(default="#2196F3")
    primary_dark: str = Field(default="#1976D2")
    primary_light: str = Field(default="#42A5F5")
    secondary: str = Field(default="#FFC107")
    secondary_dark: str = Field(default="#FFA000")
    secondary_light: str = Field(default="#FFD54F")
    background: str = Field(default="#FFFFFF")
    surface: str = Field(default="#F5F5F5")
    error: str = Field(default="#F44336")
    warning: str = Field(default="#FF9800")
    info: str = Field(default="#2196F3")
    success: str = Field(default="#4CAF50")
    text_primary: str = Field(default="#212121")
    text_secondary: str = Field(default="#757575")
    text_disabled: str = Field(default="#BDBDBD")
    border: str = Field(default="#E0E0E0")
    hover: str = Field(default="#F5F5F5")
    selected: str = Field(default="#E3F2FD")


class Typography(BaseModel):
    """Typography settings."""

    font_family: str = Field(default="Segoe UI, Arial, sans-serif")
    font_size_base: int = Field(default=14)
    font_size_small: int = Field(default=12)
    font_size_large: int = Field(default=16)
    font_size_h1: int = Field(default=32)
    font_size_h2: int = Field(default=28)
    font_size_h3: int = Field(default=24)
    font_size_h4: int = Field(default=20)
    font_size_h5: int = Field(default=18)
    font_size_h6: int = Field(default=16)
    font_weight_light: int = Field(default=300)
    font_weight_normal: int = Field(default=400)
    font_weight_medium: int = Field(default=500)
    font_weight_bold: int = Field(default=700)
    line_height: float = Field(default=1.5)


class Spacing(BaseModel):
    """Spacing settings."""

    unit: int = Field(default=8)
    xs: int = Field(default=4)
    sm: int = Field(default=8)
    md: int = Field(default=16)
    lg: int = Field(default=24)
    xl: int = Field(default=32)
    xxl: int = Field(default=48)


class BorderRadius(BaseModel):
    """Border radius settings."""

    none: int = Field(default=0)
    sm: int = Field(default=2)
    md: int = Field(default=4)
    lg: int = Field(default=8)
    xl: int = Field(default=16)
    full: int = Field(default=9999)


class Shadows(BaseModel):
    """Shadow settings."""

    none: str = Field(default="none")
    sm: str = Field(default="0 1px 3px rgba(0,0,0,0.12)")
    md: str = Field(default="0 3px 6px rgba(0,0,0,0.16)")
    lg: str = Field(default="0 10px 20px rgba(0,0,0,0.19)")
    xl: str = Field(default="0 14px 28px rgba(0,0,0,0.25)")


@dataclass
class Theme(ABC):
    """Abstract base class for themes."""

    name: str
    display_name: str
    description: str = ""
    author: str = ""
    version: str = "1.0.0"
    colors: ColorPalette = field(default_factory=ColorPalette)
    typography: Typography = field(default_factory=Typography)
    spacing: Spacing = field(default_factory=Spacing)
    borders: BorderRadius = field(default_factory=BorderRadius)
    shadows: Shadows = field(default_factory=Shadows)
    custom_styles: dict[str, str] = field(default_factory=dict)

    @abstractmethod
    def generate_stylesheet(self) -> str:
        """Generate Qt stylesheet from theme.

        Returns:
            Qt stylesheet string
        """
        ...

    def get_color(self, color_name: str) -> str:
        """Get color value by name.

        Args:
            color_name: Name of the color

        Returns:
            Color value
        """
        return getattr(self.colors, color_name, "#000000")

    def get_font_size(self, size_name: str) -> int:
        """Get font size by name.

        Args:
            size_name: Name of the size

        Returns:
            Font size in pixels
        """
        return getattr(self.typography, f"font_size_{size_name}", 14)

    def get_spacing(self, spacing_name: str) -> int:
        """Get spacing value by name.

        Args:
            spacing_name: Name of the spacing

        Returns:
            Spacing value in pixels
        """
        return getattr(self.spacing, spacing_name, 8)

    def to_dict(self) -> dict[str, Any]:
        """Convert theme to dictionary.

        Returns:
            Theme as dictionary
        """
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "author": self.author,
            "version": self.version,
            "colors": self.colors.model_dump(),
            "typography": self.typography.model_dump(),
            "spacing": self.spacing.model_dump(),
            "borders": self.borders.model_dump(),
            "shadows": self.shadows.model_dump(),
            "custom_styles": self.custom_styles,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Theme:
        """Create theme from dictionary.

        Args:
            data: Theme dictionary

        Returns:
            Theme instance
        """
        return cls(
            name=data["name"],
            display_name=data["display_name"],
            description=data.get("description", ""),
            author=data.get("author", ""),
            version=data.get("version", "1.0.0"),
            colors=ColorPalette(**data.get("colors", {})),
            typography=Typography(**data.get("typography", {})),
            spacing=Spacing(**data.get("spacing", {})),
            borders=BorderRadius(**data.get("borders", {})),
            shadows=Shadows(**data.get("shadows", {})),
            custom_styles=data.get("custom_styles", {}),
        )


class StandardTheme(Theme):
    """Standard theme implementation."""

    def generate_stylesheet(self) -> str:
        """Generate Qt stylesheet from theme."""
        return f"""
        * {{
            font-family: "{self.typography.font_family}";
            font-size: {self.typography.font_size_base}px;
            color: {self.colors.text_primary};
        }}

        QMainWindow {{
            background-color: {self.colors.background};
        }}

        QWidget {{
            background-color: {self.colors.background};
            selection-background-color: {self.colors.selected};
            selection-color: {self.colors.text_primary};
        }}

        QPushButton {{
            background-color: {self.colors.surface};
            color: {self.colors.text_primary};
            border: 1px solid {self.colors.border};
            border-radius: {self.borders.md}px;
            padding: {self.spacing.sm}px {self.spacing.md}px;
            font-weight: {self.typography.font_weight_medium};
        }}

        QPushButton:hover {{
            background-color: {self.colors.hover};
            border-color: {self.colors.primary};
        }}

        QPushButton:pressed {{
            background-color: {self.colors.selected};
        }}

        QPushButton:disabled {{
            background-color: {self.colors.text_disabled};
            color: {self.colors.surface};
        }}

        /* Button Variants */
        QPushButton[variant="primary"] {{
            background-color: {self.colors.primary};
            color: white;
            border: none;
        }}
        QPushButton[variant="primary"]:hover {{
            background-color: {self.colors.primary_light};
            border: none;
        }}
        QPushButton[variant="primary"]:pressed {{
            background-color: {self.colors.primary_dark};
            border: none;
        }}

        QPushButton[variant="secondary"] {{
            background-color: {self.colors.secondary};
            color: {self.colors.background};
            border: none;
        }}
        QPushButton[variant="secondary"]:hover {{
            background-color: {self.colors.secondary_light};
            border: none;
        }}
        QPushButton[variant="secondary"]:pressed {{
            background-color: {self.colors.secondary_dark};
            border: none;
        }}

        QPushButton[variant="success"] {{
            background-color: {self.colors.success};
            color: white;
            border: none;
        }}
        QPushButton[variant="success"]:hover {{
            background-color: {self.colors.success};
        }}
        QPushButton[variant="success"]:pressed {{
            background-color: {self.colors.success};
        }}

        QPushButton[variant="warning"] {{
            background-color: {self.colors.warning};
            color: white;
            border: none;
        }}
        QPushButton[variant="warning"]:hover {{
            background-color: {self.colors.warning};
        }}
        QPushButton[variant="warning"]:pressed {{
            background-color: {self.colors.warning};
        }}

        QPushButton[variant="danger"] {{
            background-color: {self.colors.error};
            color: white;
            border: none;
        }}
        QPushButton[variant="danger"]:hover {{
            background-color: {self.colors.error};
        }}
        QPushButton[variant="danger"]:pressed {{
            background-color: {self.colors.error};
        }}

        QPushButton[variant="info"] {{
            background-color: {self.colors.info};
            color: white;
            border: none;
        }}
        QPushButton[variant="info"]:hover {{
            background-color: {self.colors.info};
        }}
        QPushButton[variant="info"]:pressed {{
            background-color: {self.colors.info};
        }}

        QPushButton[variant="outline"] {{
            background-color: transparent;
            color: {self.colors.primary};
            border: 2px solid {self.colors.primary};
        }}
        QPushButton[variant="outline"]:hover {{
            background-color: {self.colors.primary};
            color: white;
        }}
        QPushButton[variant="outline"]:pressed {{
            background-color: {self.colors.primary_dark};
            color: white;
        }}

        QPushButton[variant="text"] {{
            background-color: transparent;
            color: {self.colors.primary};
            border: none;
        }}
        QPushButton[variant="text"]:hover {{
            background-color: {self.colors.hover};
        }}
        QPushButton[variant="text"]:pressed {{
            background-color: {self.colors.selected};
        }}

        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {self.colors.surface};
            border: 1px solid {self.colors.border};
            border-radius: {self.borders.md}px;
            padding: {self.spacing.sm}px;
            color: {self.colors.text_primary};
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {self.colors.primary};
            outline: none;
        }}

        QComboBox {{
            background-color: {self.colors.surface};
            border: 1px solid {self.colors.border};
            border-radius: {self.borders.md}px;
            padding: {self.spacing.sm}px;
            min-width: 120px;
        }}

        QComboBox:hover {{
            border-color: {self.colors.primary};
        }}

        QComboBox::drop-down {{
            border: none;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid {self.colors.text_secondary};
            margin-right: {self.spacing.sm}px;
        }}

        QLabel {{
            color: {self.colors.text_primary};
            background-color: transparent;
        }}

        QGroupBox {{
            border: 1px solid {self.colors.border};
            border-radius: {self.borders.md}px;
            margin-top: 12px;
            padding-top: {self.spacing.md}px;
            font-weight: {self.typography.font_weight_medium};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {self.spacing.sm}px;
            padding: 0 {self.spacing.xs}px;
            color: {self.colors.text_primary};
        }}

        QTabWidget::pane {{
            border: 1px solid {self.colors.border};
            background-color: {self.colors.background};
            border-radius: {self.borders.md}px;
        }}

        QTabBar::tab {{
            background-color: {self.colors.surface};
            color: {self.colors.text_secondary};
            padding: {self.spacing.sm}px {self.spacing.md}px;
            margin-right: 2px;
            border-top-left-radius: {self.borders.md}px;
            border-top-right-radius: {self.borders.md}px;
        }}

        QTabBar::tab:selected {{
            background-color: {self.colors.background};
            color: {self.colors.primary};
            border-bottom: 2px solid {self.colors.primary};
        }}

        QTabBar::tab:hover {{
            background-color: {self.colors.hover};
        }}

        QScrollBar:vertical {{
            background-color: {self.colors.surface};
            width: 12px;
            border-radius: {self.borders.md}px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {self.colors.text_disabled};
            border-radius: {self.borders.md}px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {self.colors.text_secondary};
        }}

        QMenuBar {{
            background-color: {self.colors.surface};
            color: {self.colors.text_primary};
            border-bottom: 1px solid {self.colors.border};
        }}

        QMenuBar::item:selected {{
            background-color: {self.colors.hover};
        }}

        QMenu {{
            background-color: {self.colors.background};
            border: 1px solid {self.colors.border};
            border-radius: {self.borders.md}px;
            padding: {self.spacing.xs}px;
        }}

        QMenu::item {{
            padding: {self.spacing.sm}px {self.spacing.lg}px;
            border-radius: {self.borders.sm}px;
        }}

        QMenu::item:selected {{
            background-color: {self.colors.hover};
            color: {self.colors.primary};
        }}

        QStatusBar {{
            background-color: {self.colors.surface};
            color: {self.colors.text_secondary};
            border-top: 1px solid {self.colors.border};
        }}

        QToolBar {{
            background-color: {self.colors.surface};
            border: none;
            spacing: {self.spacing.sm}px;
            padding: {self.spacing.sm}px;
        }}

        /* Icon Button / Close Button styles */
        QPushButton[class="close-button"] {{
            color: {self.colors.text_secondary};
            background-color: transparent;
            border: none;
            font-size: 16px;
            font-weight: bold;
            border-radius: 10px;
            padding: 5px;
        }}

        QPushButton[class="close-button"]:hover {{
            background-color: {self.colors.hover};
            color: {self.colors.text_primary};
        }}

        QPushButton[class="close-button"]:pressed {{
            background-color: {self.colors.selected};
        }}

        /* Light style close button - optimized for dark backgrounds */
        QPushButton[class="close-button"][style="light"] {{
            color: {self.colors.background};
        }}

        QPushButton[class="close-button"][style="light"]:hover {{
            background-color: {self.colors.hover};
            color: {self.colors.text_primary};
        }}

        /* Dark style close button - optimized for light backgrounds */
        QPushButton[class="close-button"][style="dark"] {{
            color: {self.colors.text_disabled};
        }}

        QPushButton[class="close-button"][style="dark"]:hover {{
            background-color: {self.colors.hover};
            color: {self.colors.text_primary};
        }}

        QToolButton {{
            background-color: transparent;
            border: none;
            border-radius: {self.borders.md}px;
            padding: {self.spacing.sm}px;
        }}

        QToolButton:hover {{
            background-color: {self.colors.hover};
        }}

        QToolButton:pressed {{
            background-color: {self.colors.selected};
        }}

        QProgressBar {{
            background-color: {self.colors.surface};
            border: 1px solid {self.colors.border};
            border-radius: {self.borders.md}px;
            text-align: center;
            height: 20px;
        }}

        QProgressBar::chunk {{
            background-color: {self.colors.primary};
            border-radius: {self.borders.md}px;
        }}

        QSlider::groove:horizontal {{
            background-color: {self.colors.surface};
            height: 4px;
            border-radius: 2px;
        }}

        QSlider::handle:horizontal {{
            background-color: {self.colors.primary};
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -6px 0;
        }}

        QSlider::handle:horizontal:hover {{
            background-color: {self.colors.primary_light};
        }}

        QCheckBox, QRadioButton {{
            spacing: {self.spacing.sm}px;
            color: {self.colors.text_primary};
        }}

        QCheckBox::indicator, QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {self.colors.border};
            background-color: {self.colors.surface};
        }}

        QCheckBox::indicator {{
            border-radius: {self.borders.sm}px;
        }}

        QRadioButton::indicator {{
            border-radius: 9px;
        }}

        QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
            background-color: {self.colors.primary};
            border-color: {self.colors.primary};
        }}

        QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
            border-color: {self.colors.primary_light};
        }}

        QListWidget, QTreeWidget, QTableWidget {{
            background-color: {self.colors.background};
            border: 1px solid {self.colors.border};
            border-radius: {self.borders.md}px;
            outline: none;
        }}

        QListWidget::item, QTreeWidget::item, QTableWidget::item {{
            padding: {self.spacing.sm}px;
            border-bottom: 1px solid {self.colors.surface};
        }}

        QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {{
            background-color: {self.colors.selected};
            color: {self.colors.text_primary};
        }}

        QListWidget::item:hover, QTreeWidget::item:hover, QTableWidget::item:hover {{
            background-color: {self.colors.hover};
        }}

        QHeaderView::section {{
            background-color: {self.colors.surface};
            color: {self.colors.text_primary};
            padding: {self.spacing.sm}px;
            border: none;
            border-right: 1px solid {self.colors.border};
            border-bottom: 2px solid {self.colors.border};
            font-weight: {self.typography.font_weight_medium};
        }}

        QToolTip {{
            background-color: {self.colors.text_primary};
            color: {self.colors.background};
            border: none;
            padding: {self.spacing.sm}px;
            border-radius: {self.borders.md}px;
        }}

        /* Sidebar Toggle Button */
        QPushButton[class="sidebar-toggle"] {{
            background-color: transparent;
            border: 1px solid {self.colors.border};
            border-radius: {self.borders.md}px;
            color: {self.colors.text_primary};
            font-size: 18px;
            font-weight: bold;
        }}
        QPushButton[class="sidebar-toggle"]:hover {{
            background-color: {self.colors.hover};
            border-color: {self.colors.primary};
        }}
        QPushButton[class="sidebar-toggle"]:pressed {{
            background-color: {self.colors.selected};
        }}

        /* Close Button Default Style */
        QPushButton[class="close-button"] {{
            background-color: transparent;
            border: none;
            color: {self.colors.text_secondary};
            font-size: 18px;
            font-weight: bold;
            padding: 0px;
            border-radius: {self.borders.sm}px;
        }}
        QPushButton[class="close-button"]:hover {{
            color: {self.colors.text_primary};
            background-color: {self.colors.hover};
        }}

        /* Search Clear Button (uses close-button) */
        SearchInput QPushButton[class="close-button"] {{
            margin-right: 4px;
        }}
        """
