"""Comprehensive tests for Config class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pydantic import BaseModel

from qtframework.config.config import Config


if TYPE_CHECKING:
    from pytest_qt.qtbot import QtBot


class TestConfigBasics:
    """Test basic Config functionality."""

    def test_config_creation_empty(self) -> None:
        """Test creating empty config."""
        config = Config()
        assert config.to_dict() == {}

    def test_config_creation_with_data(self) -> None:
        """Test creating config with initial data."""
        data = {"key": "value", "nested": {"key2": "value2"}}
        config = Config(data)
        assert config.get("key") == "value"
        assert config.get("nested.key2") == "value2"

    def test_get_simple_key(self) -> None:
        """Test getting simple key."""
        config = Config({"key": "value"})
        assert config.get("key") == "value"

    def test_get_nested_key(self) -> None:
        """Test getting nested key."""
        config = Config({"level1": {"level2": {"level3": "value"}}})
        assert config.get("level1.level2.level3") == "value"

    def test_get_nonexistent_key(self) -> None:
        """Test getting nonexistent key returns default."""
        config = Config({"key": "value"})
        assert config.get("nonexistent") is None
        assert config.get("nonexistent", "default") == "default"

    def test_get_nested_nonexistent_key(self) -> None:
        """Test getting nested nonexistent key."""
        config = Config({"level1": {"level2": "value"}})
        assert config.get("level1.nonexistent") is None
        assert config.get("level1.level2.nonexistent") is None

    def test_set_simple_key(self) -> None:
        """Test setting simple key."""
        config = Config()
        config.set("key", "value")
        assert config.get("key") == "value"

    def test_set_nested_key(self) -> None:
        """Test setting nested key creates intermediate dicts."""
        config = Config()
        config.set("level1.level2.level3", "value")
        assert config.get("level1.level2.level3") == "value"

    def test_set_overwrites_existing(self) -> None:
        """Test setting overwrites existing value."""
        config = Config({"key": "old"})
        config.set("key", "new")
        assert config.get("key") == "new"

    def test_set_nested_overwrites(self) -> None:
        """Test setting nested key overwrites."""
        config = Config({"level1": {"level2": "old"}})
        config.set("level1.level2", "new")
        assert config.get("level1.level2") == "new"


class TestConfigDelete:
    """Test Config delete functionality."""

    def test_delete_existing_key(self) -> None:
        """Test deleting existing key."""
        config = Config({"key": "value"})
        result = config.delete("key")
        assert result is True
        assert config.get("key") is None

    def test_delete_nonexistent_key(self) -> None:
        """Test deleting nonexistent key."""
        config = Config({"key": "value"})
        result = config.delete("nonexistent")
        assert result is False

    def test_delete_nested_key(self) -> None:
        """Test deleting nested key."""
        config = Config({"level1": {"level2": "value"}})
        result = config.delete("level1.level2")
        assert result is True
        assert config.get("level1.level2") is None

    def test_delete_nested_nonexistent(self) -> None:
        """Test deleting nonexistent nested key."""
        config = Config({"level1": {"level2": "value"}})
        result = config.delete("level1.nonexistent")
        assert result is False


class TestConfigHas:
    """Test Config has functionality."""

    def test_has_existing_key(self) -> None:
        """Test checking existing key."""
        config = Config({"key": "value"})
        assert config.has("key") is True

    def test_has_nonexistent_key(self) -> None:
        """Test checking nonexistent key."""
        config = Config({"key": "value"})
        assert config.has("nonexistent") is False

    def test_has_nested_key(self) -> None:
        """Test checking nested key."""
        config = Config({"level1": {"level2": "value"}})
        assert config.has("level1.level2") is True

    def test_has_nested_nonexistent(self) -> None:
        """Test checking nonexistent nested key."""
        config = Config({"level1": {"level2": "value"}})
        assert config.has("level1.nonexistent") is False

    def test_has_with_none_value(self) -> None:
        """Test has with None value (should return False)."""
        config = Config({"key": None})
        assert config.has("key") is False


class TestConfigWatch:
    """Test Config watch functionality."""

    def test_watch_simple_key(self, qtbot: QtBot) -> None:
        """Test watching a key."""
        config = Config({"key": "value"})
        changes = []

        def callback(value):
            changes.append(value)

        unwatch = config.watch("key", callback)

        config.set("key", "new_value")
        assert changes == ["new_value"]

        unwatch()

    def test_watch_multiple_changes(self, qtbot: QtBot) -> None:
        """Test watching multiple changes."""
        config = Config()
        changes = []

        config.watch("key", changes.append)

        config.set("key", "value1")
        config.set("key", "value2")
        config.set("key", "value3")

        assert changes == ["value1", "value2", "value3"]

    def test_unwatch(self, qtbot: QtBot) -> None:
        """Test unwatching."""
        config = Config()
        changes = []

        unwatch = config.watch("key", changes.append)

        config.set("key", "value1")
        unwatch()
        config.set("key", "value2")

        assert changes == ["value1"]

    def test_watch_nested_key(self, qtbot: QtBot) -> None:
        """Test watching nested key."""
        config = Config({"level1": {"level2": "value"}})
        changes = []

        config.watch("level1.level2", changes.append)
        config.set("level1.level2", "new_value")

        assert changes == ["new_value"]

    def test_watch_no_change_when_same_value(self, qtbot: QtBot) -> None:
        """Test watcher not called when value doesn't change."""
        config = Config({"key": "value"})
        changes = []

        config.watch("key", changes.append)
        config.set("key", "value")  # Same value

        assert changes == []


class TestConfigMerge:
    """Test Config merge functionality."""

    def test_merge_shallow(self) -> None:
        """Test shallow merge."""
        config = Config({"key1": "value1"})
        config.merge({"key2": "value2"}, deep=False)

        assert config.get("key1") == "value1"
        assert config.get("key2") == "value2"

    def test_merge_deep(self) -> None:
        """Test deep merge."""
        config = Config({"level1": {"key1": "value1"}})
        config.merge({"level1": {"key2": "value2"}}, deep=True)

        assert config.get("level1.key1") == "value1"
        assert config.get("level1.key2") == "value2"

    def test_merge_deep_overwrites(self) -> None:
        """Test deep merge overwrites existing keys."""
        config = Config({"level1": {"key1": "old"}})
        config.merge({"level1": {"key1": "new"}}, deep=True)

        assert config.get("level1.key1") == "new"

    def test_merge_emits_signal(self, qtbot: QtBot) -> None:
        """Test merge emits config_reloaded signal."""
        config = Config()

        with qtbot.waitSignal(config.config_reloaded, timeout=1000):
            config.merge({"key": "value"})


class TestConfigDictOperations:
    """Test Config dict operations."""

    def test_to_dict(self) -> None:
        """Test converting to dictionary."""
        data = {"key": "value", "nested": {"key2": "value2"}}
        config = Config(data)
        result = config.to_dict()

        assert result == data
        assert result is not config._data  # Should be a copy

    def test_from_dict(self) -> None:
        """Test loading from dictionary."""
        config = Config()
        data = {"key": "value", "nested": {"key2": "value2"}}
        config.from_dict(data)

        assert config.get("key") == "value"
        assert config.get("nested.key2") == "value2"

    def test_from_dict_emits_signal(self, qtbot: QtBot) -> None:
        """Test from_dict emits config_reloaded signal."""
        config = Config()

        with qtbot.waitSignal(config.config_reloaded, timeout=1000):
            config.from_dict({"key": "value"})

    def test_clear(self) -> None:
        """Test clearing config."""
        config = Config({"key": "value"})
        config.clear()

        assert config.to_dict() == {}
        assert config.get("key") is None

    def test_clear_emits_signal(self, qtbot: QtBot) -> None:
        """Test clear emits config_reloaded signal."""
        config = Config({"key": "value"})

        with qtbot.waitSignal(config.config_reloaded, timeout=1000):
            config.clear()


class TestConfigKeys:
    """Test Config keys functionality."""

    def test_keys_simple(self) -> None:
        """Test getting all keys."""
        config = Config({"key1": "value1", "key2": "value2"})
        keys = config.keys()

        assert "key1" in keys
        assert "key2" in keys

    def test_keys_nested(self) -> None:
        """Test getting nested keys."""
        config = Config({"level1": {"level2": {"level3": "value"}}})
        keys = config.keys()

        assert "level1" in keys
        assert "level1.level2" in keys
        assert "level1.level2.level3" in keys

    def test_keys_with_prefix(self) -> None:
        """Test getting keys with prefix."""
        config = Config({
            "app": {"name": "test", "version": "1.0"},
            "database": {"host": "localhost"},
        })
        keys = config.keys(prefix="app")

        assert "app" in keys
        assert "app.name" in keys
        assert "app.version" in keys
        assert "database" not in keys


class TestConfigValidation:
    """Test Config validation functionality."""

    def test_validate_valid_schema(self) -> None:
        """Test validating with valid schema."""

        class TestSchema(BaseModel):
            name: str
            version: str

        config = Config({"name": "test", "version": "1.0"})
        assert config.validate(TestSchema) is True

    def test_validate_invalid_schema(self) -> None:
        """Test validating with invalid schema."""

        class TestSchema(BaseModel):
            name: str
            version: str

        config = Config({"name": "test"})  # Missing version
        assert config.validate(TestSchema) is False


class TestConfigDunderMethods:
    """Test Config dunder methods."""

    def test_getitem(self) -> None:
        """Test __getitem__."""
        config = Config({"key": "value"})
        assert config["key"] == "value"

    def test_getitem_nested(self) -> None:
        """Test __getitem__ with nested key."""
        config = Config({"level1": {"level2": "value"}})
        assert config["level1.level2"] == "value"

    def test_getitem_raises_keyerror(self) -> None:
        """Test __getitem__ raises KeyError for nonexistent key."""
        config = Config({"key": "value"})
        with pytest.raises(KeyError):
            _ = config["nonexistent"]

    def test_setitem(self) -> None:
        """Test __setitem__."""
        config = Config()
        config["key"] = "value"
        assert config.get("key") == "value"

    def test_setitem_nested(self) -> None:
        """Test __setitem__ with nested key."""
        config = Config()
        config["level1.level2"] = "value"
        assert config.get("level1.level2") == "value"

    def test_contains(self) -> None:
        """Test __contains__."""
        config = Config({"key": "value"})
        assert "key" in config
        assert "nonexistent" not in config

    def test_contains_nested(self) -> None:
        """Test __contains__ with nested key."""
        config = Config({"level1": {"level2": "value"}})
        assert "level1.level2" in config
        assert "level1.nonexistent" not in config


class TestConfigSignals:
    """Test Config signal emissions."""

    def test_value_changed_signal_on_set(self, qtbot: QtBot) -> None:
        """Test value_changed signal emitted on set."""
        config = Config()

        with qtbot.waitSignal(config.value_changed, timeout=1000) as blocker:
            config.set("key", "value")

        assert blocker.args == ["key", "value"]

    def test_value_changed_signal_on_delete(self, qtbot: QtBot) -> None:
        """Test value_changed signal emitted on delete."""
        config = Config({"key": "value"})

        with qtbot.waitSignal(config.value_changed, timeout=1000) as blocker:
            config.delete("key")

        assert blocker.args == ["key", None]

    def test_no_signal_when_value_unchanged(self, qtbot: QtBot) -> None:
        """Test no signal when value doesn't change."""
        config = Config({"key": "value"})
        signals_received = []

        config.value_changed.connect(lambda k, v: signals_received.append((k, v)))
        config.set("key", "value")  # Same value

        assert signals_received == []
