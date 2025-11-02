"""Stylesheet generator for converting design tokens to Qt stylesheets."""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from qtframework.themes.tokens import DesignTokens
    from qtframework.utils.resources import ResourceManager


class StylesheetGenerator:
    """Generate Qt stylesheets from design tokens."""

    def __init__(self, resource_manager: ResourceManager | None = None) -> None:
        """Initialize stylesheet generator.

        Args:
            resource_manager: Optional resource manager for resolving icon paths
        """
        self._resource_manager = resource_manager

    def generate(self, tokens: DesignTokens, custom_styles: dict[str, str]) -> str:
        """Generate complete stylesheet from tokens.

        Args:
            tokens: Design tokens
            custom_styles: Additional custom CSS rules

        Returns:
            Complete Qt stylesheet string
        """
        styles = []

        # Base styles
        styles.append(self._generate_base_styles(tokens))

        # Widget styles
        styles.append(self._generate_button_styles(tokens))
        styles.append(self._generate_input_styles(tokens))
        styles.append(self._generate_list_styles(tokens))
        styles.append(self._generate_table_styles(tokens))
        styles.append(self._generate_menu_styles(tokens))
        styles.append(self._generate_tab_styles(tokens))
        styles.append(self._generate_scrollbar_styles(tokens))
        styles.append(self._generate_container_styles(tokens))
        styles.append(self._generate_dialog_styles(tokens))
        styles.append(self._generate_misc_styles(tokens))

        # Add custom styles
        for selector, rules in custom_styles.items():
            styles.append(f"{selector} {{\n{rules}\n}}")

        return "\n\n".join(filter(None, styles))

    def _generate_base_styles(self, tokens: DesignTokens) -> str:
        """Generate base/global styles."""
        return f"""
/* Base Styles */
* {{
    font-family: {tokens.typography.font_family_default};
    font-size: {tokens.typography.font_size_md}px;
    color: {tokens.semantic.fg_primary};
}}

QMainWindow, QDialog {{
    background-color: {tokens.semantic.bg_primary};
}}

QWidget {{
    background-color: {tokens.semantic.bg_primary};
    color: {tokens.semantic.fg_primary};
    selection-background-color: {tokens.semantic.state_selected};
    selection-color: {tokens.semantic.fg_on_accent};
}}

QLabel {{
    color: {tokens.semantic.fg_primary};
    background-color: transparent;
    padding: {tokens.spacing.space_1}px;
}}

QLabel[heading="h1"] {{
    font-size: {tokens.typography.font_size_5xl}px;
    font-weight: {tokens.typography.font_weight_bold};
    margin: {tokens.spacing.space_4}px 0;
}}

QLabel[heading="h2"] {{
    font-size: {tokens.typography.font_size_4xl}px;
    font-weight: {tokens.typography.font_weight_semibold};
    margin: {tokens.spacing.space_3}px 0;
}}

QLabel[heading="h3"] {{
    font-size: {tokens.typography.font_size_3xl}px;
    font-weight: {tokens.typography.font_weight_semibold};
    margin: {tokens.spacing.space_2}px 0;
}}

QLabel[secondary="true"] {{
    color: {tokens.semantic.fg_secondary};
}}

QLabel[disabled="true"] {{
    color: {tokens.semantic.fg_tertiary};
}}

/* Code blocks */
QLabel[codeblock="true"], QTextEdit[codeblock="true"] {{
    background-color: {tokens.semantic.bg_tertiary};
    color: {tokens.semantic.fg_primary};
    padding: 8px;
    border: 1px solid {tokens.semantic.border_subtle};
    border-radius: {tokens.borders.radius_sm}px;
}}

QTextEdit[codeblock="true"] {{
    font-family: "Consolas", "Monaco", "Courier New", monospace;
}}"""

    def _generate_button_styles(self, tokens: DesignTokens) -> str:
        """Generate button styles."""
        styles = []

        styles.append("""
/* Button Styles */
QPushButton {""")

        # Check if button textures are defined
        if tokens.components.button_image:
            # Use texture-based buttons with 9-slice
            button_url = self._resolve_image_url(tokens.components.button_image)
            if tokens.components.button_border_slice:
                slice_values = tokens.components.button_border_slice.split()
                border_width = " ".join([f"{v}px" for v in slice_values])
                styles.append(f"    border-width: {border_width};")
                styles.append(
                    f"    border-image: url({button_url}) {tokens.components.button_border_slice} fill stretch;"
                )
            else:
                styles.append(f"    background-image: url({button_url});")
                styles.append("    background-position: center;")
                styles.append("    background-repeat: no-repeat;")
            styles.append(
                f"    color: {tokens.components.button_secondary_fg or tokens.semantic.fg_primary};"
            )
        else:
            # Use solid color buttons (default)
            styles.append(
                f"    background-color: {tokens.components.button_secondary_bg or tokens.semantic.bg_secondary};"
            )
            styles.append(
                f"    color: {tokens.components.button_secondary_fg or tokens.semantic.fg_primary};"
            )
            styles.append(
                f"    border: 1px solid {tokens.components.button_secondary_border or tokens.semantic.border_default};"
            )

        styles.append(f"    border-radius: {tokens.borders.radius_md}px;")
        styles.append(f"    padding: {tokens.spacing.space_3}px {tokens.spacing.space_8}px;")
        styles.append(f"    font-weight: {tokens.typography.font_weight_medium};")
        styles.append(f"    min-height: {tokens.spacing.space_16}px;")
        styles.append("}")

        # Hover state
        styles.append("\nQPushButton:hover {")
        if tokens.components.button_hover_image:
            hover_url = self._resolve_image_url(tokens.components.button_hover_image)
            if tokens.components.button_border_slice:
                # Simple replacement: use composite texture with borders + highlight
                styles.append(
                    f"    border-image: url({hover_url}) {tokens.components.button_border_slice} fill stretch;"
                )
            else:
                styles.append(f"    background-image: url({hover_url});")
        elif not tokens.components.button_image:
            # Only use color hover if not using textures
            styles.append(f"    background-color: {tokens.semantic.state_hover};")
            styles.append(f"    border-color: {tokens.semantic.border_strong};")
        styles.append("}")

        # Pressed state
        styles.append("\nQPushButton:pressed {")
        if tokens.components.button_pressed_image:
            pressed_url = self._resolve_image_url(tokens.components.button_pressed_image)
            if tokens.components.button_border_slice:
                styles.append(
                    f"    border-image: url({pressed_url}) {tokens.components.button_border_slice} fill stretch;"
                )
            else:
                styles.append(f"    background-image: url({pressed_url});")
        elif not tokens.components.button_image:
            # Only use color pressed if not using textures
            styles.append(f"    background-color: {tokens.semantic.state_selected};")
        styles.append("}")

        # Disabled state
        styles.append("\nQPushButton:disabled {")
        if tokens.components.button_disabled_image:
            disabled_url = self._resolve_image_url(tokens.components.button_disabled_image)
            if tokens.components.button_border_slice:
                styles.append(
                    f"    border-image: url({disabled_url}) {tokens.components.button_border_slice} fill stretch;"
                )
            else:
                styles.append(f"    background-image: url({disabled_url});")
        elif not tokens.components.button_image:
            # Only use color disabled if not using textures
            styles.append(f"    background-color: {tokens.semantic.state_disabled};")
            styles.append(f"    border-color: {tokens.semantic.border_subtle};")
        styles.append(f"    color: {tokens.semantic.fg_tertiary};")
        styles.append("}")

        # Focus state
        styles.append(f"""
QPushButton:focus {{
    border-color: {tokens.semantic.border_focus};
    outline: none;
}}""")

        # Add variant styles (these override default button styles)
        styles.append(f"""
/* Primary Button */
QPushButton[variant="primary"] {{
    background-color: {tokens.components.button_primary_bg or tokens.semantic.action_primary};
    color: {tokens.components.button_primary_fg or tokens.semantic.fg_on_accent};
    border: none;
}}

QPushButton[variant="primary"]:hover {{
    background-color: {tokens.components.button_primary_border or tokens.semantic.action_primary_hover};
}}

QPushButton[variant="primary"]:pressed {{
    background-color: {tokens.semantic.action_secondary_active or tokens.semantic.action_primary_active};
}}

/* Success Button */
QPushButton[variant="success"] {{
    background-color: {tokens.semantic.feedback_success};
    color: {tokens.semantic.fg_on_accent};
    border: none;
}}

/* Warning Button */
QPushButton[variant="warning"] {{
    background-color: {tokens.semantic.feedback_warning};
    color: {tokens.semantic.fg_on_accent};
    border: none;
}}

/* Danger Button */
QPushButton[variant="danger"], QPushButton[variant="error"] {{
    background-color: {tokens.semantic.feedback_error};
    color: {tokens.semantic.fg_on_accent};
    border: none;
}}

/* Info Button */
QPushButton[variant="info"] {{
    background-color: {tokens.semantic.feedback_info};
    color: {tokens.semantic.fg_on_accent};
    border: none;
}}

/* Ghost Button */
QPushButton[variant="ghost"], QPushButton[variant="text"] {{
    background-color: transparent;
    color: {tokens.semantic.action_primary};
    border: none;
    padding: {tokens.spacing.space_2}px {tokens.spacing.space_4}px;
}}

QPushButton[variant="ghost"]:hover, QPushButton[variant="text"]:hover {{
    background-color: {tokens.semantic.state_hover};
}}

/* Outline Button */
QPushButton[variant="outline"] {{
    background-color: transparent;
    color: {tokens.semantic.action_primary};
    border: 2px solid {tokens.semantic.action_primary};
}}

QPushButton[variant="outline"]:hover {{
    background-color: {tokens.semantic.action_primary};
    color: {tokens.semantic.fg_on_accent};
}}

/* Button Sizes */
QPushButton[size="compact"] {{
    padding: 2px 8px;
    min-height: 0px;
}}

/* Icon Button */
QPushButton[icon-button="true"] {{
    background-color: transparent;
    border: none;
    padding: {tokens.spacing.space_2}px;
    border-radius: {tokens.borders.radius_md}px;
}}

QPushButton[icon-button="true"]:hover {{
    background-color: {tokens.semantic.state_hover};
}}

/* Tool Button */
QToolButton {{
    background-color: transparent;
    border: none;
    border-radius: {tokens.borders.radius_md}px;
    padding: {tokens.spacing.space_2}px;
}}

QToolButton:hover {{
    background-color: {tokens.semantic.state_hover};
}}

QToolButton:pressed {{
    background-color: {tokens.semantic.state_selected};
}}""")

        return "\n".join(styles)

    def _generate_input_styles(self, tokens: DesignTokens) -> str:
        """Generate input field styles."""
        return f"""
/* Input Styles */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
    background-color: {tokens.components.input_bg or tokens.semantic.bg_secondary};
    color: {tokens.components.input_fg or tokens.semantic.fg_primary};
    border: 1px solid {tokens.components.input_border or tokens.semantic.border_default};
    border-radius: {tokens.borders.radius_md}px;
    padding: {tokens.spacing.space_3}px {tokens.spacing.space_4}px;
    font-size: {tokens.typography.font_size_md}px;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {tokens.semantic.border_focus};
    background-color: {tokens.semantic.bg_primary};
}}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled,
QSpinBox:disabled, QDoubleSpinBox:disabled {{
    background-color: {tokens.semantic.state_disabled};
    color: {tokens.semantic.fg_tertiary};
    border-color: {tokens.semantic.border_subtle};
}}

/* ComboBox */
QComboBox {{
    background-color: {tokens.components.combobox_bg or tokens.components.input_bg or tokens.semantic.bg_secondary};
    color: {tokens.components.combobox_fg or tokens.components.input_fg or tokens.semantic.fg_primary};
    border: 1px solid {tokens.components.combobox_border or tokens.components.input_border or tokens.semantic.border_default};
    border-radius: {tokens.borders.radius_md}px;
    padding: {tokens.spacing.space_3}px {tokens.spacing.space_4}px;
    min-width: 120px;
}}

QComboBox:hover {{
    border-color: {tokens.semantic.border_strong};
}}

QComboBox:focus {{
    border-color: {tokens.semantic.border_focus};
}}

QComboBox::drop-down {{
    border: none;
    width: {tokens.components.combobox_arrow_width}px;
    background: transparent;
}}

QComboBox::down-arrow {{
    {"image: url(" + self._resolve_image_url(tokens.components.combobox_arrow_image) + ");" if tokens.components.combobox_arrow_image else self._get_icon_style("dropdown-arrow.svg")}
    width: {tokens.components.combobox_arrow_width}px;
    height: {tokens.components.combobox_arrow_height}px;
}}

QComboBox::down-arrow:hover {{
    {"image: url(" + self._resolve_image_url(tokens.components.combobox_arrow_hover_image) + ");" if tokens.components.combobox_arrow_hover_image else ""}
}}

QComboBox::down-arrow:pressed {{
    {"image: url(" + self._resolve_image_url(tokens.components.combobox_arrow_pressed_image) + ");" if tokens.components.combobox_arrow_pressed_image else ""}
}}

QComboBox::down-arrow:disabled {{
    {"image: url(" + self._resolve_image_url(tokens.components.combobox_arrow_disabled_image) + ");" if tokens.components.combobox_arrow_disabled_image else ""}
}}

QComboBox QAbstractItemView {{
    background-color: {tokens.semantic.bg_elevated};
    border: 1px solid {tokens.semantic.border_default};
    selection-background-color: {tokens.semantic.state_selected};
    selection-color: {tokens.semantic.fg_on_accent};
    padding: {tokens.spacing.space_2}px;
}}

/* CheckBox & RadioButton */
QCheckBox, QRadioButton {{
    spacing: {tokens.spacing.space_3}px;
    color: {tokens.semantic.fg_primary};
    background-color: transparent;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {tokens.semantic.border_default};
    background-color: {tokens.semantic.bg_secondary};
}}

QCheckBox::indicator {{
    border-radius: {tokens.borders.radius_sm}px;
}}

QRadioButton::indicator {{
    border-radius: 9px;
}}

QCheckBox::indicator:checked {{
    background-color: {tokens.semantic.action_primary};
    border-color: {tokens.semantic.action_primary};
    /* Using default Qt checkmark */
}}

QRadioButton::indicator:checked {{
    background-color: {tokens.semantic.action_primary};
    border-color: {tokens.semantic.action_primary};
    /* Using default Qt radio button dot */
}}

QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
    border-color: {tokens.semantic.action_primary};
}}

QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {{
    background-color: {tokens.semantic.state_disabled};
    border-color: {tokens.semantic.border_subtle};
}}

/* Slider */
QSlider {{
    background-color: transparent;
}}

QSlider::groove:horizontal {{
    background-color: {tokens.semantic.bg_tertiary};
    height: 4px;
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background-color: {tokens.semantic.action_primary};
    width: 16px;
    height: 16px;
    border-radius: 8px;
    margin: -6px 0;
}}

QSlider::handle:horizontal:hover {{
    background-color: {tokens.semantic.action_primary_hover};
    width: 18px;
    height: 18px;
    margin: -7px 0;
}}

QSlider::sub-page:horizontal {{
    background-color: {tokens.semantic.action_primary};
    border-radius: 2px;
}}

/* Vertical Slider */
QSlider::groove:vertical {{
    background-color: {tokens.semantic.bg_tertiary};
    width: 4px;
    border-radius: 2px;
}}

QSlider::handle:vertical {{
    background-color: {tokens.semantic.action_primary};
    width: 16px;
    height: 16px;
    border-radius: 8px;
    margin: 0 -6px;
}}

QSlider::handle:vertical:hover {{
    background-color: {tokens.semantic.action_primary_hover};
    width: 18px;
    height: 18px;
    margin: 0 -7px;
}}

QSlider::add-page:vertical {{
    background-color: {tokens.semantic.action_primary};
    border-radius: 2px;
}}"""

    def _generate_list_styles(self, tokens: DesignTokens) -> str:
        """Generate list and tree styles."""
        return f"""
/* List, Tree & Item Views */
QListWidget, QListView, QTreeWidget, QTreeView {{
    background-color: {tokens.semantic.bg_primary};
    border: 1px solid {tokens.semantic.border_default};
    border-radius: {tokens.borders.radius_md}px;
    padding: {tokens.spacing.space_2}px;
    outline: none;
    selection-background-color: {tokens.semantic.state_selected};
}}

QListWidget::item, QListView::item,
QTreeWidget::item, QTreeView::item {{
    padding: {tokens.spacing.space_3}px {tokens.spacing.space_4}px;
    border-radius: {tokens.borders.radius_sm}px;
}}

QListWidget::item:hover, QListView::item:hover,
QTreeWidget::item:hover, QTreeView::item:hover {{
    background-color: {tokens.semantic.state_hover};
}}

QListWidget::item:selected, QListView::item:selected,
QTreeWidget::item:selected, QTreeView::item:selected {{
    background-color: {tokens.semantic.state_selected};
    color: {tokens.semantic.fg_on_accent};
}}

QTreeView::branch {{
    background-color: transparent;
}}

QTreeView::branch:has-siblings:!adjoins-item {{
    border-image: none;
}}

QTreeView::branch:has-siblings:adjoins-item {{
    border-image: none;
}}

QTreeView::branch:!has-children:!has-siblings:adjoins-item {{
    border-image: none;
}}

/* Using default Qt tree branch indicators */"""

    def _generate_table_styles(self, tokens: DesignTokens) -> str:
        """Generate table styles."""
        return f"""
/* Table Styles */
QTableWidget, QTableView, QTreeWidget {{
    background-color: {tokens.semantic.bg_primary};
    gridline-color: {tokens.components.table_border or tokens.semantic.border_subtle};
    border: 1px solid {tokens.semantic.border_default};
    border-radius: {tokens.borders.radius_md}px;
    selection-background-color: {tokens.components.table_row_selected or tokens.semantic.state_selected};
    alternate-background-color: {tokens.components.table_row_bg_alt or tokens.semantic.bg_secondary};
}}

QTableWidget::item, QTableView::item, QTreeWidget::item {{
    padding: {tokens.spacing.space_3}px {tokens.spacing.space_4}px;
    background-color: {tokens.components.table_row_bg or tokens.semantic.bg_primary};
    color: {tokens.semantic.fg_primary};
}}

QTableWidget::item:alternate, QTableView::item:alternate, QTreeWidget::item:alternate {{
    background-color: {tokens.components.table_row_bg_alt or tokens.semantic.bg_secondary};
}}

QTableWidget::item:hover, QTableView::item:hover, QTreeWidget::item:hover {{
    background-color: {tokens.components.table_row_hover or tokens.semantic.state_hover};
}}

QTableWidget::item:selected, QTableView::item:selected, QTreeWidget::item:selected {{
    background-color: {tokens.components.table_row_selected or tokens.semantic.state_selected};
    color: {tokens.semantic.fg_on_accent};
}}

/* Tree-specific styles for branch indicators */
QTreeWidget::branch {{
    background-color: transparent;
}}

QTreeWidget::branch:has-siblings:!adjoins-item {{
    border-image: none;
}}

QTreeWidget::branch:has-siblings:adjoins-item {{
    border-image: none;
}}

QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {{
    border-image: none;
}}

QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {{
    border-image: none;
    {"image: url(" + self._resolve_image_url(tokens.components.tree_branch_closed_image) + ");" if tokens.components.tree_branch_closed_image else "image: none;"}
}}

QTreeWidget::branch:open:has-children:!has-siblings,
QTreeWidget::branch:open:has-children:has-siblings {{
    border-image: none;
    {"image: url(" + self._resolve_image_url(tokens.components.tree_branch_open_image) + ");" if tokens.components.tree_branch_open_image else "image: none;"}
}}

QTreeWidget::branch:has-children:!has-siblings:closed:hover,
QTreeWidget::branch:closed:has-children:has-siblings:hover {{
    border-image: none;
    {"image: url(" + self._resolve_image_url(tokens.components.tree_branch_closed_hover_image) + ");" if tokens.components.tree_branch_closed_hover_image else ""}
}}

QTreeWidget::branch:open:has-children:!has-siblings:hover,
QTreeWidget::branch:open:has-children:has-siblings:hover {{
    border-image: none;
    {"image: url(" + self._resolve_image_url(tokens.components.tree_branch_open_hover_image) + ");" if tokens.components.tree_branch_open_hover_image else ""}
}}

QTreeWidget::branch:has-children:!has-siblings:closed:pressed,
QTreeWidget::branch:closed:has-children:has-siblings:pressed {{
    border-image: none;
    {"image: url(" + self._resolve_image_url(tokens.components.tree_branch_closed_pressed_image) + ");" if tokens.components.tree_branch_closed_pressed_image else ""}
}}

QTreeWidget::branch:open:has-children:!has-siblings:pressed,
QTreeWidget::branch:open:has-children:has-siblings:pressed {{
    border-image: none;
    {"image: url(" + self._resolve_image_url(tokens.components.tree_branch_open_pressed_image) + ");" if tokens.components.tree_branch_open_pressed_image else ""}
}}

QHeaderView::section {{
    background-color: {tokens.components.table_header_bg or tokens.semantic.bg_tertiary};
    color: {tokens.components.table_header_fg or tokens.semantic.fg_primary};
    padding: {tokens.spacing.space_3}px {tokens.spacing.space_4}px;
    border: none;
    border-right: 1px solid {tokens.semantic.border_subtle};
    border-bottom: 2px solid {tokens.semantic.border_default};
    font-weight: {tokens.typography.font_weight_semibold};
}}

QHeaderView::section:hover {{
    background-color: {tokens.semantic.state_hover};
}}

QTableCornerButton::section {{
    background-color: {tokens.components.table_header_bg or tokens.semantic.bg_tertiary};
    border: none;
    border-right: 1px solid {tokens.semantic.border_subtle};
    border-bottom: 2px solid {tokens.semantic.border_default};
}}"""

    def _generate_menu_styles(self, tokens: DesignTokens) -> str:
        """Generate menu and menubar styles."""
        return f"""
/* Menu Styles */
QMenuBar {{
    background-color: {tokens.semantic.bg_secondary};
    color: {tokens.semantic.fg_primary};
    border-bottom: 1px solid {tokens.semantic.border_default};
    padding: {tokens.spacing.space_1}px;
}}

QMenuBar::item {{
    padding: {tokens.spacing.space_2}px {tokens.spacing.space_6}px;
    border-radius: {tokens.borders.radius_sm}px;
    background-color: transparent;
}}

QMenuBar::item:selected {{
    background-color: {tokens.semantic.state_hover};
}}

QMenuBar::item:pressed {{
    background-color: {tokens.semantic.state_selected};
}}

QMenu {{
    background-color: {tokens.components.menu_bg or tokens.semantic.bg_elevated};
    border: 1px solid {tokens.semantic.border_default};
    border-radius: {tokens.borders.radius_md}px;
    padding: {tokens.spacing.space_2}px;
}}

QMenu::item {{
    padding: {tokens.spacing.space_3}px {tokens.spacing.space_12}px;
    border-radius: {tokens.borders.radius_sm}px;
    color: {tokens.components.menu_fg or tokens.semantic.fg_primary};
}}

QMenu::item:selected {{
    background-color: {tokens.components.menu_selected_bg or tokens.semantic.state_selected};
    color: {tokens.components.menu_selected_fg or tokens.semantic.fg_on_accent};
}}

QMenu::item:disabled {{
    color: {tokens.semantic.fg_tertiary};
}}

QMenu::separator {{
    height: 1px;
    background-color: {tokens.semantic.border_subtle};
    margin: {tokens.spacing.space_2}px {tokens.spacing.space_4}px;
}}

QMenu::icon {{
    padding-left: {tokens.spacing.space_4}px;
}}"""

    def _generate_tab_styles(self, tokens: DesignTokens) -> str:
        """Generate tab widget styles."""
        return f"""
/* Tab Styles */
QTabWidget::pane {{
    background-color: {tokens.semantic.bg_primary};
    border: 1px solid {tokens.semantic.border_default};
    border-radius: {tokens.borders.radius_md}px;
}}

QTabBar {{
    background-color: transparent;
}}

QTabBar::tab {{
    background-color: {tokens.components.tab_bg or tokens.semantic.bg_secondary};
    color: {tokens.components.tab_fg or tokens.semantic.fg_secondary};
    padding: {tokens.spacing.space_3}px {tokens.spacing.space_8}px;
    margin-right: {tokens.spacing.space_1}px;
    border-top-left-radius: {tokens.borders.radius_md}px;
    border-top-right-radius: {tokens.borders.radius_md}px;
    border: 1px solid {tokens.semantic.border_subtle};
    border-bottom: none;
}}

QTabBar::tab:selected {{
    background-color: {tokens.components.tab_active_bg or tokens.semantic.bg_primary};
    color: {tokens.components.tab_active_fg or tokens.semantic.fg_primary};
    border-color: {tokens.semantic.border_default};
    border-bottom: 1px solid {tokens.semantic.bg_primary};
    margin-bottom: -1px;
}}

QTabBar::tab:hover:!selected {{
    background-color: {tokens.components.tab_hover_bg or tokens.semantic.state_hover};
    color: {tokens.components.tab_hover_fg or tokens.semantic.fg_primary};
}}

QTabBar::tab:!selected {{
    margin-top: 2px;
}}"""

    def _generate_scrollbar_styles(self, tokens: DesignTokens) -> str:
        """Generate scrollbar styles with support for custom textures and comprehensive styling."""
        # Determine scrollbar dimensions
        scrollbar_width = tokens.components.scrollbar_width or 12
        scrollbar_height = tokens.components.scrollbar_height or 12

        # Arrow dimensions - support separate width/height or fall back to size
        arrow_size = tokens.components.scrollbar_arrow_size or scrollbar_width
        scrollbar_arrow_width = tokens.components.scrollbar_arrow_width or arrow_size
        scrollbar_arrow_height = tokens.components.scrollbar_arrow_height or arrow_size

        # Horizontal arrow dimensions (can be different from vertical)
        scrollbar_arrow_width_horizontal = (
            tokens.components.scrollbar_arrow_width_horizontal or scrollbar_arrow_width
        )
        scrollbar_arrow_height_horizontal = (
            tokens.components.scrollbar_arrow_height_horizontal or scrollbar_arrow_height
        )

        # Check if arrow buttons will be visible
        has_arrows = any([
            tokens.components.scrollbar_up_arrow_image,
            tokens.components.scrollbar_down_arrow_image,
            tokens.components.scrollbar_left_arrow_image,
            tokens.components.scrollbar_right_arrow_image,
        ])

        # Base scrollbar styles
        styles = [
            f"""
/* Scrollbar Styles */
QScrollBar {{
    background-color: {tokens.components.scrollbar_bg or tokens.semantic.bg_secondary};
    border: none;
    border-radius: {tokens.borders.radius_md}px;"""
        ]

        # Add background image if specified (use border-image if slice is defined for 9-slice scaling)
        if tokens.components.scrollbar_bg_image:
            bg_url = self._resolve_image_url(tokens.components.scrollbar_bg_image)
            if tokens.components.scrollbar_bg_border_slice:
                styles.append(
                    f"    border-image: url({bg_url}) {tokens.components.scrollbar_bg_border_slice};"
                )
            else:
                styles.append(f"    background-image: url({bg_url});")
                styles.append("    background-repeat: repeat;")

        styles.append("""
}

QScrollBar:horizontal {""")
        styles.append(f"    height: {scrollbar_height}px;")
        # Reserve space for left/right arrow buttons if they exist
        # Margins must match button width (horizontal scrollbar uses horizontal arrow width)
        if has_arrows:
            styles.append(
                f"    margin: 0px {scrollbar_arrow_width_horizontal}px 0px {scrollbar_arrow_width_horizontal}px;"
            )
        styles.append("""
}

QScrollBar:vertical {""")
        styles.append(f"    width: {scrollbar_width}px;")
        # Reserve space for top/bottom arrow buttons if they exist
        # Margins must match button height (vertical scrollbar uses arrow height)
        if has_arrows:
            styles.append(
                f"    margin: {scrollbar_arrow_height}px 0px {scrollbar_arrow_height}px 0px;"
            )
        styles.append("""
}

/* Scrollbar Handle (Thumb) */
QScrollBar::handle {""")

        # Add thumb image if specified
        if tokens.components.scrollbar_thumb_image:
            thumb_url = self._resolve_image_url(tokens.components.scrollbar_thumb_image)

            # Use border-image for 9-slice if border_slice is defined
            if tokens.components.scrollbar_thumb_border_slice:
                # border-image fills the entire element, no background-color needed
                # Qt requires border-width to be set for border-image to work correctly
                slice_values = tokens.components.scrollbar_thumb_border_slice.split()
                border_width = " ".join([f"{v}px" for v in slice_values])
                styles.append(f"    border-width: {border_width};")
                styles.append(
                    f"    border-image: url({thumb_url}) {tokens.components.scrollbar_thumb_border_slice} fill stretch;"
                )
            else:
                # Fallback to background-image for simple scaling
                styles.append(
                    f"    background-color: {tokens.components.scrollbar_thumb or tokens.semantic.fg_tertiary};"
                )
                styles.append(f"    background-image: url({thumb_url});")
                styles.append("    background-position: center;")
                styles.append("    background-repeat: no-repeat;")
                styles.append("    border: none;")
        else:
            # No image, use solid color with border and border-radius
            styles.append(
                f"    background-color: {tokens.components.scrollbar_thumb or tokens.semantic.fg_tertiary};"
            )
            if tokens.components.scrollbar_thumb_border:
                styles.append(f"    border: 1px solid {tokens.components.scrollbar_thumb_border};")
            styles.append(
                f"    border-radius: {tokens.borders.radius_md - 2 if tokens.borders.radius_md > 2 else 0}px;"
            )

        styles.append("""    min-height: 20px;
    min-width: 20px;
}

QScrollBar::handle:hover {""")

        # Add hover image if specified
        if tokens.components.scrollbar_thumb_hover_image:
            hover_url = self._resolve_image_url(tokens.components.scrollbar_thumb_hover_image)

            # Use border-image for 9-slice if border_slice is defined
            # Inherit from normal state if hover-specific slice not defined
            border_slice = (
                tokens.components.scrollbar_thumb_hover_border_slice
                or tokens.components.scrollbar_thumb_border_slice
            )
            if border_slice:
                # border-image fills the entire element, no background-color needed
                slice_values = border_slice.split()
                border_width = " ".join([f"{v}px" for v in slice_values])
                styles.append(f"    border-width: {border_width};")
                styles.append(f"    border-image: url({hover_url}) {border_slice} fill stretch;")
            else:
                # Fallback to background-image for simple scaling
                styles.append(
                    f"    background-color: {tokens.components.scrollbar_thumb_hover or tokens.semantic.fg_secondary};"
                )
                styles.append(f"    background-image: url({hover_url});")
                styles.append("    background-position: center;")
                styles.append("    background-repeat: no-repeat;")
                styles.append("    border: none;")
        else:
            # No hover image, use solid color
            styles.append(
                f"    background-color: {tokens.components.scrollbar_thumb_hover or tokens.semantic.fg_secondary};"
            )

        styles.append("""
}

QScrollBar::handle:pressed {""")

        # Add pressed image if specified
        if tokens.components.scrollbar_thumb_pressed_image:
            pressed_url = self._resolve_image_url(tokens.components.scrollbar_thumb_pressed_image)

            # Use border-image for 9-slice if border_slice is defined
            # Inherit from normal state if pressed-specific slice not defined
            border_slice = (
                tokens.components.scrollbar_thumb_pressed_border_slice
                or tokens.components.scrollbar_thumb_border_slice
            )
            if border_slice:
                # border-image fills the entire element, no background-color needed
                slice_values = border_slice.split()
                border_width = " ".join([f"{v}px" for v in slice_values])
                styles.append(f"    border-width: {border_width};")
                styles.append(f"    border-image: url({pressed_url}) {border_slice} fill stretch;")
            else:
                # Fallback to background-image for simple scaling
                if tokens.components.scrollbar_thumb_pressed:
                    styles.append(
                        f"    background-color: {tokens.components.scrollbar_thumb_pressed};"
                    )
                elif tokens.components.scrollbar_thumb_hover:
                    styles.append(
                        f"    background-color: {tokens.components.scrollbar_thumb_hover};"
                    )
                styles.append(f"    background-image: url({pressed_url});")
                styles.append("    background-position: center;")
                styles.append("    background-repeat: no-repeat;")
                styles.append("    border: none;")
        # No pressed image, use solid color (fallback to hover color if pressed not specified)
        elif tokens.components.scrollbar_thumb_pressed:
            styles.append(f"    background-color: {tokens.components.scrollbar_thumb_pressed};")
        elif tokens.components.scrollbar_thumb_hover:
            styles.append(f"    background-color: {tokens.components.scrollbar_thumb_hover};")

        styles.append("""
}

/* Scrollbar Arrow Buttons */
QScrollBar::add-line, QScrollBar::sub-line {""")

        # If arrow images are specified, show arrow buttons
        if has_arrows:
            # Don't set background-color here - we'll use images as backgrounds
            styles.append("    border: none;")
        else:
            # Hide arrow buttons by default
            styles.append("    background: none;")
            styles.append("    border: none;")
            styles.append("    width: 0px;")
            styles.append("    height: 0px;")

        styles.append("""
}""")

        # Only add hover/pressed states if arrow buttons are visible
        if has_arrows:
            styles.append("""
QScrollBar::add-line:hover, QScrollBar::sub-line:hover {
    background-color: rgba(0, 0, 0, 0.1);
}

QScrollBar::add-line:pressed, QScrollBar::sub-line:pressed {
    background-color: rgba(0, 0, 0, 0.2);
}""")

        styles.append("""
/* Vertical Scrollbar Arrows */
QScrollBar::sub-line:vertical {
    subcontrol-position: top;
    subcontrol-origin: margin;
}

QScrollBar::add-line:vertical {
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}

/* Horizontal Scrollbar Arrows */
QScrollBar::sub-line:horizontal {
    subcontrol-position: left;
    subcontrol-origin: margin;
}

QScrollBar::add-line:horizontal {
    subcontrol-position: right;
    subcontrol-origin: margin;
}""")

        # Add button background images (use full texture, not just arrow icon)
        # Include sizing here to ensure proper application
        if tokens.components.scrollbar_up_arrow_image:
            up_arrow_url = self._resolve_image_url(tokens.components.scrollbar_up_arrow_image)
            styles.append(f"""
QScrollBar::sub-line:vertical {{
    width: {scrollbar_arrow_width}px;
    height: {scrollbar_arrow_height}px;
    background-image: url({up_arrow_url});
    background-repeat: no-repeat;
    background-position: center;
}}""")

        if tokens.components.scrollbar_down_arrow_image:
            down_arrow_url = self._resolve_image_url(tokens.components.scrollbar_down_arrow_image)
            styles.append(f"""
QScrollBar::add-line:vertical {{
    width: {scrollbar_arrow_width}px;
    height: {scrollbar_arrow_height}px;
    background-image: url({down_arrow_url});
    background-repeat: no-repeat;
    background-position: center;
}}""")

        if tokens.components.scrollbar_left_arrow_image:
            left_arrow_url = self._resolve_image_url(tokens.components.scrollbar_left_arrow_image)
            styles.append(f"""
QScrollBar::sub-line:horizontal {{
    width: {scrollbar_arrow_width_horizontal}px;
    height: {scrollbar_arrow_height_horizontal}px;
    background-image: url({left_arrow_url});
    background-repeat: no-repeat;
    background-position: center;
}}""")

        if tokens.components.scrollbar_right_arrow_image:
            right_arrow_url = self._resolve_image_url(tokens.components.scrollbar_right_arrow_image)
            styles.append(f"""
QScrollBar::add-line:horizontal {{
    width: {scrollbar_arrow_width_horizontal}px;
    height: {scrollbar_arrow_height_horizontal}px;
    background-image: url({right_arrow_url});
    background-repeat: no-repeat;
    background-position: center;
}}""")

        styles.append("""
/* Scrollbar Page Areas (track) */
QScrollBar::add-page, QScrollBar::sub-page {
    background: none;
}""")

        return "".join(styles)

    def _generate_container_styles(self, tokens: DesignTokens) -> str:
        """Generate container widget styles."""
        return f"""
/* Container Styles */
QGroupBox {{
    background-color: {tokens.semantic.bg_secondary};
    border: 1px solid {tokens.semantic.border_default};
    border-radius: {tokens.borders.radius_md}px;
    margin-top: {tokens.spacing.space_8}px;
    padding-top: {tokens.spacing.space_8}px;
    font-weight: {tokens.typography.font_weight_semibold};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: {tokens.spacing.space_4}px;
    padding: 0 {tokens.spacing.space_2}px;
    color: {tokens.semantic.fg_primary};
    background-color: {tokens.semantic.bg_secondary};
}}

QFrame {{
    background-color: transparent;
}}

QFrame[frameShape="HLine"], QFrame[frameShape="VLine"] {{
    background-color: {tokens.semantic.border_subtle};
}}

QFrame[frameShape="HLine"] {{
    height: 1px;
}}

QFrame[frameShape="VLine"] {{
    width: 1px;
}}

QSplitter::handle {{
    background-color: {tokens.semantic.border_default};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

QSplitter::handle:hover {{
    background-color: {tokens.semantic.action_primary};
}}

/* Card Style */
QFrame[card="true"] {{
    background-color: {tokens.semantic.bg_elevated};
    border: 1px solid {tokens.semantic.border_subtle};
    border-radius: {tokens.borders.radius_lg}px;
    padding: {tokens.spacing.space_8}px;
}}"""

    def _generate_dialog_styles(self, tokens: DesignTokens) -> str:
        """Generate dialog and message box styles."""
        return f"""
/* Dialog Styles */
QDialog {{
    background-color: {tokens.semantic.bg_primary};
}}

QDialogButtonBox {{
    background-color: transparent;
}}

QMessageBox {{
    background-color: {tokens.semantic.bg_primary};
}}

QMessageBox QLabel {{
    color: {tokens.semantic.fg_primary};
    min-width: 240px;
}}

/* Progress Bar */
QProgressBar {{
    background-color: {tokens.semantic.bg_tertiary};
    border: 1px solid {tokens.semantic.border_subtle};
    border-radius: {tokens.borders.radius_md}px;
    text-align: center;
    height: 20px;
    color: {tokens.semantic.fg_primary};
}}

QProgressBar::chunk {{
    background-color: {tokens.semantic.action_primary};
    border-radius: {tokens.borders.radius_md - 1 if tokens.borders.radius_md > 1 else 0}px;
}}"""

    def _generate_misc_styles(self, tokens: DesignTokens) -> str:
        """Generate miscellaneous widget styles."""
        return f"""
/* ToolBar */
QToolBar {{
    background-color: {tokens.semantic.bg_secondary};
    border: none;
    spacing: {tokens.spacing.space_2}px;
    padding: {tokens.spacing.space_2}px;
}}

QToolBar::separator {{
    background-color: {tokens.semantic.border_subtle};
    width: 1px;
    height: 1px;
    margin: {tokens.spacing.space_2}px;
}}

/* StatusBar */
QStatusBar {{
    background-color: {tokens.semantic.bg_secondary};
    color: {tokens.semantic.fg_secondary};
    border-top: 1px solid {tokens.semantic.border_default};
}}

QStatusBar::item {{
    border: none;
}}

/* ToolTip */
QToolTip {{
    background-color: {tokens.semantic.bg_elevated or tokens.semantic.bg_primary};
    color: {tokens.semantic.fg_primary};
    border: 1px solid {tokens.semantic.border_default};
    padding: {tokens.spacing.space_2}px {tokens.spacing.space_4}px;
    border-radius: {tokens.borders.radius_md}px;
}}

/* SpinBox Buttons - using default Qt arrows */
QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
}}

/* Date/Time Edit */
QDateEdit, QTimeEdit, QDateTimeEdit {{
    background-color: {tokens.components.input_bg or tokens.semantic.bg_secondary};
    color: {tokens.components.input_fg or tokens.semantic.fg_primary};
    border: 1px solid {tokens.components.input_border or tokens.semantic.border_default};
    border-radius: {tokens.borders.radius_md}px;
    padding: {tokens.spacing.space_3}px {tokens.spacing.space_4}px;
}}

QDateEdit:focus, QTimeEdit:focus, QDateTimeEdit:focus {{
    border-color: {tokens.semantic.border_focus};
}}

QCalendarWidget {{
    background-color: {tokens.semantic.bg_elevated};
    border: 1px solid {tokens.semantic.border_default};
    border-radius: {tokens.borders.radius_lg}px;
}}

QCalendarWidget QWidget {{
    alternate-background-color: {tokens.semantic.bg_secondary};
}}

QCalendarWidget QAbstractItemView {{
    background-color: {tokens.semantic.bg_primary};
    selection-background-color: {tokens.semantic.state_selected};
    selection-color: {tokens.semantic.fg_on_accent};
}}

QCalendarWidget QToolButton {{
    background-color: transparent;
    color: {tokens.semantic.fg_primary};
}}

QCalendarWidget QToolButton:hover {{
    background-color: {tokens.semantic.state_hover};
    border-radius: {tokens.borders.radius_sm}px;
}}

/* Dock Widget */
QDockWidget {{
    background-color: {tokens.semantic.bg_secondary};
    color: {tokens.semantic.fg_primary};
    border: 1px solid {tokens.semantic.border_default};
}}

QDockWidget::title {{
    background-color: {tokens.semantic.bg_tertiary};
    padding: {tokens.spacing.space_3}px;
    border-bottom: 1px solid {tokens.semantic.border_default};
}}

QDockWidget::close-button, QDockWidget::float-button {{
    background-color: transparent;
    border: none;
    padding: 2px;
}}

QDockWidget::close-button:hover, QDockWidget::float-button:hover {{
    background-color: {tokens.semantic.state_hover};
    border-radius: {tokens.borders.radius_sm}px;
}}"""

    def _get_icon_style(self, icon_name: str) -> str:
        """Get icon URL style for use in stylesheets.

        Args:
            icon_name: Name of the icon file

        Returns:
            CSS image property with icon URL or empty string if not found
        """
        if self._resource_manager:
            icon_url = self._resource_manager.get_resource_url("icons", icon_name)
            if icon_url:
                return f"image: url({icon_url});"
        # Fallback to relative path
        return f"image: url(resources/icons/{icon_name});"

    def _resolve_image_url(self, image_path: str) -> str:
        """Resolve an image path to a proper path for Qt stylesheets.

        Args:
            image_path: Path to image file (relative or absolute)

        Returns:
            Properly formatted path for use in Qt stylesheets (NOT a URL)

        Note:
            Qt stylesheets don't use file:/// URLs - they use plain file paths.
            Paths must use forward slashes, even on Windows.
        """
        from pathlib import Path

        if not image_path:
            return ""

        path = Path(image_path)

        # If already a URL (qrc or http), return as-is
        if image_path.startswith(("http://", "https://", "qrc:")):
            return image_path

        # Remove file:// prefix if present (not needed for Qt stylesheets)
        if image_path.startswith("file://"):
            image_path = image_path.replace("file:///", "").replace("file://", "")
            path = Path(image_path)

        # Convert to absolute path if needed
        if not path.is_absolute():
            # Try to resolve relative to current working directory
            with suppress(Exception):
                path = path.resolve()

        # Return path with forward slashes (works on all platforms for Qt)
        return path.as_posix()
