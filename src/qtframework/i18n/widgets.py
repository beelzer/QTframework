"""Qt widget integration for i18n."""

from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QMenu,
    QPushButton,
)

from qtframework.i18n.babel_manager import get_i18n_manager
from qtframework.utils.logger import get_logger


if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtCore import QObject
    from PySide6.QtWidgets import (
        QWidget,
    )


logger = get_logger(__name__)


class TranslatableWidget:
    """Mixin for widgets that support automatic translation updates."""

    def __init__(self) -> None:
        """Initialize the translatable widget."""
        self._translation_key: str | None = None
        self._translation_args: dict[str, Any] = {}
        self._plural_count: int | None = None

    def set_translation_key(self, key: str, **kwargs) -> None:
        """Set the translation key for this widget.

        Args:
            key: Translation key
            **kwargs: Variables for string interpolation
        """
        self._translation_key = key
        self._translation_args = kwargs
        self._update_translation()

        # Connect to translation reload signal
        manager = get_i18n_manager()
        if manager:
            manager.translations_reloaded.connect(self._update_translation)
            manager.locale_changed.connect(self._on_locale_changed)

    def set_plural_translation(self, singular: str, plural: str, count: int, **kwargs) -> None:
        """Set plural translation for this widget.

        Args:
            singular: Singular form (msgid)
            plural: Plural form (msgid_plural)
            count: Count for pluralization
            **kwargs: Additional variables
        """
        self._translation_key = singular
        self._plural_form = plural
        self._plural_count = count
        # Ensure count is in kwargs for formatting
        if "count" not in kwargs:
            kwargs["count"] = count
        self._translation_args = kwargs
        self._update_translation()

        # Connect to translation reload signal
        manager = get_i18n_manager()
        if manager:
            manager.translations_reloaded.connect(self._update_translation)
            manager.locale_changed.connect(self._on_locale_changed)

    def _update_translation(self) -> None:
        """Update the widget's text with current translation."""
        if not self._translation_key:
            return

        manager = get_i18n_manager()
        if not manager:
            return

        if self._plural_count is not None and hasattr(self, "_plural_form"):
            # Ensure count is in args for formatting
            args = dict(self._translation_args)
            if "count" not in args:
                args["count"] = self._plural_count
            text = manager.plural(
                self._translation_key, self._plural_form, self._plural_count, **args
            )
        else:
            text = manager.t(self._translation_key, **self._translation_args)

        # Update widget text
        if isinstance(self, QLabel | QPushButton | QAction) or hasattr(self, "setText"):
            self.setText(text)
        elif hasattr(self, "setTitle"):
            self.setTitle(text)

    def _on_locale_changed(self, locale: str) -> None:
        """Handle locale change."""
        self._update_translation()


class TranslatableLabel(QLabel, TranslatableWidget):
    """QLabel with automatic translation support."""

    def __init__(
        self, translation_key: str | None = None, parent: QWidget | None = None, **kwargs
    ) -> None:
        """Initialize translatable label.

        Args:
            translation_key: Optional translation key
            parent: Parent widget
            **kwargs: Translation variables
        """
        QLabel.__init__(self, parent)
        TranslatableWidget.__init__(self)

        if translation_key:
            self.set_translation_key(translation_key, **kwargs)


class TranslatableButton(QPushButton, TranslatableWidget):
    """QPushButton with automatic translation support."""

    def __init__(
        self, translation_key: str | None = None, parent: QWidget | None = None, **kwargs
    ) -> None:
        """Initialize translatable button.

        Args:
            translation_key: Optional translation key
            parent: Parent widget
            **kwargs: Translation variables
        """
        QPushButton.__init__(self, parent)
        TranslatableWidget.__init__(self)

        if translation_key:
            self.set_translation_key(translation_key, **kwargs)


class TranslatableAction(QAction, TranslatableWidget):
    """QAction with automatic translation support."""

    def __init__(
        self, translation_key: str | None = None, parent: QObject | None = None, **kwargs
    ) -> None:
        """Initialize translatable action.

        Args:
            translation_key: Optional translation key
            parent: Parent object
            **kwargs: Translation variables
        """
        QAction.__init__(self, parent)
        TranslatableWidget.__init__(self)

        if translation_key:
            self.set_translation_key(translation_key, **kwargs)


class TranslatableMenu(QMenu, TranslatableWidget):
    """QMenu with automatic translation support."""

    def __init__(
        self, translation_key: str | None = None, parent: QWidget | None = None, **kwargs
    ) -> None:
        """Initialize translatable menu.

        Args:
            translation_key: Optional translation key
            parent: Parent widget
            **kwargs: Translation variables
        """
        QMenu.__init__(self, parent)
        TranslatableWidget.__init__(self)

        if translation_key:
            self.set_translation_key(translation_key, **kwargs)


class LanguageSelector(QComboBox):
    """Combo box for selecting application language."""

    language_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize language selector."""
        super().__init__(parent)

        self.manager = get_i18n_manager()
        if not self.manager:
            logger.warning("No i18n manager available")
            return

        # Populate languages
        self._populate_languages()

        # Set current selection
        current_locale = self.manager.get_current_locale()
        index = self.findData(current_locale)
        if index >= 0:
            self.setCurrentIndex(index)

        # Connect change signal
        self.currentIndexChanged.connect(self._on_selection_changed)

        # Update on locale changes
        self.manager.locale_changed.connect(self._on_locale_changed)

    def _populate_languages(self) -> None:
        """Populate the combo box with available languages."""
        self.clear()

        if not self.manager:
            return

        locale_info = self.manager.get_locale_info()
        # Sort by display name
        sorted_locales = sorted(locale_info.items(), key=lambda x: x[1]["display_name"])

        for locale_code, info in sorted_locales:
            display_name = info["display_name"]
            self.addItem(display_name, locale_code)

    def _on_selection_changed(self, index: int) -> None:
        """Handle language selection change."""
        if index < 0 or not self.manager:
            return

        locale = self.itemData(index)
        if locale:
            self.manager.set_locale(locale)
            self.language_changed.emit(locale)

    def _on_locale_changed(self, locale: str) -> None:
        """Handle external locale change."""
        index = self.findData(locale)
        if index >= 0 and index != self.currentIndex():
            self.setCurrentIndex(index)


def translatable(translation_key: str | None = None, **default_args):
    """Decorator to make a method automatically translatable.

    Args:
        translation_key: Translation key to use
        **default_args: Default translation arguments

    Returns:
        Decorated method
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Get translation
            manager = get_i18n_manager()
            if manager and translation_key:
                # Merge default args with provided args
                trans_args = {**default_args, **kwargs}
                text = manager.t(translation_key, **trans_args)

                # If the method returns a string, replace it
                result = func(self, *args, **kwargs)
                if isinstance(result, str):
                    return text
                return result

            return func(self, *args, **kwargs)

        return wrapper

    return decorator


class TranslationHelper:
    """Helper class for managing translations in complex widgets."""

    def __init__(self, widget: QWidget) -> None:
        """Initialize translation helper.

        Args:
            widget: Widget to manage translations for
        """
        self.widget = widget
        self.translations: dict[int, dict[str, Any]] = {}
        self.manager = get_i18n_manager()

        if self.manager:
            self.manager.translations_reloaded.connect(self._update_all)
            self.manager.locale_changed.connect(lambda _: self._update_all())

    def register(self, element: Any, key: str, setter: str = "setText", **kwargs) -> None:
        """Register an element for automatic translation.

        Args:
            element: UI element to translate
            key: Translation key
            setter: Method name to set text (default: "setText")
            **kwargs: Translation arguments
        """
        element_id = id(element)
        self.translations[element_id] = {
            "element": element,
            "key": key,
            "setter": setter,
            "args": kwargs,
        }

        # Apply initial translation
        self._update_element(element_id)

    def register_plural(
        self, element: Any, key: str, count: int, setter: str = "setText", **kwargs
    ) -> None:
        """Register an element for plural translation.

        Args:
            element: UI element to translate
            key: Translation key
            count: Count for pluralization
            setter: Method name to set text
            **kwargs: Additional arguments
        """
        element_id = id(element)
        self.translations[element_id] = {
            "element": element,
            "key": key,
            "setter": setter,
            "count": count,
            "args": kwargs,
        }

        # Apply initial translation
        self._update_element(element_id)

    def update_count(self, element: Any, count: int) -> None:
        """Update the count for a plural translation.

        Args:
            element: UI element
            count: New count
        """
        element_id = id(element)
        if element_id in self.translations:
            self.translations[element_id]["count"] = count
            self._update_element(element_id)

    def _update_element(self, element_id: int) -> None:
        """Update a single element's translation."""
        if not self.manager or element_id not in self.translations:
            return

        info = self.translations[element_id]
        element = info["element"]

        # Get translation
        if "count" in info:
            text = self.manager.plural(info["key"], info["count"], **info["args"])
        else:
            text = self.manager.t(info["key"], **info["args"])

        # Set text using specified method
        setter = getattr(element, info["setter"], None)
        if setter:
            setter(text)

    def _update_all(self) -> None:
        """Update all registered translations."""
        for element_id in self.translations:
            self._update_element(element_id)

    def clear(self) -> None:
        """Clear all registered translations."""
        self.translations.clear()


def setup_widget_translations(widget: QWidget) -> TranslationHelper:
    """Setup translation helper for a widget.

    Args:
        widget: Widget to setup translations for

    Returns:
        TranslationHelper instance
    """
    helper = TranslationHelper(widget)
    widget._translation_helper = helper
    return helper


__all__ = [
    "LanguageSelector",
    "TranslatableAction",
    "TranslatableButton",
    "TranslatableLabel",
    "TranslatableMenu",
    "TranslatableWidget",
    "TranslationHelper",
    "setup_widget_translations",
    "translatable",
]
