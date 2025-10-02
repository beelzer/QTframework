"""Tests for base Widget class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtframework.widgets.base import Widget


if TYPE_CHECKING:
    from pytest_qt.qtbot import QtBot


class TestWidgetCreation:
    """Test Widget creation."""

    def test_widget_creation_default(self, qtbot: QtBot) -> None:
        """Test creating widget with defaults."""
        widget = Widget()
        qtbot.addWidget(widget)

        assert widget._style_class == ""
        assert widget._custom_properties == {}

    def test_widget_creation_with_object_name(self, qtbot: QtBot) -> None:
        """Test creating widget with object name."""
        widget = Widget(object_name="test_widget")
        qtbot.addWidget(widget)

        assert widget.objectName() == "test_widget"

    def test_widget_creation_with_style_class(self, qtbot: QtBot) -> None:
        """Test creating widget with style class."""
        widget = Widget(style_class="custom-class")
        qtbot.addWidget(widget)

        assert widget._style_class == "custom-class"
        assert widget.property("class") == "custom-class"


class TestWidgetStyleClass:
    """Test Widget style class operations."""

    def test_get_style_class(self, qtbot: QtBot) -> None:
        """Test getting style class."""
        widget = Widget(style_class="test-class")
        qtbot.addWidget(widget)

        assert widget._get_style_class() == "test-class"

    def test_set_style_class(self, qtbot: QtBot) -> None:
        """Test setting style class."""
        widget = Widget()
        qtbot.addWidget(widget)

        widget._set_style_class("new-class")
        assert widget._style_class == "new-class"
        assert widget.property("class") == "new-class"

    def test_set_style_class_emits_signal(self, qtbot: QtBot) -> None:
        """Test setting style class emits signal."""
        widget = Widget()
        qtbot.addWidget(widget)

        with qtbot.waitSignal(widget.style_changed, timeout=1000):
            widget._set_style_class("new-class")

    def test_set_same_style_class_no_signal(self, qtbot: QtBot) -> None:
        """Test setting same style class doesn't emit signal."""
        widget = Widget(style_class="test-class")
        qtbot.addWidget(widget)

        signals_received = []
        widget.style_changed.connect(lambda: signals_received.append(True))

        widget._set_style_class("test-class")
        assert signals_received == []

    def test_add_style_class(self, qtbot: QtBot) -> None:
        """Test adding style class."""
        widget = Widget()
        qtbot.addWidget(widget)

        widget.add_style_class("class1")
        assert widget._style_class == "class1"

        widget.add_style_class("class2")
        assert "class1" in widget._style_class
        assert "class2" in widget._style_class

    def test_add_duplicate_style_class(self, qtbot: QtBot) -> None:
        """Test adding duplicate style class."""
        widget = Widget(style_class="existing")
        qtbot.addWidget(widget)

        widget.add_style_class("existing")
        assert widget._style_class == "existing"  # Should not duplicate

    def test_remove_style_class(self, qtbot: QtBot) -> None:
        """Test removing style class."""
        widget = Widget(style_class="class1 class2 class3")
        qtbot.addWidget(widget)

        widget.remove_style_class("class2")
        assert "class1" in widget._style_class
        assert "class2" not in widget._style_class
        assert "class3" in widget._style_class

    def test_remove_nonexistent_style_class(self, qtbot: QtBot) -> None:
        """Test removing nonexistent style class."""
        widget = Widget(style_class="class1")
        qtbot.addWidget(widget)

        widget.remove_style_class("nonexistent")
        assert widget._style_class == "class1"

    def test_toggle_style_class_add(self, qtbot: QtBot) -> None:
        """Test toggle adds class when not present."""
        widget = Widget()
        qtbot.addWidget(widget)

        widget.toggle_style_class("active")
        assert "active" in widget._style_class

    def test_toggle_style_class_remove(self, qtbot: QtBot) -> None:
        """Test toggle removes class when present."""
        widget = Widget(style_class="active")
        qtbot.addWidget(widget)

        widget.toggle_style_class("active")
        assert "active" not in widget._style_class

    def test_has_style_class_true(self, qtbot: QtBot) -> None:
        """Test has_style_class returns True for existing class."""
        widget = Widget(style_class="class1 class2")
        qtbot.addWidget(widget)

        assert widget.has_style_class("class1") is True
        assert widget.has_style_class("class2") is True

    def test_has_style_class_false(self, qtbot: QtBot) -> None:
        """Test has_style_class returns False for non-existing class."""
        widget = Widget(style_class="class1")
        qtbot.addWidget(widget)

        assert widget.has_style_class("class2") is False


class TestWidgetCustomProperties:
    """Test Widget custom properties."""

    def test_set_custom_property(self, qtbot: QtBot) -> None:
        """Test setting custom property."""
        widget = Widget()
        qtbot.addWidget(widget)

        widget.set_custom_property("custom", "value")
        assert widget._custom_properties["custom"] == "value"
        assert widget.property("custom") == "value"

    def test_get_custom_property(self, qtbot: QtBot) -> None:
        """Test getting custom property."""
        widget = Widget()
        qtbot.addWidget(widget)

        widget.set_custom_property("test", "data")
        assert widget.get_custom_property("test") == "data"

    def test_get_custom_property_default(self, qtbot: QtBot) -> None:
        """Test getting nonexistent custom property returns default."""
        widget = Widget()
        qtbot.addWidget(widget)

        assert widget.get_custom_property("nonexistent") is None
        assert widget.get_custom_property("nonexistent", "default") == "default"

    def test_set_multiple_custom_properties(self, qtbot: QtBot) -> None:
        """Test setting multiple custom properties."""
        widget = Widget()
        qtbot.addWidget(widget)

        widget.set_custom_property("prop1", "value1")
        widget.set_custom_property("prop2", 123)
        widget.set_custom_property("prop3", True)

        assert widget.get_custom_property("prop1") == "value1"
        assert widget.get_custom_property("prop2") == 123
        assert widget.get_custom_property("prop3") is True

    def test_overwrite_custom_property(self, qtbot: QtBot) -> None:
        """Test overwriting custom property."""
        widget = Widget()
        qtbot.addWidget(widget)

        widget.set_custom_property("key", "old")
        widget.set_custom_property("key", "new")

        assert widget.get_custom_property("key") == "new"


class TestWidgetProperties:
    """Test Widget Qt properties."""

    def test_style_class_property(self, qtbot: QtBot) -> None:
        """Test styleClass property."""
        widget = Widget(style_class="initial")
        qtbot.addWidget(widget)

        assert widget.styleClass == "initial"

        widget.styleClass = "updated"
        assert widget.styleClass == "updated"


class TestWidgetApplication:
    """Test Widget application access."""

    def test_get_application_returns_instance(self, qtbot: QtBot) -> None:
        """Test get_application returns Application instance."""
        widget = Widget()
        qtbot.addWidget(widget)

        # Should return our Application instance from qapp fixture
        assert widget.get_application() is not None


class TestWidgetSignals:
    """Test Widget signals."""

    def test_style_changed_signal(self, qtbot: QtBot) -> None:
        """Test style_changed signal."""
        widget = Widget()
        qtbot.addWidget(widget)

        with qtbot.waitSignal(widget.style_changed, timeout=1000):
            widget.add_style_class("new-class")


class TestWidgetParent:
    """Test Widget parent handling."""

    def test_widget_with_parent(self, qtbot: QtBot) -> None:
        """Test creating widget with parent."""
        from PySide6.QtWidgets import QWidget

        parent = QWidget()
        qtbot.addWidget(parent)

        widget = Widget(parent=parent)
        qtbot.addWidget(widget)

        assert widget.parent() == parent

    def test_widget_without_parent(self, qtbot: QtBot) -> None:
        """Test creating widget without parent."""
        widget = Widget()
        qtbot.addWidget(widget)

        assert widget.parent() is None


class TestWidgetStyleClassComplex:
    """Test complex style class operations."""

    def test_multiple_class_operations(self, qtbot: QtBot) -> None:
        """Test multiple class operations in sequence."""
        widget = Widget()
        qtbot.addWidget(widget)

        widget.add_style_class("class1")
        widget.add_style_class("class2")
        widget.add_style_class("class3")

        assert widget.has_style_class("class1")
        assert widget.has_style_class("class2")
        assert widget.has_style_class("class3")

        widget.remove_style_class("class2")
        assert not widget.has_style_class("class2")
        assert widget.has_style_class("class1")
        assert widget.has_style_class("class3")

        widget.toggle_style_class("class4")
        assert widget.has_style_class("class4")

        widget.toggle_style_class("class4")
        assert not widget.has_style_class("class4")
