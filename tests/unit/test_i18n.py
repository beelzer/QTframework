"""Basic tests for i18n package."""

from __future__ import annotations

import tempfile
from datetime import UTC
from pathlib import Path

from qtframework.i18n.locale_formatter import LocaleFormatter
from qtframework.i18n.translation_loader import TranslationLoader


class TestTranslationLoader:
    """Test translation loader."""

    def test_initialization(self) -> None:
        """Test loader initializes with defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = TranslationLoader(
                locale_dir=Path(tmpdir),
                domain="test",
                auto_compile=False,
            )
            assert loader.locale_dir == Path(tmpdir)
            assert loader._domain == "test"

    def test_get_locale_chain_simple(self) -> None:
        """Test locale chain for simple locale."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = TranslationLoader(
                locale_dir=Path(tmpdir),
                auto_compile=False,
            )
            chain = loader.get_locale_chain("en")
            assert "en" in chain

    def test_get_locale_chain_with_region(self) -> None:
        """Test locale chain includes base language."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = TranslationLoader(
                locale_dir=Path(tmpdir),
                auto_compile=False,
            )
            chain = loader.get_locale_chain("es_MX")
            assert "es_MX" in chain
            assert "es" in chain

    def test_get_locale_chain_includes_fallbacks(self) -> None:
        """Test locale chain includes fallback locales."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = TranslationLoader(
                locale_dir=Path(tmpdir),
                fallback_locales=["en_US", "en"],
                auto_compile=False,
            )
            chain = loader.get_locale_chain("fr_FR")
            assert "fr_FR" in chain
            assert "fr" in chain
            assert "en_US" in chain
            assert "en" in chain

    def test_get_available_locales_empty(self) -> None:
        """Test getting available locales from empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = TranslationLoader(
                locale_dir=Path(tmpdir),
                auto_compile=False,
            )
            locales = loader.get_available_locales()
            assert isinstance(locales, list)

    def test_custom_fallback_locales(self) -> None:
        """Test custom fallback locales."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = TranslationLoader(
                locale_dir=Path(tmpdir),
                fallback_locales=["de_DE", "de"],
                auto_compile=False,
            )
            assert loader._fallback_locales == ["de_DE", "de"]


class TestLocaleFormatter:
    """Test locale formatter."""

    def test_initialization_default(self) -> None:
        """Test formatter initializes with default locale."""
        formatter = LocaleFormatter()
        assert formatter.get_locale() == "en_US"

    def test_initialization_custom_locale(self) -> None:
        """Test formatter with custom locale."""
        formatter = LocaleFormatter(locale="fr_FR")
        assert formatter.get_locale() == "fr_FR"

    def test_format_number_basic(self) -> None:
        """Test basic number formatting."""
        formatter = LocaleFormatter(locale="en_US")
        result = formatter.format_number(1234.56)
        assert "1" in result
        assert "234" in result

    def test_format_number_integer(self) -> None:
        """Test integer formatting."""
        formatter = LocaleFormatter(locale="en_US")
        result = formatter.format_number(1000)
        assert "1" in result

    def test_format_currency_basic(self) -> None:
        """Test basic currency formatting."""
        formatter = LocaleFormatter(locale="en_US")
        result = formatter.format_currency(100.50, "USD")
        assert "100" in result

    def test_format_percent_basic(self) -> None:
        """Test basic percent formatting."""
        formatter = LocaleFormatter(locale="en_US")
        result = formatter.format_percent(0.75)
        assert "75" in result or "0.75" in result

    def test_format_date_basic(self) -> None:
        """Test basic date formatting."""
        from datetime import datetime

        formatter = LocaleFormatter(locale="en_US")
        date = datetime(2023, 12, 25, tzinfo=UTC)
        result = formatter.format_date(date)
        assert "2023" in result or "23" in result
        assert "12" in result or "25" in result

    def test_format_time_basic(self) -> None:
        """Test basic time formatting."""
        from datetime import datetime

        formatter = LocaleFormatter(locale="en_US")
        time = datetime(2023, 1, 1, 14, 30, 0, tzinfo=UTC)
        result = formatter.format_time(time)
        assert "14" in result or "2" in result or "30" in result

    def test_format_datetime_basic(self) -> None:
        """Test basic datetime formatting."""
        from datetime import datetime

        formatter = LocaleFormatter(locale="en_US")
        dt = datetime(2023, 12, 25, 14, 30, 0, tzinfo=UTC)
        result = formatter.format_datetime(dt)
        assert len(result) > 0

    def test_different_locales(self) -> None:
        """Test formatter with different locales."""
        formatter_us = LocaleFormatter(locale="en_US")
        formatter_fr = LocaleFormatter(locale="fr_FR")

        assert formatter_us.get_locale() == "en_US"
        assert formatter_fr.get_locale() == "fr_FR"

    def test_set_locale(self) -> None:
        """Test setting locale after initialization."""
        formatter = LocaleFormatter(locale="en_US")
        assert formatter.get_locale() == "en_US"

        formatter.set_locale("de_DE")
        assert formatter.get_locale() == "de_DE"
