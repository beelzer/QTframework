"""Internationalization (i18n) demo page."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from qtframework.i18n import (
    LanguageSelector,
    TranslatableButton,
    TranslatableLabel,
    get_i18n_manager,
    setup_widget_translations,
    t,
)
from qtframework.widgets import Badge, CountBadge

from qtframework.widgets import ScrollablePage as DemoPage


class I18nPage(DemoPage):
    """Demo page for i18n features."""

    def __init__(self):
        """Initialize the i18n demo page."""
        super().__init__(title="Internationalization (i18n)", scrollable=True)
        self.setObjectName("i18nPage")
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI content."""
        # Add description
        desc = QLabel(
            "Comprehensive localization support with hot-reload, pluralization, and formatting"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("QLabel { color: #666; margin-bottom: 10px; }")
        self.content_layout.addWidget(desc)

        # Language selector
        self.content_layout.addWidget(self._create_language_selector())

        # Basic translations
        self.content_layout.addWidget(self._create_basic_translations())

        # Dynamic translations
        self.content_layout.addWidget(self._create_dynamic_translations())

        # Pluralization
        self.content_layout.addWidget(self._create_pluralization())

        # Date and number formatting
        self.content_layout.addWidget(self._create_formatting())

        # Translatable widgets
        self.content_layout.addWidget(self._create_translatable_widgets())

        self.content_layout.addStretch()

        # Connect signals after UI is created
        self._connect_signals()

    def _create_language_selector(self) -> QGroupBox:
        """Create language selector section."""
        group = QGroupBox("Language Selection")
        layout = QFormLayout()

        # Language selector widget
        self.language_selector = LanguageSelector()
        layout.addRow("Select Language:", self.language_selector)

        # Current locale info
        self.locale_info = QLabel()
        self._update_locale_info()
        layout.addRow("Current Locale:", self.locale_info)

        # Available locales
        manager = get_i18n_manager()
        if manager:
            locales = ", ".join(manager.get_available_locales())
            layout.addRow("Available:", QLabel(locales))

        group.setLayout(layout)
        return group

    def _create_basic_translations(self) -> QGroupBox:
        """Create basic translation examples."""
        group = QGroupBox("Basic Translations")
        layout = QVBoxLayout()

        # Setup translation helper
        self.helper = setup_widget_translations(group)

        # Common UI strings - using English text as msgid
        common_layout = QHBoxLayout()
        for msgid in ["OK", "Cancel", "Save", "Delete"]:
            label = QLabel()
            self.helper.register(label, msgid)
            common_layout.addWidget(label)
        layout.addLayout(common_layout)

        # Menu items - using English text as msgid
        menu_layout = QHBoxLayout()
        for msgid in ["File", "Edit", "View", "Help"]:
            label = QLabel()
            self.helper.register(label, msgid)
            menu_layout.addWidget(label)
        layout.addLayout(menu_layout)

        # Status messages - using English text as msgid
        status_layout = QHBoxLayout()
        for msgid in ["Ready", "Loading...", "Connected", "Offline"]:
            badge = Badge()
            self.helper.register(badge, msgid, setter="setText")
            status_layout.addWidget(badge)
        layout.addLayout(status_layout)

        group.setLayout(layout)
        return group

    def _create_dynamic_translations(self) -> QGroupBox:
        """Create dynamic translation examples."""
        group = QGroupBox("Dynamic Translations with Variables")
        layout = QVBoxLayout()

        # Error message with variable
        self.error_label = QLabel()
        self._update_error_message()
        layout.addWidget(self.error_label)

        # About message with app name
        self.about_label = QLabel()
        self._update_about_message()
        layout.addWidget(self.about_label)

        # Update button
        self.update_btn = TranslatableButton("Update Messages")
        self.update_btn.clicked.connect(self._update_dynamic_messages)
        layout.addWidget(self.update_btn)

        group.setLayout(layout)
        return group

    def _create_pluralization(self) -> QGroupBox:
        """Create pluralization examples."""
        group = QGroupBox("Pluralization")
        layout = QVBoxLayout()

        # Item count selector
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Item Count:"))

        self.item_spinner = QSpinBox()
        self.item_spinner.setRange(0, 100)
        self.item_spinner.setValue(1)
        count_layout.addWidget(self.item_spinner)

        layout.addLayout(count_layout)

        # Plural labels
        self.items_label = QLabel()
        self.selected_label = QLabel()
        self.delete_label = QLabel()

        self._update_plural_labels()

        layout.addWidget(self.items_label)
        layout.addWidget(self.selected_label)
        layout.addWidget(self.delete_label)

        # Count badge
        self.count_badge = CountBadge(count=1)
        layout.addWidget(self.count_badge)

        group.setLayout(layout)
        return group

    def _create_formatting(self) -> QGroupBox:
        """Create date and number formatting examples."""
        group = QGroupBox("Locale-Specific Formatting")
        layout = QFormLayout()

        manager = get_i18n_manager()
        if not manager:
            layout.addRow(QLabel("No i18n manager available"))
            group.setLayout(layout)
            return group

        # Current date/time
        now = datetime.now()

        # Date formatting - use "long" format to show full month names
        self.date_label = QLabel(manager.format_date(now, "long"))
        layout.addRow("Date:", self.date_label)

        # DateTime formatting
        self.datetime_label = QLabel(manager.format_datetime(now, "medium"))
        layout.addRow("DateTime:", self.datetime_label)

        # Time formatting
        self.time_label = QLabel(manager.format_time(now))
        layout.addRow("Time:", self.time_label)

        # Number formatting
        self.number_label = QLabel(manager.format_number(1234567.89))
        layout.addRow("Number:", self.number_label)

        # Currency formatting
        self.currency_label = QLabel(manager.format_currency(1234.56, "USD"))
        layout.addRow("Currency:", self.currency_label)

        # Percentage formatting
        self.percent_label = QLabel(manager.format_percent(0.85))
        layout.addRow("Percentage:", self.percent_label)

        group.setLayout(layout)
        return group

    def _create_translatable_widgets(self) -> QGroupBox:
        """Create translatable widget examples."""
        group = QGroupBox("Translatable Widgets")
        layout = QVBoxLayout()

        # Translatable label - using actual text as msgid
        label = TranslatableLabel("Are you sure you want to continue?")
        layout.addWidget(label)

        # Translatable buttons - using actual text as msgid
        button_layout = QHBoxLayout()

        save_btn = TranslatableButton("Save")
        button_layout.addWidget(save_btn)

        cancel_btn = TranslatableButton("Cancel")
        button_layout.addWidget(cancel_btn)

        apply_btn = TranslatableButton("Apply")
        button_layout.addWidget(apply_btn)

        layout.addLayout(button_layout)

        # Buttons with dynamic content
        self.file_btn = TranslatableButton()
        self.file_btn.set_translation_key("File saved successfully")
        layout.addWidget(self.file_btn)

        # Plural button
        self.plural_btn = TranslatableButton()
        self.plural_btn.set_plural_translation("{count} item", "{count} items", 5)
        layout.addWidget(self.plural_btn)

        group.setLayout(layout)
        return group

    def _connect_signals(self):
        """Connect widget signals."""
        # Language change
        self.language_selector.language_changed.connect(self._on_language_changed)

        # Item count change
        self.item_spinner.valueChanged.connect(self._on_item_count_changed)

        # Manager signals
        manager = get_i18n_manager()
        if manager:
            manager.locale_changed.connect(self._on_locale_changed)
            manager.translations_reloaded.connect(self._on_translations_reloaded)

    def _on_language_changed(self, locale: str):
        """Handle language selection change."""
        self._update_locale_info()
        self._update_dynamic_messages()
        self._update_plural_labels()
        self._update_formatting()

    def _on_locale_changed(self, locale: str):
        """Handle locale change from manager."""
        self._update_locale_info()
        self._update_dynamic_messages()
        self._update_plural_labels()
        self._update_formatting()

    def _on_translations_reloaded(self):
        """Handle translations reload."""
        self._update_dynamic_messages()
        self._update_plural_labels()

    def _on_item_count_changed(self, value: int):
        """Handle item count change."""
        self._update_plural_labels()
        self.count_badge.count = value

        # Update plural button
        if hasattr(self, "plural_btn"):
            self.plural_btn.set_plural_translation("{count} item", "{count} items", value)

    def _update_locale_info(self):
        """Update locale information display."""
        manager = get_i18n_manager()
        if manager:
            locale = manager.get_current_locale()
            # Get locale display name from manager's locale info
            locale_info = manager.get_locale_info()
            if locale in locale_info:
                # locale_info[locale] is a dict with 'display_name' key
                display_name = locale_info[locale]["display_name"]
            else:
                display_name = locale
            self.locale_info.setText(f"{locale} ({display_name})")

    def _update_error_message(self):
        """Update error message with variable."""
        self.error_label.setText(t("File not found: {filename}", filename="example.txt"))

    def _update_about_message(self):
        """Update about message with app name."""
        self.about_label.setText(t("About {app_name}", app_name="Qt Framework"))

    def _update_dynamic_messages(self):
        """Update all dynamic messages."""
        self._update_error_message()
        self._update_about_message()

    def _update_plural_labels(self):
        """Update pluralization examples."""
        manager = get_i18n_manager()
        if not manager:
            return

        count = self.item_spinner.value()

        # Update labels using proper plural forms with count parameter
        self.items_label.setText(
            manager.plural("{count} item", "{count} items", count, count=count)
        )
        self.selected_label.setText(
            manager.plural("{count} item selected", "{count} items selected", count, count=count)
        )
        self.delete_label.setText(
            manager.plural(
                "Are you sure you want to delete {count} item?",
                "Are you sure you want to delete {count} items?",
                count,
                count=count,
            )
        )

    def _update_formatting(self):
        """Update formatted values."""
        manager = get_i18n_manager()
        if not manager:
            return

        now = datetime.now()

        # Update all formatted labels - use "long" format for date to show full month name
        self.date_label.setText(manager.format_date(now, "long"))
        self.datetime_label.setText(manager.format_datetime(now, "medium"))
        self.time_label.setText(manager.format_time(now))
        self.number_label.setText(manager.format_number(1234567.89))
        self.currency_label.setText(manager.format_currency(1234.56, "USD"))
        self.percent_label.setText(manager.format_percent(0.85))
