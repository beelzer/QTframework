"""Gettext-based internationalization support for Qt Framework.

Provides comprehensive i18n using standard .po/.mo files:
- Standard Gettext format compatible with Poedit, Lokalize, Weblate
- Qt widget integration
- CLDR-compliant pluralization
- Date/time/number formatting with Babel
"""

from __future__ import annotations

# Core components - Babel-based manager
from qtframework.i18n.babel_manager import (
    BabelI18nManager as I18nManager,
    _,
    get_i18n_manager,
    lazy_gettext,
    pgettext,
    plural,
    set_i18n_manager,
    t,
)

# Context and lazy evaluation
from qtframework.i18n.contexts import (
    LazyPlural,
    LazyString,
    MessageFormatter,
    TranslationContext,
    UIContext,
    lazy,
    lazy_plural,
    translatable_property,
)

# Extraction tools
from qtframework.i18n.extractor import TranslationExtractor, extract_and_update

# Widget integration
from qtframework.i18n.widgets import (
    LanguageSelector,
    TranslatableAction,
    TranslatableButton,
    TranslatableLabel,
    TranslatableMenu,
    TranslatableWidget,
    TranslationHelper,
    setup_widget_translations,
    translatable,
)


__version__ = "3.0.0"

__all__ = [
    # Core
    "I18nManager",
    "LanguageSelector",
    "LazyPlural",
    "LazyString",
    "MessageFormatter",
    "TranslatableAction",
    "TranslatableButton",
    "TranslatableLabel",
    "TranslatableMenu",
    # Widgets
    "TranslatableWidget",
    # Context and lazy
    "TranslationContext",
    # Extraction
    "TranslationExtractor",
    "TranslationHelper",
    "UIContext",
    "_",
    "extract_and_update",
    "get_i18n_manager",
    "lazy",
    "lazy_gettext",
    "lazy_plural",
    "pgettext",
    "plural",
    "set_i18n_manager",
    "setup_widget_translations",
    "t",
    "translatable",
    "translatable_property",
]
