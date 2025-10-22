"""Live configuration editor page using generic ConfigEditorWidget."""

from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout

from qtframework.widgets import (
    ConfigEditorWidget,
    ConfigFieldDescriptor,
    ScrollablePage as DemoPage,
)


class ConfigEditorPage(DemoPage):
    """Live configuration editor page."""

    def __init__(self, parent_window=None):
        """Initialize the config editor page.

        Args:
            parent_window: Parent window (ShowcaseWindow) to access app config and theme manager
        """
        super().__init__("Live Configuration Editor")
        self.parent_window = parent_window
        self._init_editor()

    def _init_editor(self):
        """Initialize the configuration editor."""
        # Get config manager from parent
        if self.parent_window and hasattr(self.parent_window, "config_manager"):
            config_manager = self.parent_window.config_manager
        else:
            # Fallback - shouldn't happen in the showcase
            from qtframework.config import ConfigManager

            config_manager = ConfigManager()

        # Listen for theme changes to refresh the editor
        if self.parent_window and hasattr(self.parent_window, "theme_manager"):
            self.parent_window.theme_manager.theme_changed.connect(self._on_external_theme_change)

        # Define fields using the descriptor API
        fields = [
            # App settings group
            ConfigFieldDescriptor(
                key="app.name",
                label="App Name",
                field_type="string",
                default="Qt Framework Showcase",
                group="Application Settings",
            ),
            ConfigFieldDescriptor(
                key="app.version",
                label="App Version",
                field_type="string",
                default="1.0.0",
                group="Application Settings",
            ),
            ConfigFieldDescriptor(
                key="app.debug",
                label="Debug Mode",
                field_type="bool",
                default=False,
                group="Application Settings",
            ),
            # UI settings group
            ConfigFieldDescriptor(
                key="ui.theme",
                label="Theme",
                field_type="choice",
                default="light",
                choices_callback=self._get_available_themes,
                on_change=self._on_theme_changed,
                group="User Interface",
            ),
            ConfigFieldDescriptor(
                key="ui.language",
                label="Language",
                field_type="choice",
                default="en_US",
                choices=["en_US", "es_ES", "fr_FR", "de_DE", "ja_JP"],
                group="User Interface",
            ),
            ConfigFieldDescriptor(
                key="ui.font_scale",
                label="Font Scale (%)",
                field_type="int",
                default=100,
                min_value=50,
                max_value=200,
                on_change=self._on_font_scale_changed,
                group="User Interface",
            ),
            # Performance settings group
            ConfigFieldDescriptor(
                key="performance.cache_size",
                label="Cache Size (MB)",
                field_type="int",
                default=100,
                min_value=0,
                max_value=1000,
                group="Performance",
            ),
            ConfigFieldDescriptor(
                key="performance.max_threads",
                label="Max Threads",
                field_type="int",
                default=4,
                min_value=1,
                max_value=64,
                group="Performance",
            ),
        ]

        # Create the generic config editor widget
        self.editor_widget = ConfigEditorWidget(
            config_manager=config_manager,
            fields=fields,
            show_json_view=True,
            show_file_buttons=True,
        )

        # Add to page layout
        layout = QVBoxLayout()
        layout.addWidget(self.editor_widget)

        # Use a container widget to hold the editor
        from PySide6.QtWidgets import QWidget

        container = QWidget()
        container.setLayout(layout)

        self.add_section("Configuration Editor", container)
        self.add_stretch()

        # Connect signals
        self.editor_widget.config_changed.connect(self._on_config_changed)

    def _get_available_themes(self) -> list[str]:
        """Get list of available themes dynamically."""
        if self.parent_window and hasattr(self.parent_window, "theme_manager"):
            return self.parent_window.theme_manager.list_themes()
        return ["light", "dark", "monokai", "blue", "purple"]

    def _on_theme_changed(self, new_theme: str):
        """Handle theme changes by applying to theme manager."""
        if self.parent_window and hasattr(self.parent_window, "theme_manager"):
            try:
                self.parent_window.theme_manager.set_theme(new_theme)
            except Exception as e:
                print(f"Error applying theme: {e}")

    def _on_font_scale_changed(self, new_scale: int):
        """Handle font scale changes by applying to theme manager."""
        if self.parent_window and hasattr(self.parent_window, "theme_manager"):
            try:
                self.parent_window.theme_manager.set_font_scale(new_scale)
                # Re-apply the current theme to update the stylesheet
                from PySide6.QtWidgets import QApplication

                app = QApplication.instance()
                if app:
                    app.setStyleSheet(self.parent_window.theme_manager.get_stylesheet())
            except Exception as e:
                print(f"Error applying font scale: {e}")

    def _on_external_theme_change(self, theme_name: str):
        """Handle theme changes from external sources (menu bar, etc.)."""
        # Refresh the editor widget to show new theme value
        if hasattr(self, "editor_widget"):
            self.editor_widget.refresh_values()

    def page_shown(self):
        """Called when this page is shown in the content area."""
        # Refresh editor to show latest values
        if hasattr(self, "editor_widget"):
            self.editor_widget.refresh_values()

    def _on_config_changed(self):
        """Handle config changes - save to file."""
        # Save config back to the file
        if self.parent_window and hasattr(self.parent_window, "save_config"):
            self.parent_window.save_config()
