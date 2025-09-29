"""Translation context helpers and lazy evaluation support.

This module provides advanced i18n features including:
- Translation contexts for disambiguation
- Lazy translation evaluation
- Message formatting with ICU-style patterns
"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps

from babel.support import LazyProxy

from qtframework.i18n.babel_manager import get_i18n_manager


class TranslationContext:
    """Context for disambiguating translations.

    Usage:
        # Same word, different meanings
        may_month = pgettext("month", "May")
        may_permission = pgettext("permission", "May")

        # Widget-specific context
        save_button = pgettext("button", "Save")
        save_menu = pgettext("menu", "Save")
    """

    def __init__(self, context: str):
        """Initialize with a context string."""
        self.context = context
        self._manager = get_i18n_manager()

    def t(self, msgid: str, **kwargs) -> str:
        """Translate with this context."""
        return self._manager.pgettext(self.context, msgid, **kwargs)

    def plural(self, singular: str, plural_form: str, n: int, **kwargs) -> str:
        """Translate plural with this context."""
        return self._manager.npgettext(self.context, singular, plural_form, n, **kwargs)

    def lazy(self, msgid: str) -> LazyProxy:
        """Create lazy translation with this context."""
        return self._manager.lazy_pgettext(self.context, msgid)


# Predefined contexts for common UI elements
class UIContext:
    """Standard UI element contexts."""

    button = TranslationContext("button")
    menu = TranslationContext("menu")
    tooltip = TranslationContext("tooltip")
    label = TranslationContext("label")
    title = TranslationContext("title")
    placeholder = TranslationContext("placeholder")
    error = TranslationContext("error")
    warning = TranslationContext("warning")
    info = TranslationContext("info")
    success = TranslationContext("success")
    dialog = TranslationContext("dialog")
    tab = TranslationContext("tab")
    header = TranslationContext("header")
    footer = TranslationContext("footer")


class LazyString:
    """Lazy string that delays translation until str() is called.

    This is useful for module-level constants that need translation
    but are defined before the locale is set.

    Usage:
        # At module level
        ERROR_MESSAGE = LazyString("An error occurred")

        # Later, when locale is set
        print(str(ERROR_MESSAGE))  # Translates to current locale
    """

    def __init__(self, msgid: str, context: str | None = None, **kwargs):
        """Initialize lazy string.

        Args:
            msgid: Message ID to translate
            context: Optional context for disambiguation
            **kwargs: Formatting parameters
        """
        self.msgid = msgid
        self.context = context
        self.kwargs = kwargs

    def __str__(self) -> str:
        """Evaluate translation when converted to string."""
        manager = get_i18n_manager()
        if self.context:
            translated = manager.pgettext(self.context, self.msgid)
        else:
            translated = manager.t(self.msgid)

        if self.kwargs:
            try:
                translated = translated.format(**self.kwargs)
            except (KeyError, ValueError):
                pass

        return translated

    def __repr__(self) -> str:
        """Return representation for debugging."""
        return f"LazyString({self.msgid!r}, context={self.context!r})"

    def format(self, **kwargs) -> LazyString:
        """Create new LazyString with additional format parameters."""
        new_kwargs = {**self.kwargs, **kwargs}
        return LazyString(self.msgid, self.context, **new_kwargs)


class LazyPlural:
    """Lazy plural string that delays translation until evaluation.

    Usage:
        # At module level
        ITEMS_COUNT = LazyPlural(
            "{count} item",
            "{count} items"
        )

        # Later
        print(ITEMS_COUNT.format(count=5))  # "5 items"
    """

    def __init__(self, singular: str, plural: str, context: str | None = None):
        """Initialize lazy plural.

        Args:
            singular: Singular form
            plural: Plural form
            context: Optional context
        """
        self.singular = singular
        self.plural = plural
        self.context = context

    def format(self, n: int, **kwargs) -> str:
        """Format with count and additional parameters.

        Args:
            n: Count for pluralization
            **kwargs: Additional format parameters

        Returns:
            Translated and formatted string
        """
        manager = get_i18n_manager()

        if self.context:
            translated = manager.npgettext(self.context, self.singular, self.plural, n)
        else:
            translated = manager.plural(self.singular, self.plural, n)

        # Ensure count is in kwargs
        if "count" not in kwargs:
            kwargs["count"] = n

        try:
            return translated.format(**kwargs)
        except (KeyError, ValueError):
            return translated

    def __repr__(self) -> str:
        """Return representation for debugging."""
        return f"LazyPlural({self.singular!r}, {self.plural!r}, context={self.context!r})"


def translatable_property(context: str | None = None):
    """Decorator for creating translatable class properties.

    Usage:
        class MyWidget:
            @translatable_property("tooltip")
            def help_text(self):
                return "Click here for help"

    The property will automatically translate when accessed.
    """

    def decorator(func: Callable) -> property:
        @wraps(func)
        def getter(self) -> str:
            msgid = func(self)
            manager = get_i18n_manager()

            if context:
                return manager.pgettext(context, msgid)
            return manager.t(msgid)

        return property(getter)

    return decorator


class MessageFormatter:
    """Advanced message formatter supporting ICU-style patterns.

    This provides more complex formatting than simple string.format(),
    including gender, select cases, and nested patterns.

    Usage:
        formatter = MessageFormatter()

        # Gender-aware messages
        pattern = "{name} {gender, select, male {his} female {her} other {their}} profile"
        result = formatter.format(pattern, name="Alex", gender="female")
        # "Alex her profile"

        # Plural with select
        pattern = "{count, plural, =0 {no items} one {# item} other {# items}}"
        result = formatter.format(pattern, count=5)
        # "5 items"
    """

    def __init__(self):
        """Initialize formatter."""
        self._manager = get_i18n_manager()

    def format(self, pattern: str, **kwargs) -> str:
        """Format a pattern with parameters.

        Args:
            pattern: ICU-style message pattern
            **kwargs: Parameters for formatting

        Returns:
            Formatted string
        """
        # This is a simplified implementation
        # For full ICU support, consider using py-icu library

        result = pattern

        # Handle select patterns
        import re

        select_pattern = r"\{(\w+),\s*select,\s*([^}]+)\}"
        for match in re.finditer(select_pattern, result):
            param_name = match.group(1)
            cases = match.group(2)

            if param_name in kwargs:
                value = kwargs[param_name]
                # Parse cases
                case_dict = {}
                for case_match in re.finditer(r"(\w+)\s*\{([^}]*)\}", cases):
                    case_key = case_match.group(1)
                    case_value = case_match.group(2)
                    case_dict[case_key] = case_value

                # Get matching case or 'other'
                replacement = case_dict.get(value, case_dict.get("other", ""))
                result = result.replace(match.group(0), replacement)

        # Handle plural patterns (simplified)
        plural_pattern = r"\{(\w+),\s*plural,\s*([^}]+)\}"
        for match in re.finditer(plural_pattern, result):
            param_name = match.group(1)
            cases = match.group(2)

            if param_name in kwargs:
                count = kwargs[param_name]
                # Parse cases
                case_dict = {}
                for case_match in re.finditer(r"(=?\w+)\s*\{([^}]*)\}", cases):
                    case_key = case_match.group(1)
                    case_value = case_match.group(2)
                    # Replace # with count
                    case_value = case_value.replace("#", str(count))
                    case_dict[case_key] = case_value

                # Determine which case to use
                if f"={count}" in case_dict:
                    replacement = case_dict[f"={count}"]
                elif count == 1 and "one" in case_dict:
                    replacement = case_dict["one"]
                else:
                    replacement = case_dict.get("other", str(count))

                result = result.replace(match.group(0), replacement)

        # Handle simple placeholders
        try:
            result = result.format(**kwargs)
        except (KeyError, ValueError):
            pass

        return result


# Convenience functions
def lazy(msgid: str, context: str | None = None, **kwargs) -> LazyString:
    """Create a lazy translatable string."""
    return LazyString(msgid, context, **kwargs)


def lazy_plural(singular: str, plural: str, context: str | None = None) -> LazyPlural:
    """Create a lazy plural string."""
    return LazyPlural(singular, plural, context)


# Context shortcuts
button = UIContext.button
menu = UIContext.menu
tooltip = UIContext.tooltip
label = UIContext.label
title = UIContext.title
error = UIContext.error
warning = UIContext.warning
info = UIContext.info
success = UIContext.success
