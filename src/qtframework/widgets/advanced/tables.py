"""Advanced table widgets with filtering, sorting, and search capabilities."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal, QSortFilterProxyModel, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem, QColor, QBrush
from PySide6.QtWidgets import (
    QApplication,
    QHeaderView,
    QTableView,
    QTreeView,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QAbstractItemView,
)


class DataTable(QWidget):
    """Enhanced data table widget with filtering and sorting."""

    row_selected = Signal(int)
    cell_edited = Signal(int, int, str)
    row_double_clicked = Signal(int)

    def __init__(
        self,
        rows: int = 0,
        columns: int = 0,
        headers: list[str] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize data table."""
        super().__init__(parent)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Search/filter bar
        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(0, 0, 0, 5)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self._on_search_changed)

        self.column_filter = QComboBox()
        self.column_filter.addItem("All Columns")
        if headers:
            self.column_filter.addItems(headers)
        self.column_filter.currentIndexChanged.connect(self._on_filter_column_changed)

        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(QLabel("in"))
        filter_layout.addWidget(self.column_filter)
        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        # Table widget
        self.table = QTableWidget(rows, columns)
        if headers:
            self.set_headers(headers)

        # Configure table
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)

        # Connect signals
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.itemChanged.connect(self._on_item_changed)
        self.table.itemDoubleClicked.connect(self._on_item_double_clicked)

        layout.addWidget(self.table)

        # Store original data for filtering
        self._original_data: list[list[Any]] = []
        self._filter_column = -1  # -1 means all columns

        # Apply theme-based styling and connect to theme changes
        self._apply_theme_style()
        self._connect_theme_signals()

    def _apply_theme_style(self) -> None:
        """Apply theme-based styling to the table."""
        # Get theme from application
        app = QApplication.instance()
        if hasattr(app, 'theme_manager'):
            theme = app.theme_manager.get_theme()
            if theme and theme.colors:
                colors = theme.colors
                self.table.setStyleSheet(f"""
                    QTableWidget {{
                        gridline-color: {colors.table_grid};
                        selection-background-color: {colors.table_row_selected};
                        background-color: {colors.background};
                    }}
                    QTableWidget::item {{
                        padding: 5px;
                        color: {colors.text_primary};
                    }}
                    QTableWidget::item:alternate {{
                        background-color: {colors.table_row_bg_alt};
                    }}
                    QTableWidget::item:hover {{
                        background-color: {colors.table_row_hover};
                    }}
                    QHeaderView::section {{
                        background-color: {colors.table_header_bg};
                        color: {colors.text_primary};
                        padding: 5px;
                        border: 1px solid {colors.table_grid};
                        font-weight: bold;
                    }}
                """)
                return

        # Fallback to palette-based styling
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: palette(mid);
                selection-background-color: palette(highlight);
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: palette(alternate-base);
                color: palette(text);
                padding: 5px;
                border: 1px solid palette(mid);
                font-weight: bold;
            }
        """)

    def _connect_theme_signals(self) -> None:
        """Connect to theme change signals."""
        app = QApplication.instance()
        if hasattr(app, 'theme_manager'):
            app.theme_manager.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme_name: str) -> None:
        """Handle theme change."""
        self._apply_theme_style()

    def set_headers(self, headers: list[str]) -> None:
        """Set table headers."""
        self.table.setHorizontalHeaderLabels(headers)
        # Update column filter
        self.column_filter.clear()
        self.column_filter.addItem("All Columns")
        self.column_filter.addItems(headers)

    def set_data(self, data: list[list[Any]]) -> None:
        """Set table data.

        Args:
            data: 2D list of data
        """
        self._original_data = [row[:] for row in data]  # Store copy
        self.table.setRowCount(len(data))
        if data:
            self.table.setColumnCount(len(data[0]))

        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)

    def get_data(self) -> list[list[str]]:
        """Get table data.

        Returns:
            2D list of data
        """
        data = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data

    def add_row(self, data: list[Any] | None = None) -> None:
        """Add a row to the table.

        Args:
            data: Row data
        """
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)

        if data:
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row_count, col, item)
            # Add to original data
            self._original_data.append(data[:])

    def remove_selected_rows(self) -> None:
        """Remove selected rows."""
        rows = set()
        for item in self.table.selectedItems():
            rows.add(item.row())

        for row in sorted(rows, reverse=True):
            self.table.removeRow(row)
            if row < len(self._original_data):
                self._original_data.pop(row)

    def clear_selection(self) -> None:
        """Clear current selection."""
        self.table.clearSelection()

    def select_row(self, row: int) -> None:
        """Select a specific row."""
        self.table.selectRow(row)

    def get_selected_rows(self) -> list[int]:
        """Get list of selected row indices."""
        rows = set()
        for item in self.table.selectedItems():
            rows.add(item.row())
        return sorted(rows)

    def _on_selection_changed(self) -> None:
        """Handle selection change."""
        selected = self.table.selectedItems()
        if selected:
            self.row_selected.emit(selected[0].row())

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        """Handle item change."""
        if item:
            self.cell_edited.emit(item.row(), item.column(), item.text())

    def _on_item_double_clicked(self, item: QTableWidgetItem) -> None:
        """Handle item double click."""
        if item:
            self.row_double_clicked.emit(item.row())

    def _on_search_changed(self, text: str) -> None:
        """Handle search text change."""
        self._apply_filter(text)

    def _on_filter_column_changed(self, index: int) -> None:
        """Handle filter column change."""
        self._filter_column = index - 1  # -1 for "All Columns"
        self._apply_filter(self.search_input.text())

    def _apply_filter(self, filter_text: str) -> None:
        """Apply filter to table rows."""
        filter_text = filter_text.lower()

        for row in range(self.table.rowCount()):
            should_hide = True

            if self._filter_column == -1:  # All columns
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and filter_text in item.text().lower():
                        should_hide = False
                        break
            else:  # Specific column
                item = self.table.item(row, self._filter_column)
                if item and filter_text in item.text().lower():
                    should_hide = False

            self.table.setRowHidden(row, should_hide if filter_text else False)

    def enable_sorting(self, enable: bool = True) -> None:
        """Enable column sorting.

        Args:
            enable: Enable sorting
        """
        self.table.setSortingEnabled(enable)

    def set_column_width(self, column: int, width: int) -> None:
        """Set column width."""
        self.table.setColumnWidth(column, width)

    def set_row_color(self, row: int, color: QColor) -> None:
        """Set background color for a row."""
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item:
                item.setBackground(QBrush(color))


class TreeTable(QWidget):
    """Enhanced tree table widget with search and expandable rows."""

    item_selected = Signal(str)
    item_expanded = Signal(str)
    item_double_clicked = Signal(str)

    def __init__(
        self,
        headers: list[str] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize tree table."""
        super().__init__(parent)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Search bar
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 5)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tree...")
        self.search_input.textChanged.connect(self._on_search_changed)

        self.expand_all_btn = QPushButton("Expand All")
        self.expand_all_btn.clicked.connect(self._expand_all)

        self.collapse_all_btn = QPushButton("Collapse All")
        self.collapse_all_btn.clicked.connect(self._collapse_all)

        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        search_layout.addWidget(self.expand_all_btn)
        search_layout.addWidget(self.collapse_all_btn)

        layout.addLayout(search_layout)

        # Tree widget
        self.tree = QTreeWidget()
        if headers:
            self.set_headers(headers)

        # Configure tree
        self.tree.setAlternatingRowColors(True)
        self.tree.setAnimated(True)
        self.tree.setExpandsOnDoubleClick(True)
        self.tree.setSortingEnabled(True)

        # Connect signals
        self._setup_connections()

        layout.addWidget(self.tree)

        # Apply theme-based styling and connect to theme changes
        self._apply_theme_style()
        self._connect_theme_signals()

    def _apply_theme_style(self) -> None:
        """Apply theme-based styling to the tree."""
        # Get theme from application
        app = QApplication.instance()
        if hasattr(app, 'theme_manager'):
            theme = app.theme_manager.get_theme()
            if theme and theme.colors:
                colors = theme.colors
                self.tree.setStyleSheet(f"""
                    QTreeWidget {{
                        selection-background-color: {colors.table_row_selected};
                        background-color: {colors.background};
                    }}
                    QTreeWidget::item {{
                        padding: 3px;
                        color: {colors.text_primary};
                    }}
                    QTreeWidget::item:hover {{
                        background-color: {colors.table_row_hover};
                    }}
                    QTreeWidget::item:selected {{
                        background-color: {colors.table_row_selected};
                    }}
                    QHeaderView::section {{
                        background-color: {colors.table_header_bg};
                        color: {colors.text_primary};
                        padding: 5px;
                        border: 1px solid {colors.table_grid};
                        font-weight: bold;
                    }}
                """)
                return

        # Fallback to palette-based styling
        self.tree.setStyleSheet("""
            QTreeWidget {
                selection-background-color: palette(highlight);
            }
            QTreeWidget::item {
                padding: 3px;
            }
            QHeaderView::section {
                background-color: palette(alternate-base);
                color: palette(text);
                padding: 5px;
                border: 1px solid palette(mid);
                font-weight: bold;
            }
        """)

    def _connect_theme_signals(self) -> None:
        """Connect to theme change signals."""
        app = QApplication.instance()
        if hasattr(app, 'theme_manager'):
            app.theme_manager.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme_name: str) -> None:
        """Handle theme change."""
        self._apply_theme_style()

    def _setup_connections(self) -> None:
        """Setup signal connections."""
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.itemExpanded.connect(self._on_item_expanded)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)

    def set_headers(self, headers: list[str]) -> None:
        """Set tree headers."""
        self.tree.setHeaderLabels(headers)
        self.tree.setColumnCount(len(headers))

    def add_item(
        self,
        parent_item: QTreeWidgetItem | None,
        values: list[str],
        data: Any = None,
    ) -> QTreeWidgetItem:
        """Add item to tree.

        Args:
            parent_item: Parent item (None for root)
            values: Column values
            data: Item data

        Returns:
            Created tree item
        """
        if parent_item:
            item = QTreeWidgetItem(parent_item, values)
        else:
            item = QTreeWidgetItem(self.tree, values)

        if data:
            item.setData(0, Qt.ItemDataRole.UserRole, data)

        return item

    def get_selected_item(self) -> QTreeWidgetItem | None:
        """Get selected item."""
        items = self.tree.selectedItems()
        return items[0] if items else None

    def get_item_data(self, item: QTreeWidgetItem) -> Any:
        """Get data stored in item."""
        return item.data(0, Qt.ItemDataRole.UserRole)

    def clear(self) -> None:
        """Clear all items."""
        self.tree.clear()

    def _on_selection_changed(self) -> None:
        """Handle selection change."""
        selected = self.tree.selectedItems()
        if selected:
            self.item_selected.emit(selected[0].text(0))

    def _on_item_expanded(self, item: QTreeWidgetItem) -> None:
        """Handle item expansion."""
        if item:
            self.item_expanded.emit(item.text(0))

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle item double click."""
        if item:
            self.item_double_clicked.emit(item.text(0))

    def _on_search_changed(self, text: str) -> None:
        """Handle search text change."""
        self._apply_search_filter(text.lower())

    def _apply_search_filter(self, search_text: str) -> None:
        """Apply search filter to tree items."""
        def filter_item(item: QTreeWidgetItem, text: str) -> bool:
            """Recursively filter items."""
            # Check if item matches
            item_matches = False
            for col in range(item.columnCount()):
                if text in item.text(col).lower():
                    item_matches = True
                    break

            # Check children
            child_matches = False
            for i in range(item.childCount()):
                child = item.child(i)
                if filter_item(child, text):
                    child_matches = True

            # Show item if it or any child matches
            should_show = item_matches or child_matches or not text
            item.setHidden(not should_show)

            # Expand if children match but item doesn't
            if child_matches and not item_matches and text:
                item.setExpanded(True)

            return should_show

        # Apply to all root items
        for i in range(self.tree.topLevelItemCount()):
            filter_item(self.tree.topLevelItem(i), search_text)

    def _expand_all(self) -> None:
        """Expand all tree items."""
        self.tree.expandAll()

    def _collapse_all(self) -> None:
        """Collapse all tree items."""
        self.tree.collapseAll()

    def set_column_width(self, column: int, width: int) -> None:
        """Set column width."""
        self.tree.setColumnWidth(column, width)

    def set_item_color(self, item: QTreeWidgetItem, color: QColor) -> None:
        """Set item background color."""
        for col in range(item.columnCount()):
            item.setBackground(col, QBrush(color))

    def set_item_icon(self, item: QTreeWidgetItem, column: int, icon: Any) -> None:
        """Set item icon."""
        item.setIcon(column, icon)


class PivotTable(QWidget):
    """Pivot table widget for data aggregation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize pivot table."""
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()

        self.row_field = QComboBox()
        self.col_field = QComboBox()
        self.value_field = QComboBox()
        self.agg_function = QComboBox()
        self.agg_function.addItems(["Sum", "Average", "Count", "Min", "Max"])

        controls_layout.addWidget(QLabel("Rows:"))
        controls_layout.addWidget(self.row_field)
        controls_layout.addWidget(QLabel("Columns:"))
        controls_layout.addWidget(self.col_field)
        controls_layout.addWidget(QLabel("Values:"))
        controls_layout.addWidget(self.value_field)
        controls_layout.addWidget(QLabel("Aggregate:"))
        controls_layout.addWidget(self.agg_function)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_pivot)
        controls_layout.addWidget(refresh_btn)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Pivot table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        self._source_data: list[dict[str, Any]] = []

    def set_data(self, data: list[dict[str, Any]]) -> None:
        """Set source data for pivot table."""
        self._source_data = data

        if data:
            # Update field combos
            fields = list(data[0].keys())
            self.row_field.clear()
            self.row_field.addItems(fields)
            self.col_field.clear()
            self.col_field.addItems(fields)
            self.value_field.clear()
            self.value_field.addItems(fields)

    def _refresh_pivot(self) -> None:
        """Refresh pivot table based on current settings."""
        if not self._source_data:
            return

        row_field = self.row_field.currentText()
        col_field = self.col_field.currentText()
        value_field = self.value_field.currentText()
        agg_func = self.agg_function.currentText()

        if not all([row_field, col_field, value_field]):
            return

        # Calculate pivot
        pivot_data = self._calculate_pivot(
            row_field, col_field, value_field, agg_func
        )

        # Display in table
        self._display_pivot(pivot_data, row_field, col_field)

    def _calculate_pivot(
        self,
        row_field: str,
        col_field: str,
        value_field: str,
        agg_func: str,
    ) -> dict[str, dict[str, float]]:
        """Calculate pivot table data."""
        pivot = {}

        for record in self._source_data:
            row_val = str(record.get(row_field, ""))
            col_val = str(record.get(col_field, ""))
            value = record.get(value_field, 0)

            if row_val not in pivot:
                pivot[row_val] = {}
            if col_val not in pivot[row_val]:
                pivot[row_val][col_val] = []

            try:
                pivot[row_val][col_val].append(float(value))
            except (ValueError, TypeError):
                pivot[row_val][col_val].append(0)

        # Apply aggregation
        for row_val in pivot:
            for col_val in pivot[row_val]:
                values = pivot[row_val][col_val]
                if agg_func == "Sum":
                    pivot[row_val][col_val] = sum(values)
                elif agg_func == "Average":
                    pivot[row_val][col_val] = sum(values) / len(values) if values else 0
                elif agg_func == "Count":
                    pivot[row_val][col_val] = len(values)
                elif agg_func == "Min":
                    pivot[row_val][col_val] = min(values) if values else 0
                elif agg_func == "Max":
                    pivot[row_val][col_val] = max(values) if values else 0

        return pivot

    def _display_pivot(
        self,
        pivot_data: dict[str, dict[str, float]],
        row_label: str,
        col_label: str,
    ) -> None:
        """Display pivot data in table."""
        # Get unique column values
        col_values = set()
        for row_data in pivot_data.values():
            col_values.update(row_data.keys())
        col_values = sorted(col_values)

        # Set up table
        self.table.setRowCount(len(pivot_data))
        self.table.setColumnCount(len(col_values) + 1)
        self.table.setHorizontalHeaderLabels([row_label] + col_values)

        # Fill table
        for row_idx, (row_val, row_data) in enumerate(sorted(pivot_data.items())):
            # Row header
            self.table.setItem(row_idx, 0, QTableWidgetItem(row_val))

            # Data cells
            for col_idx, col_val in enumerate(col_values):
                value = row_data.get(col_val, 0)
                item = QTableWidgetItem(f"{value:.2f}")
                self.table.setItem(row_idx, col_idx + 1, item)