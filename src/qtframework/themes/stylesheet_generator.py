"""Stylesheet generator for converting design tokens to Qt stylesheets."""

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from qtframework.themes.tokens import DesignTokens


class StylesheetGenerator:
    """Generate Qt stylesheets from design tokens."""

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
        return f"""
/* Button Styles */
QPushButton {{
    background-color: {tokens.components.button_secondary_bg or tokens.semantic.bg_secondary};
    color: {tokens.components.button_secondary_fg or tokens.semantic.fg_primary};
    border: 1px solid {tokens.components.button_secondary_border or tokens.semantic.border_default};
    border-radius: {tokens.borders.radius_md}px;
    padding: {tokens.spacing.space_3}px {tokens.spacing.space_8}px;
    font-weight: {tokens.typography.font_weight_medium};
    min-height: {tokens.spacing.space_16}px;
}}

QPushButton:hover {{
    background-color: {tokens.semantic.state_hover};
    border-color: {tokens.semantic.border_strong};
}}

QPushButton:pressed {{
    background-color: {tokens.semantic.state_selected};
}}

QPushButton:disabled {{
    background-color: {tokens.semantic.state_disabled};
    color: {tokens.semantic.fg_tertiary};
    border-color: {tokens.semantic.border_subtle};
}}

QPushButton:focus {{
    border-color: {tokens.semantic.border_focus};
    outline: none;
}}

/* Primary Button */
QPushButton[variant="primary"] {{
    background-color: {tokens.components.button_primary_bg or tokens.semantic.action_primary};
    color: {tokens.components.button_primary_fg or tokens.semantic.fg_on_accent};
    border: none;
}}

QPushButton[variant="primary"]:hover {{
    background-color: {tokens.semantic.action_primary_hover};
}}

QPushButton[variant="primary"]:pressed {{
    background-color: {tokens.semantic.action_primary_active};
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
}}"""

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
    background-color: {tokens.components.input_bg or tokens.semantic.bg_secondary};
    color: {tokens.components.input_fg or tokens.semantic.fg_primary};
    border: 1px solid {tokens.components.input_border or tokens.semantic.border_default};
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
    width: 24px;
}}

QComboBox::down-arrow {{
    image: url(resources/icons/dropdown-arrow-filled.svg);
    width: 16px;
    height: 16px;
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
QTableWidget, QTableView {{
    background-color: {tokens.semantic.bg_primary};
    gridline-color: {tokens.components.table_border or tokens.semantic.border_subtle};
    border: 1px solid {tokens.semantic.border_default};
    border-radius: {tokens.borders.radius_md}px;
    selection-background-color: {tokens.components.table_row_selected or tokens.semantic.state_selected};
}}

QTableWidget::item, QTableView::item {{
    padding: {tokens.spacing.space_3}px {tokens.spacing.space_4}px;
    background-color: {tokens.components.table_row_bg or tokens.semantic.bg_primary};
    color: {tokens.semantic.fg_primary};
}}

QTableWidget::item:alternate, QTableView::item:alternate {{
    background-color: {tokens.components.table_row_bg_alt or tokens.semantic.bg_secondary};
}}

QTableWidget::item:hover, QTableView::item:hover {{
    background-color: {tokens.components.table_row_hover or tokens.semantic.state_hover};
}}

QTableWidget::item:selected, QTableView::item:selected {{
    background-color: {tokens.components.table_row_selected or tokens.semantic.state_selected};
    color: {tokens.semantic.fg_on_accent};
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
        """Generate scrollbar styles."""
        return f"""
/* Scrollbar Styles */
QScrollBar {{
    background-color: {tokens.components.scrollbar_bg or tokens.semantic.bg_secondary};
    border: none;
    border-radius: {tokens.borders.radius_md}px;
}}

QScrollBar:horizontal {{
    height: 12px;
}}

QScrollBar:vertical {{
    width: 12px;
}}

QScrollBar::handle {{
    background-color: {tokens.components.scrollbar_thumb or tokens.semantic.fg_tertiary};
    border-radius: {tokens.borders.radius_md - 2 if tokens.borders.radius_md > 2 else 0}px;
    min-height: 20px;
    min-width: 20px;
}}

QScrollBar::handle:hover {{
    background-color: {tokens.components.scrollbar_thumb_hover or tokens.semantic.fg_secondary};
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    background: none;
    border: none;
}}

QScrollBar::add-page, QScrollBar::sub-page {{
    background: none;
}}"""

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
