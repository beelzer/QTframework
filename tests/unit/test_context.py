"""Tests for Context class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtframework.core.context import Context


if TYPE_CHECKING:
    from pytest_qt.qtbot import QtBot


class TestContextCreation:
    """Test Context creation."""

    def test_context_creation(self) -> None:
        """Test creating context."""
        context = Context()
        assert context._data == {}

    def test_context_initialization(self) -> None:
        """Test context initializes empty."""
        context = Context()
        assert context.keys() == []


class TestContextSetGet:
    """Test Context set and get operations."""

    def test_set_value(self) -> None:
        """Test setting a value."""
        context = Context()
        context.set("key", "value")
        assert context._data["key"] == "value"

    def test_get_value(self) -> None:
        """Test getting a value."""
        context = Context()
        context.set("key", "value")
        assert context.get("key") == "value"

    def test_get_nonexistent_value(self) -> None:
        """Test getting nonexistent value returns None."""
        context = Context()
        assert context.get("nonexistent") is None

    def test_get_with_default(self) -> None:
        """Test getting value with default."""
        context = Context()
        assert context.get("nonexistent", "default") == "default"

    def test_set_overwrites_existing(self) -> None:
        """Test setting overwrites existing value."""
        context = Context()
        context.set("key", "old")
        context.set("key", "new")
        assert context.get("key") == "new"

    def test_set_multiple_values(self) -> None:
        """Test setting multiple values."""
        context = Context()
        context.set("key1", "value1")
        context.set("key2", "value2")
        context.set("key3", "value3")

        assert context.get("key1") == "value1"
        assert context.get("key2") == "value2"
        assert context.get("key3") == "value3"


class TestContextRemove:
    """Test Context remove operations."""

    def test_remove_existing_key(self) -> None:
        """Test removing existing key."""
        context = Context()
        context.set("key", "value")
        context.remove("key")

        assert context.get("key") is None
        assert "key" not in context._data

    def test_remove_nonexistent_key(self) -> None:
        """Test removing nonexistent key doesn't error."""
        context = Context()
        context.remove("nonexistent")  # Should not raise

    def test_remove_emits_signal(self, qtbot: QtBot) -> None:
        """Test remove emits value_changed signal."""
        context = Context()
        context.set("key", "value")

        with qtbot.waitSignal(context.value_changed, timeout=1000) as blocker:
            context.remove("key")

        assert blocker.args == ["key", None]


class TestContextClear:
    """Test Context clear operations."""

    def test_clear_empty_context(self) -> None:
        """Test clearing empty context."""
        context = Context()
        context.clear()
        assert context._data == {}

    def test_clear_with_values(self) -> None:
        """Test clearing context with values."""
        context = Context()
        context.set("key1", "value1")
        context.set("key2", "value2")

        context.clear()

        assert context._data == {}
        assert context.get("key1") is None
        assert context.get("key2") is None


class TestContextKeys:
    """Test Context keys operations."""

    def test_keys_empty(self) -> None:
        """Test keys on empty context."""
        context = Context()
        assert context.keys() == []

    def test_keys_with_values(self) -> None:
        """Test keys with values."""
        context = Context()
        context.set("key1", "value1")
        context.set("key2", "value2")
        context.set("key3", "value3")

        keys = context.keys()
        assert "key1" in keys
        assert "key2" in keys
        assert "key3" in keys
        assert len(keys) == 3

    def test_keys_after_remove(self) -> None:
        """Test keys after removing a key."""
        context = Context()
        context.set("key1", "value1")
        context.set("key2", "value2")
        context.remove("key1")

        keys = context.keys()
        assert "key1" not in keys
        assert "key2" in keys


class TestContextItems:
    """Test Context items operations."""

    def test_items_empty(self) -> None:
        """Test items on empty context."""
        context = Context()
        assert context.items() == []

    def test_items_with_values(self) -> None:
        """Test items with values."""
        context = Context()
        context.set("key1", "value1")
        context.set("key2", "value2")

        items = context.items()
        assert ("key1", "value1") in items
        assert ("key2", "value2") in items
        assert len(items) == 2

    def test_items_returns_list(self) -> None:
        """Test items returns a list."""
        context = Context()
        context.set("key", "value")

        items = context.items()
        assert isinstance(items, list)


class TestContextUpdate:
    """Test Context update operations."""

    def test_update_empty(self) -> None:
        """Test updating with empty dict."""
        context = Context()
        context.update({})
        assert context._data == {}

    def test_update_single_value(self) -> None:
        """Test updating with single value."""
        context = Context()
        context.update({"key": "value"})
        assert context.get("key") == "value"

    def test_update_multiple_values(self) -> None:
        """Test updating with multiple values."""
        context = Context()
        context.update({"key1": "value1", "key2": "value2", "key3": "value3"})

        assert context.get("key1") == "value1"
        assert context.get("key2") == "value2"
        assert context.get("key3") == "value3"

    def test_update_overwrites_existing(self) -> None:
        """Test update overwrites existing values."""
        context = Context()
        context.set("key", "old")
        context.update({"key": "new"})

        assert context.get("key") == "new"

    def test_update_merges_with_existing(self) -> None:
        """Test update merges with existing values."""
        context = Context()
        context.set("key1", "value1")
        context.update({"key2": "value2"})

        assert context.get("key1") == "value1"
        assert context.get("key2") == "value2"


class TestContextSignals:
    """Test Context signal emissions."""

    def test_value_changed_signal_on_set(self, qtbot: QtBot) -> None:
        """Test value_changed signal emitted on set."""
        context = Context()

        with qtbot.waitSignal(context.value_changed, timeout=1000) as blocker:
            context.set("key", "value")

        assert blocker.args == ["key", "value"]

    def test_value_changed_signal_on_update(self, qtbot: QtBot) -> None:
        """Test value_changed signal emitted on update."""
        context = Context()

        with qtbot.waitSignal(context.value_changed, timeout=1000):
            context.set("key", "old")

        with qtbot.waitSignal(context.value_changed, timeout=1000) as blocker:
            context.set("key", "new")

        assert blocker.args == ["key", "new"]

    def test_no_signal_when_same_value(self, qtbot: QtBot) -> None:
        """Test no signal when setting same value."""
        context = Context()
        context.set("key", "value")

        signals_received = []
        context.value_changed.connect(lambda k, v: signals_received.append((k, v)))

        context.set("key", "value")  # Same value
        assert signals_received == []

    def test_value_changed_signal_multiple_updates(self, qtbot: QtBot) -> None:
        """Test multiple value_changed signals."""
        context = Context()
        signals_received = []

        context.value_changed.connect(lambda k, v: signals_received.append((k, v)))

        context.update({"key1": "value1", "key2": "value2"})

        assert ("key1", "value1") in signals_received
        assert ("key2", "value2") in signals_received


class TestContextDataTypes:
    """Test Context with different data types."""

    def test_string_values(self) -> None:
        """Test context with string values."""
        context = Context()
        context.set("key", "string value")
        assert context.get("key") == "string value"

    def test_integer_values(self) -> None:
        """Test context with integer values."""
        context = Context()
        context.set("count", 42)
        assert context.get("count") == 42

    def test_boolean_values(self) -> None:
        """Test context with boolean values."""
        context = Context()
        context.set("flag", True)
        assert context.get("flag") is True

    def test_list_values(self) -> None:
        """Test context with list values."""
        context = Context()
        context.set("items", [1, 2, 3])
        assert context.get("items") == [1, 2, 3]

    def test_dict_values(self) -> None:
        """Test context with dict values."""
        context = Context()
        context.set("config", {"nested": "value"})
        assert context.get("config") == {"nested": "value"}

    def test_none_values(self) -> None:
        """Test context with None values."""
        context = Context()
        context.set("empty", None)
        assert context.get("empty") is None

    def test_mixed_types(self) -> None:
        """Test context with mixed types."""
        context = Context()
        context.update({
            "string": "text",
            "number": 123,
            "flag": True,
            "list": [1, 2, 3],
            "dict": {"key": "value"},
        })

        assert context.get("string") == "text"
        assert context.get("number") == 123
        assert context.get("flag") is True
        assert context.get("list") == [1, 2, 3]
        assert context.get("dict") == {"key": "value"}
