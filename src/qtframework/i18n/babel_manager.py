"""Modern i18n manager using Babel with full gettext support."""

from __future__ import annotations

import threading
from contextlib import contextmanager, suppress
from pathlib import Path
from typing import TYPE_CHECKING

from babel import Locale
from babel.support import LazyProxy
from PySide6.QtCore import QObject, QSettings, Signal

from qtframework.i18n.locale_formatter import LocaleFormatter
from qtframework.i18n.translation_loader import TranslationLoader
from qtframework.utils.logger import get_logger


if TYPE_CHECKING:
    from babel.plural import PluralRule
    from babel.support import Translations

logger = get_logger(__name__)


class BabelI18nManager(QObject):
    """Modern internationalization manager using Babel.

    Features:
    - Full CLDR plural support
    - Translation contexts (pgettext)
    - Lazy translations
    - Multiple domains
    - Locale fallback chains
    - Translation caching
    """

    locale_changed = Signal(str)
    translations_reloaded = Signal()

    def __init__(
        self,
        locale_dir: Path | None = None,
        domain: str = "qtframework",
        default_locale: str = "en_US",
        fallback_locales: list[str] | None = None,
        cache_size: int = 128,
        auto_compile: bool = True,
    ) -> None:
        """Initialize the Babel i18n manager.

        Args:
            locale_dir: Directory containing locale subdirectories
            domain: The gettext domain (base name of .po files)
            default_locale: Default locale to use
            fallback_locales: List of fallback locales in order
            cache_size: Size of translation cache
            auto_compile: Auto-compile .po to .mo in development (default: True)
        """
        super().__init__()

        # Set default locale directory if not provided
        if locale_dir is None:
            locale_dir = Path(__file__).parent / "locale"

        self._current_locale = default_locale
        self._default_locale = default_locale
        self._current_translations: Translations | None = None

        # Delegate to specialized components
        self._translation_loader = TranslationLoader(
            locale_dir=Path(locale_dir),
            domain=domain,
            fallback_locales=fallback_locales or ["en_US", "en"],
            cache_size=cache_size,
            auto_compile=auto_compile,
        )
        self._formatter = LocaleFormatter(locale=default_locale)

        # Locale objects cache
        self._locales: dict[str, Locale] = {}
        self._locales_lock = threading.RLock()

        # Settings persistence
        self._settings = QSettings()
        saved_locale = self._settings.value("i18n/locale")
        if saved_locale and isinstance(saved_locale, str):
            self._current_locale = saved_locale

        # Load initial locale
        self.set_locale(self._current_locale)

    def _get_locale_object(self, locale_code: str) -> Locale:
        """Get or create a Babel Locale object."""
        with self._locales_lock:
            if locale_code not in self._locales:
                self._locales[locale_code] = Locale.parse(locale_code)

            return self._locales[locale_code]

    def set_locale(self, locale: str) -> bool:
        """Set the current locale.

        Args:
            locale: Locale code (e.g., 'en_US', 'es_ES')

        Returns:
            True if locale was set successfully
        """
        translations = self._translation_loader.load_translations(locale)

        if translations:
            self._current_translations = translations
            self._current_locale = locale
            self._formatter.set_locale(locale)

            # Save to settings
            self._settings.setValue("i18n/locale", locale)

            # Clear translation cache when locale changes
            self._translation_loader.clear_cache()

            # Emit signals
            self.locale_changed.emit(locale)
            self.translations_reloaded.emit()

            return True

        return False

    def get_current_locale(self) -> str:
        """Get the current locale code."""
        return self._current_locale

    def get_current_locale_object(self) -> Locale:
        """Get the current Babel Locale object."""
        return self._get_locale_object(self._current_locale)

    @property
    def domain_name(self) -> str:
        """Return the active gettext domain."""
        return self._translation_loader._domain

    def get_available_locales(self) -> list[str]:
        """Get list of available locales."""
        return self._translation_loader.get_available_locales()

    def get_locale_info(self) -> dict[str, dict[str, str]]:
        """Get detailed information about available locales."""
        info = {}

        for locale_code in self.get_available_locales():
            try:
                locale_obj = self._get_locale_object(locale_code)
                info[locale_code] = {
                    "display_name": locale_obj.display_name,
                    "english_name": locale_obj.english_name,
                    "language": locale_obj.language,
                    "territory": locale_obj.territory or "",
                    "script": locale_obj.script or "",
                }
            except (ValueError, AttributeError) as e:
                logger.warning(f"Failed to parse locale {locale_code}: {e}")
                info[locale_code] = {
                    "display_name": locale_code,
                    "english_name": locale_code,
                    "language": locale_code.split("_")[0],
                    "territory": "",
                    "script": "",
                }

        return info

    # Translation methods

    def t(self, msgid: str, **kwargs) -> str:
        """Translate a message.

        Args:
            msgid: Message ID to translate
            **kwargs: Variables for string formatting

        Returns:
            Translated and formatted string
        """
        if self._current_translations:
            translated = self._current_translations.ugettext(msgid)
        else:
            translated = msgid

        if kwargs:
            with suppress(KeyError, ValueError):
                translated = translated.format(**kwargs)

        return translated

    def gettext(self, msgid: str) -> str:
        """Alias for t()."""
        return self.t(msgid)

    def _(self, msgid: str) -> str:
        """Short alias for t()."""
        return self.t(msgid)

    def pgettext(self, context: str, msgid: str, **kwargs) -> str:
        """Translate with context.

        Args:
            context: Translation context
            msgid: Message ID
            **kwargs: Variables for formatting

        Returns:
            Translated string with context consideration
        """
        if self._current_translations:
            # Babel uses \x04 as context separator
            translated = self._current_translations.upgettext(context, msgid)
        else:
            translated = msgid

        if kwargs:
            with suppress(KeyError, ValueError):
                translated = translated.format(**kwargs)

        return translated

    def plural(self, singular: str, plural_form: str, n: int, **kwargs) -> str:
        """Translate plural message with CLDR rules.

        Args:
            singular: Singular form
            plural_form: Plural form
            n: Number for plural selection
            **kwargs: Variables for formatting

        Returns:
            Correctly pluralized translation
        """
        if self._current_translations:
            translated = self._current_translations.ungettext(singular, plural_form, n)
        else:
            # Use simple English rules when no translations
            translated = singular if n == 1 else plural_form

        # Add count to kwargs
        if "count" not in kwargs:
            kwargs["count"] = n
        if "n" not in kwargs:
            kwargs["n"] = n

        with suppress(KeyError, ValueError):
            translated = translated.format(**kwargs)

        return translated

    def ngettext(self, singular: str, plural_form: str, n: int) -> str:
        """Alias for plural()."""
        return self.plural(singular, plural_form, n)

    def npgettext(self, context: str, singular: str, plural_form: str, n: int, **kwargs) -> str:
        """Translate plural with context.

        Args:
            context: Translation context
            singular: Singular form
            plural_form: Plural form
            n: Number for plural selection
            **kwargs: Variables for formatting

        Returns:
            Contextualized plural translation
        """
        if self._current_translations:
            translated = self._current_translations.unpgettext(context, singular, plural_form, n)
        else:
            translated = singular if n == 1 else plural_form

        if "count" not in kwargs:
            kwargs["count"] = n

        with suppress(KeyError, ValueError):
            translated = translated.format(**kwargs)

        return translated

    def lazy_gettext(self, msgid: str) -> LazyProxy:
        """Get lazy translation that evaluates when accessed.

        Args:
            msgid: Message ID

        Returns:
            LazyProxy that translates when converted to string
        """
        return LazyProxy(lambda: self.t(msgid))

    def lazy_pgettext(self, context: str, msgid: str) -> LazyProxy:
        """Lazy translation with context."""
        return LazyProxy(lambda: self.pgettext(context, msgid))

    # Formatting methods using Babel's CLDR data (delegate to formatter)

    def format_number(self, number: float, **kwargs) -> str:
        """Format number according to locale."""
        return self._formatter.format_number(number, **kwargs)

    def format_decimal(self, number: float, **kwargs) -> str:
        """Format decimal according to locale."""
        return self._formatter.format_decimal(number, **kwargs)

    def format_currency(self, number: float, currency: str, **kwargs) -> str:
        """Format currency according to locale."""
        return self._formatter.format_currency(number, currency, **kwargs)

    def format_percent(self, number: float, **kwargs) -> str:
        """Format percentage according to locale."""
        return self._formatter.format_percent(number, **kwargs)

    def format_scientific(self, number: float, **kwargs) -> str:
        """Format number in scientific notation."""
        return self._formatter.format_scientific(number, **kwargs)

    def format_date(self, date, format: str = "medium") -> str:
        """Format date according to locale."""
        return self._formatter.format_date(date, format)

    def format_datetime(self, datetime, format: str = "medium") -> str:
        """Format datetime according to locale."""
        return self._formatter.format_datetime(datetime, format)

    def format_time(self, time, format: str = "medium") -> str:
        """Format time according to locale."""
        return self._formatter.format_time(time, format)

    # Domain support

    @contextmanager
    def domain(self, domain: str):
        """Context manager for temporary domain switch.

        Usage:
            with i18n.domain('emails'):
                subject = i18n.t('welcome_subject')
        """
        old_domain = self._translation_loader._domain
        self._translation_loader._domain = domain
        # Clear cache for new domain
        self._translation_loader.clear_cache()
        self._translation_loader.clear_translations()
        self.set_locale(self._current_locale)

        try:
            yield
        finally:
            self._translation_loader._domain = old_domain
            self._translation_loader.clear_cache()
            self._translation_loader.clear_translations()
            self.set_locale(self._current_locale)

    def get_plural_rule(self) -> PluralRule:
        """Get the plural rule for current locale."""
        locale_obj = self.get_current_locale_object()
        return locale_obj.plural_form

    def get_plural_categories(self) -> list[str]:
        """Get plural categories for current locale (zero, one, two, few, many, other)."""
        rule = self.get_plural_rule()
        return list(rule.tags)


# Global instance management
_manager: BabelI18nManager | None = None


def get_i18n_manager() -> BabelI18nManager:
    """Get the global i18n manager instance."""
    global _manager
    if _manager is None:
        _manager = BabelI18nManager()
    return _manager


def set_i18n_manager(manager: BabelI18nManager) -> None:
    """Set the global i18n manager instance."""
    global _manager
    _manager = manager


# Convenience functions that use the global manager
def t(msgid: str, **kwargs) -> str:
    """Translate using global manager."""
    return get_i18n_manager().t(msgid, **kwargs)


def _(msgid: str) -> str:
    """Short translation alias."""
    return get_i18n_manager().t(msgid)


def pgettext(context: str, msgid: str, **kwargs) -> str:
    """Translate with context using global manager."""
    return get_i18n_manager().pgettext(context, msgid, **kwargs)


def plural(singular: str, plural_form: str, n: int, **kwargs) -> str:
    """Translate plural using global manager."""
    return get_i18n_manager().plural(singular, plural_form, n, **kwargs)


def lazy_gettext(msgid: str) -> LazyProxy:
    """Lazy translation using global manager."""
    return get_i18n_manager().lazy_gettext(msgid)
