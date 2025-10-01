"""Locale-aware formatting utilities using Babel's CLDR data."""

from __future__ import annotations

from babel.dates import format_date, format_datetime, format_time
from babel.numbers import (
    format_currency,
    format_decimal,
    format_number,
    format_percent,
    format_scientific,
)


class LocaleFormatter:
    """Provides locale-aware formatting for numbers, dates, and currency."""

    def __init__(self, locale: str = "en_US") -> None:
        """Initialize locale formatter.

        Args:
            locale: Locale code to use for formatting
        """
        self._locale = locale

    def set_locale(self, locale: str) -> None:
        """Set the locale for formatting.

        Args:
            locale: Locale code to use
        """
        self._locale = locale

    def get_locale(self) -> str:
        """Get the current locale.

        Returns:
            Current locale code
        """
        return self._locale

    # Number formatting methods

    def format_number(self, number: float, **kwargs) -> str:
        """Format number according to locale.

        Args:
            number: Number to format
            **kwargs: Additional formatting options

        Returns:
            Formatted number string
        """
        return format_number(number, locale=self._locale, **kwargs)

    def format_decimal(self, number: float, **kwargs) -> str:
        """Format decimal according to locale.

        Args:
            number: Decimal to format
            **kwargs: Additional formatting options

        Returns:
            Formatted decimal string
        """
        return format_decimal(number, locale=self._locale, **kwargs)

    def format_currency(self, number: float, currency: str, **kwargs) -> str:
        """Format currency according to locale.

        Args:
            number: Amount to format
            currency: Currency code (e.g., 'USD', 'EUR')
            **kwargs: Additional formatting options

        Returns:
            Formatted currency string
        """
        return format_currency(number, currency, locale=self._locale, **kwargs)

    def format_percent(self, number: float, **kwargs) -> str:
        """Format percentage according to locale.

        Args:
            number: Percentage to format (0.5 = 50%)
            **kwargs: Additional formatting options

        Returns:
            Formatted percentage string
        """
        return format_percent(number, locale=self._locale, **kwargs)

    def format_scientific(self, number: float, **kwargs) -> str:
        """Format number in scientific notation.

        Args:
            number: Number to format
            **kwargs: Additional formatting options

        Returns:
            Formatted scientific notation string
        """
        return format_scientific(number, locale=self._locale, **kwargs)

    # Date and time formatting methods

    def format_date(self, date, format: str = "medium") -> str:
        """Format date according to locale.

        Args:
            date: Date object to format
            format: Format style ('short', 'medium', 'long', 'full')

        Returns:
            Formatted date string
        """
        return format_date(date, format=format, locale=self._locale)

    def format_datetime(self, datetime, format: str = "medium") -> str:
        """Format datetime according to locale.

        Args:
            datetime: Datetime object to format
            format: Format style ('short', 'medium', 'long', 'full')

        Returns:
            Formatted datetime string
        """
        return format_datetime(datetime, format=format, locale=self._locale)

    def format_time(self, time, format: str = "medium") -> str:
        """Format time according to locale.

        Args:
            time: Time object to format
            format: Format style ('short', 'medium', 'long', 'full')

        Returns:
            Formatted time string
        """
        return format_time(time, format=format, locale=self._locale)
