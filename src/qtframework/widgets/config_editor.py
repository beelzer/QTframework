"""Generic configuration editor widget.

This module provides a reusable widget for editing configuration values
with automatic UI generation based on config schema.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from qtframework.widgets.buttons import Button, ButtonVariant


if TYPE_CHECKING:
    from collections.abc import Callable

    from qtframework.config import ConfigManager


class ConfigFieldDescriptor:
    """Describes a configuration field for automatic UI generation.

    Attributes:
        key: Config key (dot-notation like "ui.theme")
        label: Human-readable label for the field
        field_type: Type of field ("string", "int", "float", "bool", "choice")
        default: Default value
        min_value: Minimum value (for int/float)
        max_value: Maximum value (for int/float)
        choices: List of choices (for choice type)
        choices_callback: Callable that returns list of choices dynamically
        on_change: Optional callback when value changes
        group: Optional group name to organize fields
    """

    def __init__(  # noqa: PLR0917
        self,
        key: str,
        label: str,
        field_type: str = "string",
        default: Any = None,
        min_value: float | None = None,
        max_value: float | None = None,
        choices: list[str] | None = None,
        choices_callback: Callable[[], list[str]] | None = None,
        on_change: Callable[[Any], None] | None = None,
        group: str | None = None,
    ):
        """Initialize field descriptor.

        Args:
            key: Config key in dot notation
            label: Display label
            field_type: Type of field widget to create
            default: Default value if config key doesn't exist
            min_value: Minimum value for numeric fields
            max_value: Maximum value for numeric fields
            choices: Static list of choices for choice fields
            choices_callback: Dynamic callback for choices
            on_change: Callback when field value changes
            group: Group name for organizing fields
        """
        self.key = key
        self.label = label
        self.field_type = field_type
        self.default = default
        self.min_value = min_value
        self.max_value = max_value
        self.choices = choices
        self.choices_callback = choices_callback
        self.on_change = on_change
        self.group = group


class ConfigEditorWidget(QWidget):
    """Generic configuration editor widget.

    This widget automatically generates a form-based UI for editing
    configuration values based on field descriptors.

    Signals:
        config_changed: Emitted when configuration is modified
        config_loaded: Emitted when configuration is loaded from file
        config_saved: Emitted when configuration is saved to file
    """

    config_changed = Signal()
    config_loaded = Signal(str)  # file_path
    config_saved = Signal(str)  # file_path

    def __init__(
        self,
        config_manager: ConfigManager,
        fields: list[ConfigFieldDescriptor],
        show_json_view: bool = True,
        show_file_buttons: bool = True,
        parent: QWidget | None = None,
    ):
        """Initialize the config editor widget.

        Args:
            config_manager: ConfigManager instance to edit
            fields: List of field descriptors defining the UI
            show_json_view: Whether to show JSON view of config
            show_file_buttons: Whether to show load/save buttons
            parent: Parent widget
        """
        super().__init__(parent)
        self.config_manager = config_manager
        self.fields = fields
        self.show_json_view = show_json_view
        self.show_file_buttons = show_file_buttons

        # Store widget references by config key
        self._field_widgets: dict[str, QWidget] = {}

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Create form sections grouped by category
        groups = self._organize_fields_by_group()

        for group_name, group_fields in groups.items():
            group_widget = self._create_group_widget(group_name, group_fields)
            layout.addWidget(group_widget)

        # Button layout
        btn_layout = QHBoxLayout()

        # Apply button (removed refresh button - auto-updates now)
        apply_btn = Button("Apply Changes", variant=ButtonVariant.PRIMARY)
        apply_btn.clicked.connect(self.apply_changes)
        btn_layout.addWidget(apply_btn)

        btn_layout.addStretch()

        if self.show_file_buttons:
            # Load button
            load_btn = Button("Load from File...", variant=ButtonVariant.SECONDARY)
            load_btn.clicked.connect(self._load_config)
            btn_layout.addWidget(load_btn)

            # Save button
            save_btn = Button("Save to File...", variant=ButtonVariant.SECONDARY)
            save_btn.clicked.connect(self._save_config)
            btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # JSON view (optional)
        if self.show_json_view:
            json_view = self._create_json_view()
            layout.addWidget(json_view)

    def _organize_fields_by_group(self) -> dict[str, list[ConfigFieldDescriptor]]:
        """Organize fields by their group attribute."""
        groups: dict[str, list[ConfigFieldDescriptor]] = {}

        for field in self.fields:
            group_name = field.group or "Configuration"
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(field)

        return groups

    def _create_group_widget(
        self, group_name: str, group_fields: list[ConfigFieldDescriptor]
    ) -> QWidget:
        """Create a grouped section of form fields."""
        group_box = QGroupBox(group_name)
        form_layout = QFormLayout(group_box)

        for field in group_fields:
            widget = self._create_field_widget(field)
            self._field_widgets[field.key] = widget
            form_layout.addRow(f"{field.label}:", widget)

        return group_box

    def _create_field_widget(self, field: ConfigFieldDescriptor) -> QWidget:
        """Create appropriate widget for a field based on its type."""
        current_value = self.config_manager.get(field.key, field.default)

        if field.field_type == "string":
            widget = QLineEdit()
            widget.setText(str(current_value or ""))
            return widget

        if field.field_type == "int":
            int_widget = QSpinBox()
            if field.min_value is not None:
                int_widget.setMinimum(int(field.min_value))
            if field.max_value is not None:
                int_widget.setMaximum(int(field.max_value))
            int_widget.setValue(int(current_value or field.default or 0))
            return int_widget

        if field.field_type == "float":
            float_widget = QDoubleSpinBox()
            if field.min_value is not None:
                float_widget.setMinimum(float(field.min_value))
            if field.max_value is not None:
                float_widget.setMaximum(float(field.max_value))
            float_widget.setValue(float(current_value or field.default or 0.0))
            return float_widget

        if field.field_type == "bool":
            bool_widget = QCheckBox()
            bool_widget.setChecked(bool(current_value or field.default or False))
            return bool_widget

        if field.field_type == "choice":
            choice_widget = QComboBox()
            # Get choices from callback or static list
            choices = field.choices_callback() if field.choices_callback else field.choices or []
            choice_widget.addItems(choices)
            if current_value and current_value in choices:
                choice_widget.setCurrentText(str(current_value))
            return choice_widget

        # Fallback to string input
        fallback_widget = QLineEdit()
        fallback_widget.setText(str(current_value or ""))
        return fallback_widget

    def _create_json_view(self) -> QWidget:
        """Create config view section."""
        group = QGroupBox("Current Configuration")
        layout = QVBoxLayout(group)

        self.json_display = QTextEdit()
        self.json_display.setReadOnly(True)
        self.json_display.setMaximumHeight(200)
        self._update_config_display()
        layout.addWidget(self.json_display)

        return group

    def showEvent(self, event):
        """Auto-refresh values when widget becomes visible."""
        super().showEvent(event)
        self.refresh_values()

    def refresh_values(self) -> None:
        """Refresh all field values from current config."""
        for field in self.fields:
            widget = self._field_widgets.get(field.key)
            if not widget:
                continue

            current_value = self.config_manager.get(field.key, field.default)

            if isinstance(widget, QLineEdit):
                widget.setText(str(current_value or ""))
            elif isinstance(widget, QSpinBox):
                widget.setValue(int(current_value or field.default or 0))
            elif isinstance(widget, QDoubleSpinBox):
                widget.setValue(float(current_value or field.default or 0.0))
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(current_value or field.default or False))
            elif isinstance(widget, QComboBox):
                # Refresh choices if dynamic
                if field.choices_callback:
                    choices = field.choices_callback()
                    widget.clear()
                    widget.addItems(choices)
                if current_value:
                    widget.setCurrentText(str(current_value))

        if self.show_json_view:
            self._update_config_display()

    def apply_changes(self) -> None:
        """Apply changes from widgets to config manager."""
        try:
            changes_made = []

            for field in self.fields:
                widget = self._field_widgets.get(field.key)
                if not widget:
                    continue

                old_value = self.config_manager.get(field.key, field.default)
                new_value: Any = None

                if isinstance(widget, QLineEdit):
                    new_value = widget.text()
                elif isinstance(widget, QSpinBox | QDoubleSpinBox):
                    new_value = widget.value()
                elif isinstance(widget, QCheckBox):
                    new_value = widget.isChecked()
                elif isinstance(widget, QComboBox):
                    new_value = widget.currentText()

                # Only update if value changed
                if new_value != old_value:
                    self.config_manager.set(field.key, new_value)
                    changes_made.append(field.label)

                    # Call field-specific change handler
                    if field.on_change:
                        field.on_change(new_value)

            if self.show_json_view:
                self._update_config_display()

            if changes_made:
                self.status_label.setText(f"✓ Configuration updated: {', '.join(changes_made)}")
                self.config_changed.emit()
            else:
                self.status_label.setText("No changes to apply")

        except Exception as e:
            self.status_label.setText(f"✗ Error updating config: {e}")

    def _update_config_display(self) -> None:
        """Update the config display (try YAML, fall back to JSON)."""
        if hasattr(self, "json_display"):
            try:
                # Try to format as YAML for readability
                import yaml

                config_data = yaml.dump(
                    self.config_manager.get_all(),
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )
            except ImportError:
                # Fall back to JSON if YAML not available
                config_data = json.dumps(self.config_manager.get_all(), indent=2)

            self.json_display.setPlainText(config_data)

    def _load_config(self) -> None:
        """Load config from file."""
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Configuration",
            "",
            "Config Files (*.json *.yaml *.yml *.ini *.env);;"
            "JSON Files (*.json);;"
            "YAML Files (*.yaml *.yml);;"
            "INI Files (*.ini);;"
            "ENV Files (*.env);;"
            "All Files (*.*)",
        )

        if file_path:
            file_path_obj = Path(file_path)
            try:
                if self.config_manager.load_file(file_path_obj):
                    self.status_label.setText(f"✓ Config loaded from: {file_path}")
                    self.refresh_values()
                    self.config_loaded.emit(file_path)
                else:
                    self.status_label.setText("✗ Failed to load config")
            except Exception as e:
                self.status_label.setText(f"✗ Error loading config: {e}")
        else:
            self.status_label.setText("Load cancelled")

    def _save_config(self) -> None:
        """Save config to file."""
        import tempfile

        from PySide6.QtWidgets import QFileDialog

        default_path = Path(tempfile.gettempdir()) / "config.json"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration",
            str(default_path),
            "JSON Files (*.json);;"
            "YAML Files (*.yaml *.yml);;"
            "INI Files (*.ini);;"
            "ENV Files (*.env);;"
            "All Files (*.*)",
        )

        if file_path:
            file_path_obj = Path(file_path)
            if self.config_manager.save(file_path_obj):
                self.status_label.setText(f"✓ Config saved to: {file_path}")
                self.config_saved.emit(file_path)
            else:
                self.status_label.setText("✗ Failed to save config")
        else:
            self.status_label.setText("Save cancelled")

    def add_field(self, field: ConfigFieldDescriptor) -> None:
        """Add a new field to the editor dynamically.

        Note: This requires rebuilding the UI. For best performance,
        define all fields upfront in the constructor.

        Args:
            field: Field descriptor to add
        """
        self.fields.append(field)
        # TODO: Implement dynamic field addition without full rebuild

    def get_value(self, key: str) -> Any:
        """Get current value from widget (not yet applied to config).

        Args:
            key: Config key

        Returns:
            Current widget value or None if key not found
        """
        widget = self._field_widgets.get(key)
        if not widget:
            return None

        if isinstance(widget, QLineEdit):
            return widget.text()
        if isinstance(widget, QSpinBox | QDoubleSpinBox):
            return widget.value()
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        if isinstance(widget, QComboBox):
            return widget.currentText()

        return None

    def set_value(self, key: str, value: Any) -> None:
        """Set widget value directly (does not update config until apply_changes).

        Args:
            key: Config key
            value: Value to set
        """
        widget = self._field_widgets.get(key)
        if not widget:
            return

        if isinstance(widget, QLineEdit):
            widget.setText(str(value))
        elif isinstance(widget, QSpinBox):
            widget.setValue(int(value))
        elif isinstance(widget, QDoubleSpinBox):
            widget.setValue(float(value))
        elif isinstance(widget, QCheckBox):
            widget.setChecked(bool(value))
        elif isinstance(widget, QComboBox):
            widget.setCurrentText(str(value))
