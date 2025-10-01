"""Translation file loading and compilation."""

from __future__ import annotations

import threading
from functools import lru_cache
from pathlib import Path
from typing import cast

from babel.support import Translations

from qtframework.utils.logger import get_logger


logger = get_logger(__name__)


class TranslationLoader:
    """Handles loading, compiling, and caching translation files."""

    def __init__(
        self,
        locale_dir: Path,
        domain: str = "qtframework",
        fallback_locales: list[str] | None = None,
        cache_size: int = 128,
        auto_compile: bool = True,
    ) -> None:
        """Initialize translation loader.

        Args:
            locale_dir: Directory containing locale subdirectories
            domain: The gettext domain (base name of .po files)
            fallback_locales: List of fallback locales in order
            cache_size: Size of translation cache
            auto_compile: Auto-compile .po to .mo in development
        """
        self.locale_dir = Path(locale_dir)
        self._domain = domain
        self._fallback_locales = fallback_locales or ["en_US", "en"]
        self._auto_compile = auto_compile

        # Translations cache
        self._translations: dict[str, Translations] = {}
        self._translations_lock = threading.RLock()

        # Configure LRU cache for translations
        self._get_translation_cached = lru_cache(maxsize=cache_size)(self._get_translation_uncached)

        # Auto-compile .po files if needed
        if auto_compile:
            self._compile_translations()

    def get_locale_chain(self, locale: str) -> list[str]:
        """Get the fallback chain for a locale.

        Examples:
            es_MX -> [es_MX, es, en_US, en]
            fr_CA -> [fr_CA, fr, en_US, en]
        """
        chain = [locale]

        # Add base language if locale has region
        if "_" in locale:
            base_lang = locale.split("_", maxsplit=1)[0]
            if base_lang not in chain:
                chain.append(base_lang)

        # Add configured fallbacks
        for fallback in self._fallback_locales:
            if fallback not in chain:
                chain.append(fallback)

        return chain

    def load_translations(self, locale: str) -> Translations:
        """Load translations for a specific locale with fallback support.

        Args:
            locale: Locale code to load

        Returns:
            Translations object for the locale
        """
        with self._translations_lock:
            if locale in self._translations:
                return self._translations[locale]

            locale_chain = self.get_locale_chain(locale)
            base_translation: Translations | None = None

            for loc in locale_chain:
                locale_path = self.locale_dir / loc / "LC_MESSAGES"
                if locale_path.exists():
                    try:
                        # Load using Babel's support
                        trans = cast(
                            "Translations",
                            Translations.load(
                                dirname=str(self.locale_dir), locales=[loc], domain=self._domain
                            ),
                        )

                        if base_translation is None:
                            base_translation = trans
                        else:
                            # Merge with fallback
                            base_translation.merge(trans)

                    except Exception as e:
                        logger.exception(f"Failed to load translations for {loc}: {e}")

            # If no translations found, create null translations
            if base_translation is None:
                base_translation = Translations()

            self._translations[locale] = base_translation
            return base_translation

    def _get_translation_uncached(self, msgid: str, translations: Translations | None) -> str:
        """Internal method to get translation without caching."""
        if translations:
            return translations.ugettext(msgid)
        return msgid

    def clear_cache(self) -> None:
        """Clear the translation cache."""
        self._get_translation_cached.cache_clear()

    def clear_translations(self) -> None:
        """Clear loaded translations."""
        with self._translations_lock:
            self._translations.clear()

    def get_available_locales(self) -> list[str]:
        """Get list of available locales.

        Returns:
            List of locale codes that have translation files
        """
        locales = []

        if self.locale_dir.exists():
            for path in self.locale_dir.iterdir():
                if path.is_dir():
                    # Check if it has translation files
                    mo_file = path / "LC_MESSAGES" / f"{self._domain}.mo"
                    po_file = path / "LC_MESSAGES" / f"{self._domain}.po"

                    if mo_file.exists() or po_file.exists():
                        locales.append(path.name)

        return sorted(locales)

    def _compile_translations(self) -> None:
        """Auto-compile .po files to .mo files if they are newer or missing.

        Only runs in development mode to avoid runtime overhead.
        """
        try:
            import polib

            for locale_dir in self.locale_dir.iterdir():
                if locale_dir.is_dir():
                    po_file = locale_dir / "LC_MESSAGES" / f"{self._domain}.po"
                    mo_file = locale_dir / "LC_MESSAGES" / f"{self._domain}.mo"

                    if po_file.exists():
                        # Check if .mo needs updating
                        if (
                            not mo_file.exists()
                            or po_file.stat().st_mtime > mo_file.stat().st_mtime
                        ):
                            try:
                                po = polib.pofile(str(po_file), encoding="utf-8")
                                po.save_as_mofile(str(mo_file))
                                logger.debug(f"Compiled {locale_dir.name}: {po_file} -> {mo_file}")
                            except Exception as e:
                                logger.warning("Failed to compile %s: %s", po_file, e)
        except ImportError:
            logger.debug("polib not available, skipping auto-compilation")
