"""Advanced tab widgets for the framework."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QSlider,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from qtframework.widgets.base import Widget


class TabWidget(Widget):
    """Enhanced tab widget with framework integration."""

    tab_changed = Signal(int)
    tab_close_requested = Signal(int)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        closeable_tabs: bool = False,
        moveable_tabs: bool = True,
    ) -> None:
        """Initialize tab widget.

        Args:
            parent: Parent widget
            closeable_tabs: Whether tabs can be closed
            moveable_tabs: Whether tabs can be moved/reordered
        """
        super().__init__(parent)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self._tab_widget = QTabWidget()

        if closeable_tabs:
            self._tab_widget.setTabsClosable(True)
            self._tab_widget.tabCloseRequested.connect(self.tab_close_requested.emit)

        if moveable_tabs:
            self._tab_widget.setMovable(True)

        self._tab_widget.currentChanged.connect(self.tab_changed.emit)

        layout.addWidget(self._tab_widget)

        # Store tab metadata
        self._tab_data: dict[int, dict[str, Any]] = {}

    def add_tab(
        self,
        widget: QWidget,
        title: str,
        *,
        icon: Any = None,
        closeable: bool | None = None,
        data: dict[str, Any] | None = None,
    ) -> int:
        """Add a tab to the widget.

        Args:
            widget: The widget to add as a tab
            title: Tab title
            icon: Optional tab icon
            closeable: Whether this specific tab is closeable (overrides global setting)
            data: Optional metadata for the tab

        Returns:
            Index of the added tab
        """
        if icon:
            index = self._tab_widget.addTab(widget, icon, title)
        else:
            index = self._tab_widget.addTab(widget, title)

        # Store tab data
        self._tab_data[index] = data or {}

        # Set tab-specific closeable state if provided
        if closeable is not None:
            self._tab_widget.tabBar().setTabButton(
                index,
                self._tab_widget.tabBar().RightSide
                if closeable
                else self._tab_widget.tabBar().LeftSide,
                None,
            )

        return index

    def insert_tab(
        self,
        index: int,
        widget: QWidget,
        title: str,
        *,
        icon: Any = None,
        data: dict[str, Any] | None = None,
    ) -> int:
        """Insert a tab at the specified index.

        Args:
            index: Position to insert the tab
            widget: The widget to add as a tab
            title: Tab title
            icon: Optional tab icon
            data: Optional metadata for the tab

        Returns:
            Index of the inserted tab
        """
        if icon:
            actual_index = self._tab_widget.insertTab(index, widget, icon, title)
        else:
            actual_index = self._tab_widget.insertTab(index, widget, title)

        # Update tab data indices and store new data
        new_tab_data = {}
        for i, tab_data in self._tab_data.items():
            if i >= index:
                new_tab_data[i + 1] = tab_data
            else:
                new_tab_data[i] = tab_data

        new_tab_data[actual_index] = data or {}
        self._tab_data = new_tab_data

        return actual_index

    def remove_tab(self, index: int) -> None:
        """Remove tab at the specified index.

        Args:
            index: Index of tab to remove
        """
        self._tab_widget.removeTab(index)

        # Update tab data indices
        if index in self._tab_data:
            del self._tab_data[index]

        new_tab_data = {}
        for i, tab_data in self._tab_data.items():
            if i > index:
                new_tab_data[i - 1] = tab_data
            else:
                new_tab_data[i] = tab_data
        self._tab_data = new_tab_data

    def set_tab_title(self, index: int, title: str) -> None:
        """Set the title of a tab.

        Args:
            index: Tab index
            title: New title
        """
        self._tab_widget.setTabText(index, title)

    def get_tab_title(self, index: int) -> str:
        """Get the title of a tab.

        Args:
            index: Tab index

        Returns:
            Tab title
        """
        return self._tab_widget.tabText(index)

    def set_tab_enabled(self, index: int, enabled: bool) -> None:
        """Enable or disable a tab.

        Args:
            index: Tab index
            enabled: Whether the tab should be enabled
        """
        self._tab_widget.setTabEnabled(index, enabled)

    def is_tab_enabled(self, index: int) -> bool:
        """Check if a tab is enabled.

        Args:
            index: Tab index

        Returns:
            True if tab is enabled
        """
        return self._tab_widget.isTabEnabled(index)

    def set_current_index(self, index: int) -> None:
        """Set the current tab by index.

        Args:
            index: Tab index to make current
        """
        self._tab_widget.setCurrentIndex(index)

    def current_index(self) -> int:
        """Get the current tab index.

        Returns:
            Current tab index
        """
        return self._tab_widget.currentIndex()

    def current_widget(self) -> QWidget | None:
        """Get the current tab widget.

        Returns:
            Current tab widget or None
        """
        return self._tab_widget.currentWidget()

    def widget(self, index: int) -> QWidget | None:
        """Get the widget at the specified tab index.

        Args:
            index: Tab index

        Returns:
            Tab widget or None
        """
        return self._tab_widget.widget(index)

    def count(self) -> int:
        """Get the number of tabs.

        Returns:
            Number of tabs
        """
        return self._tab_widget.count()

    def get_tab_data(self, index: int) -> dict[str, Any]:
        """Get metadata for a tab.

        Args:
            index: Tab index

        Returns:
            Tab metadata dictionary
        """
        return self._tab_data.get(index, {})

    def set_tab_data(self, index: int, data: dict[str, Any]) -> None:
        """Set metadata for a tab.

        Args:
            index: Tab index
            data: Metadata dictionary
        """
        self._tab_data[index] = data

    def set_tab_position(self, position: str) -> None:
        """Set the position of tab bar.

        Args:
            position: One of 'north', 'south', 'west', 'east'
        """
        position_map = {
            "north": QTabWidget.TabPosition.North,
            "south": QTabWidget.TabPosition.South,
            "west": QTabWidget.TabPosition.West,
            "east": QTabWidget.TabPosition.East,
        }

        if position in position_map:
            self._tab_widget.setTabPosition(position_map[position])

    def clear(self) -> None:
        """Remove all tabs."""
        self._tab_widget.clear()
        self._tab_data.clear()


class BaseTabPage(Widget):
    """Base class for tab page widgets."""

    value_changed = Signal(str, object)  # key, value

    def __init__(
        self,
        data: dict[str, Any] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize tab page.

        Args:
            data: Data for this tab page
            parent: Parent widget
        """
        super().__init__(parent)

        self._data = data or {}
        self._controls: dict[str, QWidget] = {}

        # Main layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 20, 20, 20)
        self._layout.setSpacing(15)

        self._setup_ui()
        self._connect_signals()
        self._load_values()

    def _setup_ui(self) -> None:
        """Setup the UI. Override in subclasses."""

    def _connect_signals(self) -> None:
        """Connect control signals. Override in subclasses."""

    def _load_values(self) -> None:
        """Load values from data into controls."""
        for key, control in self._controls.items():
            if key in self._data:
                self._set_control_value(control, self._data[key])

    def _set_control_value(self, control: QWidget, value: Any) -> None:
        """Set value of a control widget."""
        if isinstance(control, QLineEdit):
            control.setText(str(value))
        elif isinstance(control, (QSpinBox, QDoubleSpinBox)):
            control.setValue(value)
        elif isinstance(control, QCheckBox):
            control.setChecked(bool(value))
        elif isinstance(control, QComboBox):
            index = control.findText(str(value))
            if index >= 0:
                control.setCurrentIndex(index)
        elif isinstance(control, QSlider):
            control.setValue(int(value))

    def _get_control_value(self, control: QWidget) -> Any:
        """Get value from a control widget."""
        if isinstance(control, QLineEdit):
            return control.text()
        if isinstance(control, QSpinBox) or isinstance(control, QDoubleSpinBox):
            return control.value()
        if isinstance(control, QCheckBox):
            return control.isChecked()
        if isinstance(control, QComboBox):
            return control.currentText()
        if isinstance(control, QSlider):
            return control.value()
        return None

    def get_values(self) -> dict[str, Any]:
        """Get all values from the tab controls."""
        values = {}
        for key, control in self._controls.items():
            values[key] = self._get_control_value(control)
        return values

    def update_data(self, data: dict[str, Any]) -> None:
        """Update data and refresh controls."""
        self._data = data
        self._load_values()

    def _create_group(self, title: str) -> QGroupBox:
        """Create a group box with title."""
        group = QGroupBox(title)
        group.setLayout(QFormLayout())
        return group

    def _add_control_to_group(
        self,
        group: QGroupBox,
        label: str,
        control: QWidget,
        key: str,
    ) -> None:
        """Add a control to a group with proper labeling."""
        self._controls[key] = control
        group.layout().addRow(label, control)

    def _create_slider_with_label(
        self,
        min_val: int,
        max_val: int,
        current_val: int,
        suffix: str = "",
    ) -> tuple[QSlider, QLabel]:
        """Create a slider with value label."""
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(current_val)

        label = QLabel(f"{current_val}{suffix}")
        slider.valueChanged.connect(lambda v: label.setText(f"{v}{suffix}"))

        return slider, label
