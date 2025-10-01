"""Configuration management demonstration page."""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from qtframework.config import ConfigFileLoader, ConfigManager, ConfigMigrator, ConfigValidator
from qtframework.widgets.buttons import Button, ButtonVariant

from .base import DemoPage


class ConfigPage(DemoPage):
    """Demonstrate configuration management features."""

    def __init__(self, parent_window=None):
        """Initialize the config page.

        Args:
            parent_window: Parent window (ShowcaseWindow) to access app config and theme manager
        """
        super().__init__("Configuration Management")
        self.parent_window = parent_window
        self._init_demo()

    def _init_demo(self):
        """Initialize configuration demos."""
        # Use the app's config manager if available, otherwise create demo one
        if self.parent_window and hasattr(self.parent_window, "config_manager"):
            self.config_manager = self.parent_window.config_manager
            # Sync config with actual theme
            self._sync_config_with_theme()
        else:
            # Create standalone config manager for demo
            self.config_manager = ConfigManager()
            self._load_demo_config()

        # Create UI sections (common for both paths)
        self._create_ui()

    def _sync_config_with_theme(self):
        """Sync config theme value with actual active theme."""
        current_theme = self._get_current_theme()
        if current_theme:
            self.config_manager.set("ui.theme", current_theme)

    def _create_ui(self):
        """Create the UI sections."""
        # Add sections
        self.add_section("Config Manager Overview", self._create_manager_demo())
        self.add_section("Modular Components", self._create_components_demo())

        # Add status label at bottom
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.status_label)

        self.add_stretch()

    def _load_demo_config(self):
        """Load demo configuration as fallback when not using parent config."""
        # Get actual current theme for initial config
        initial_theme = self._get_current_theme()

        self.config_manager.load_defaults({
            "$schema_version": "1.0.0",
            "app": {
                "name": "Qt Framework Showcase",
                "version": "1.0.0",
                "debug": False,
            },
            "ui": {
                "theme": initial_theme,
                "language": "en_US",
                "font_size": 12,
            },
            "performance": {
                "cache_size": 100,
                "max_threads": 4,
            },
        })

    def _create_manager_demo(self) -> QWidget:
        """Create config manager demo widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Info label
        info = QLabel(
            "The ConfigManager has been refactored into smaller, focused components:\n"
            "• ConfigFileLoader - Handles file I/O (JSON, YAML, INI, ENV)\n"
            "• ConfigValidator - Validates configuration values\n"
            "• ConfigMigrator - Manages schema versions and migrations"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # Display current config - keep reference for updates
        self.config_display = QTextEdit()
        self.config_display.setReadOnly(True)
        self.config_display.setMaximumHeight(200)
        # Use refresh method to handle YAML formatting
        self._refresh_config_display()
        layout.addWidget(self.config_display)

        # Action buttons
        btn_layout = QHBoxLayout()

        reload_btn = Button("Refresh Display", variant=ButtonVariant.SECONDARY)
        reload_btn.clicked.connect(self._reload_config)
        btn_layout.addWidget(reload_btn)

        load_btn = Button("Load from File...", variant=ButtonVariant.SECONDARY)
        load_btn.clicked.connect(self._load_config)
        btn_layout.addWidget(load_btn)

        save_btn = Button("Save to File...", variant=ButtonVariant.PRIMARY)
        save_btn.clicked.connect(self._save_config)
        btn_layout.addWidget(save_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return widget

    def _create_components_demo(self) -> QWidget:
        """Create demo of modular components."""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # File Loader demo
        loader_group = QGroupBox("ConfigFileLoader")
        loader_layout = QVBoxLayout(loader_group)

        loader_info = QLabel(
            "Handles loading/saving config files:\n"
            "✓ JSON, YAML, INI, ENV formats\n"
            "✓ File security validation\n"
            "✓ 10MB size limit\n"
            "✓ Format auto-detection"
        )
        loader_info.setWordWrap(True)
        loader_layout.addWidget(loader_info)

        test_loader_btn = Button("Test File Loader", variant=ButtonVariant.SECONDARY)
        test_loader_btn.clicked.connect(self._test_file_loader)
        loader_layout.addWidget(test_loader_btn)
        loader_layout.addStretch()

        layout.addWidget(loader_group)

        # Validator demo
        validator_group = QGroupBox("ConfigValidator")
        validator_layout = QVBoxLayout(validator_group)

        validator_info = QLabel(
            "Validates configuration values:\n"
            "✓ Type checking\n"
            "✓ Range validation\n"
            "✓ Choice constraints\n"
            "✓ Nested validation"
        )
        validator_info.setWordWrap(True)
        validator_layout.addWidget(validator_info)

        test_validator_btn = Button("Test Validator", variant=ButtonVariant.SECONDARY)
        test_validator_btn.clicked.connect(self._test_validator)
        validator_layout.addWidget(test_validator_btn)
        validator_layout.addStretch()

        layout.addWidget(validator_group)

        # Migrator demo
        migrator_group = QGroupBox("ConfigMigrator")
        migrator_layout = QVBoxLayout(migrator_group)

        migrator_info = QLabel(
            "Manages schema versions:\n"
            "✓ Version detection\n"
            "✓ Automatic migration\n"
            "✓ Custom handlers\n"
            f"✓ Current: v{self.config_manager.get_schema_version()}"
        )
        migrator_info.setWordWrap(True)
        migrator_layout.addWidget(migrator_info)

        test_migrator_btn = Button("Test Migrator", variant=ButtonVariant.SECONDARY)
        test_migrator_btn.clicked.connect(self._test_migrator)
        migrator_layout.addWidget(test_migrator_btn)
        migrator_layout.addStretch()

        layout.addWidget(migrator_group)

        return widget

    def _get_current_theme(self) -> str:
        """Get the currently active theme from theme manager."""
        if self.parent_window and hasattr(self.parent_window, "theme_manager"):
            current_theme = self.parent_window.theme_manager.get_current_theme()
            if current_theme:
                return current_theme.name
        return self.config_manager.get("ui.theme", "light")

    def _reload_config(self):
        """Reload and display config - just refresh the display from current state."""
        # Don't call config_manager.reload() as there are no files to reload from
        # Just refresh the UI to show current state
        self._refresh_config_display()
        self.status_label.setText("✓ Display refreshed")

    def _refresh_config_display(self):
        """Refresh the config display in the manager demo section."""
        if hasattr(self, "config_display"):
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

            self.config_display.setPlainText(config_data)

    def _load_config(self):
        """Load config from file."""
        from PySide6.QtWidgets import QFileDialog

        # Ask user which file to load
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
            file_path = Path(file_path)
            try:
                if self.config_manager.load_file(file_path):
                    self.status_label.setText(f"✓ Config loaded from: {file_path}")
                    # Refresh display
                    self._refresh_config_display()
                else:
                    self.status_label.setText("✗ Failed to load config")
            except Exception as e:
                self.status_label.setText(f"✗ Error loading config: {e}")
        else:
            self.status_label.setText("Load cancelled")

    def _save_config(self):
        """Save config to file."""
        from PySide6.QtWidgets import QFileDialog
        import tempfile

        # Suggest a default location
        default_path = Path(tempfile.gettempdir()) / "qtframework_showcase_config.json"

        # Ask user where to save
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
            file_path = Path(file_path)
            if self.config_manager.save(file_path):
                self.status_label.setText(f"✓ Config saved to: {file_path}")
            else:
                self.status_label.setText("✗ Failed to save config")
        else:
            self.status_label.setText("Save cancelled")

    def _test_file_loader(self):
        """Test the ConfigFileLoader component."""
        loader = ConfigFileLoader()

        # Create temp file
        import tempfile

        temp_file = Path(tempfile.gettempdir()) / "test_config.json"
        test_data = {"test": "data", "value": 123}

        # Test save
        if loader.save(temp_file, test_data, "json"):
            # Test load
            loaded = loader.load(temp_file, "json")
            if loaded == test_data:
                self.status_label.setText(f"✓ FileLoader test passed: {temp_file}")
            else:
                self.status_label.setText("✗ FileLoader load mismatch")
        else:
            self.status_label.setText("✗ FileLoader save failed")

    def _test_validator(self):
        """Test the ConfigValidator component."""
        validator = self.config_manager.validator

        try:
            # Test valid data
            valid_data = {"ui": {"theme": "dark", "font_size": 14}}
            validator.validate(valid_data, "test")

            # Test invalid data (should raise)
            invalid_data = {
                "ui": {"font_size": 999}  # Out of range
            }
            try:
                validator.validate(invalid_data, "test")
                self.status_label.setText("✗ Validator should have caught invalid value")
            except Exception:
                self.status_label.setText("✓ Validator correctly caught invalid value")

        except Exception as e:
            self.status_label.setText(f"✗ Validator test failed: {e}")

    def _test_migrator(self):
        """Test the ConfigMigrator component."""
        migrator = self.config_manager.migrator

        # Test old version migration
        old_config = {
            "$schema_version": "0.9.0",
            "ui": {"colour": "dark"},  # Old key name
        }

        migrated = migrator.validate_and_migrate(old_config, "test")

        # Check migration happened
        if migrated.get("$schema_version") == "1.0.0" and "theme" in migrated.get("ui", {}):
            versions = migrator.get_supported_versions()
            self.status_label.setText(
                f"✓ Migrator test passed. Supported versions: {', '.join(versions)}"
            )
        else:
            self.status_label.setText("✗ Migration did not complete as expected")
