"""Tests for Button widgets."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon

from qtframework.widgets.buttons import Button, ButtonSize, ButtonVariant

if TYPE_CHECKING:
    from pytest_qt.qtbot import QtBot


class TestButtonVariant:
    """Test ButtonVariant enum."""

    def test_button_variant_values(self) -> None:
        """Test button variant enum values."""
        assert ButtonVariant.PRIMARY.value == "primary"
        assert ButtonVariant.SECONDARY.value == "secondary"
        assert ButtonVariant.SUCCESS.value == "success"
        assert ButtonVariant.WARNING.value == "warning"
        assert ButtonVariant.DANGER.value == "danger"
        assert ButtonVariant.INFO.value == "info"
        assert ButtonVariant.OUTLINE.value == "outline"
        assert ButtonVariant.TEXT.value == "text"


class TestButtonSize:
    """Test ButtonSize enum."""

    def test_button_size_values(self) -> None:
        """Test button size enum values."""
        assert ButtonSize.SMALL.value == "small"
        assert ButtonSize.MEDIUM.value == "medium"
        assert ButtonSize.LARGE.value == "large"


class TestButtonCreation:
    """Test Button creation."""

    def test_button_creation_default(self, qtbot: QtBot) -> None:
        """Test creating button with defaults."""
        button = Button()
        qtbot.addWidget(button)

        assert button.text() == ""
        assert button._variant == ButtonVariant.PRIMARY
        assert button._size == ButtonSize.MEDIUM

    def test_button_creation_with_text(self, qtbot: QtBot) -> None:
        """Test creating button with text."""
        button = Button("Click Me")
        qtbot.addWidget(button)

        assert button.text() == "Click Me"

    def test_button_creation_with_variant(self, qtbot: QtBot) -> None:
        """Test creating button with variant."""
        button = Button(variant=ButtonVariant.SUCCESS)
        qtbot.addWidget(button)

        assert button._variant == ButtonVariant.SUCCESS

    def test_button_creation_with_size(self, qtbot: QtBot) -> None:
        """Test creating button with size."""
        button = Button(size=ButtonSize.LARGE)
        qtbot.addWidget(button)

        assert button._size == ButtonSize.LARGE

    def test_button_creation_with_object_name(self, qtbot: QtBot) -> None:
        """Test creating button with object name."""
        button = Button(object_name="test_button")
        qtbot.addWidget(button)

        assert button.objectName() == "test_button"

    def test_button_creation_with_icon(self, qtbot: QtBot) -> None:
        """Test creating button with icon."""
        # Create a simple pixmap icon
        from PySide6.QtGui import QPixmap

        pixmap = QPixmap(16, 16)
        icon = QIcon(pixmap)
        button = Button(icon=icon)
        qtbot.addWidget(button)

        assert not button.icon().isNull()


class TestButtonVariants:
    """Test Button variant changes."""

    def test_button_primary_variant(self, qtbot: QtBot) -> None:
        """Test button with primary variant."""
        button = Button(variant=ButtonVariant.PRIMARY)
        qtbot.addWidget(button)

        assert "primary" in button.property("variant").lower()

    def test_button_secondary_variant(self, qtbot: QtBot) -> None:
        """Test button with secondary variant."""
        button = Button(variant=ButtonVariant.SECONDARY)
        qtbot.addWidget(button)

        assert "secondary" in button.property("variant").lower()

    def test_button_success_variant(self, qtbot: QtBot) -> None:
        """Test button with success variant."""
        button = Button(variant=ButtonVariant.SUCCESS)
        qtbot.addWidget(button)

        assert "success" in button.property("variant").lower()

    def test_button_warning_variant(self, qtbot: QtBot) -> None:
        """Test button with warning variant."""
        button = Button(variant=ButtonVariant.WARNING)
        qtbot.addWidget(button)

        assert "warning" in button.property("variant").lower()

    def test_button_danger_variant(self, qtbot: QtBot) -> None:
        """Test button with danger variant."""
        button = Button(variant=ButtonVariant.DANGER)
        qtbot.addWidget(button)

        assert "danger" in button.property("variant").lower()

    def test_button_info_variant(self, qtbot: QtBot) -> None:
        """Test button with info variant."""
        button = Button(variant=ButtonVariant.INFO)
        qtbot.addWidget(button)

        assert "info" in button.property("variant").lower()

    def test_button_outline_variant(self, qtbot: QtBot) -> None:
        """Test button with outline variant."""
        button = Button(variant=ButtonVariant.OUTLINE)
        qtbot.addWidget(button)

        assert "outline" in button.property("variant").lower()

    def test_button_text_variant(self, qtbot: QtBot) -> None:
        """Test button with text variant."""
        button = Button(variant=ButtonVariant.TEXT)
        qtbot.addWidget(button)

        assert "text" in button.property("variant").lower()


class TestButtonSizes:
    """Test Button size changes."""

    def test_button_small_size(self, qtbot: QtBot) -> None:
        """Test button with small size."""
        button = Button(size=ButtonSize.SMALL)
        qtbot.addWidget(button)

        assert button._size == ButtonSize.SMALL

    def test_button_medium_size(self, qtbot: QtBot) -> None:
        """Test button with medium size."""
        button = Button(size=ButtonSize.MEDIUM)
        qtbot.addWidget(button)

        assert button._size == ButtonSize.MEDIUM

    def test_button_large_size(self, qtbot: QtBot) -> None:
        """Test button with large size."""
        button = Button(size=ButtonSize.LARGE)
        qtbot.addWidget(button)

        assert button._size == ButtonSize.LARGE


class TestButtonSignals:
    """Test Button signals."""

    def test_button_clicked_signal(self, qtbot: QtBot) -> None:
        """Test button clicked signal."""
        button = Button("Click")
        qtbot.addWidget(button)

        with qtbot.waitSignal(button.clicked, timeout=1000):
            button.click()

    def test_button_variant_changed_signal(self, qtbot: QtBot) -> None:
        """Test variant changed signal."""
        button = Button()
        qtbot.addWidget(button)

        with qtbot.waitSignal(button.variant_changed, timeout=1000):
            button._set_variant("danger")

    def test_button_size_changed_signal(self, qtbot: QtBot) -> None:
        """Test size changed signal."""
        button = Button()
        qtbot.addWidget(button)

        with qtbot.waitSignal(button.size_changed, timeout=1000):
            button._set_size("large")


class TestButtonMethods:
    """Test Button methods."""

    def test_button_set_text(self, qtbot: QtBot) -> None:
        """Test setting button text."""
        button = Button()
        qtbot.addWidget(button)

        button.setText("New Text")
        assert button.text() == "New Text"

    def test_button_set_variant(self, qtbot: QtBot) -> None:
        """Test setting button variant."""
        button = Button()
        qtbot.addWidget(button)

        button._set_variant("success")
        assert button._variant == ButtonVariant.SUCCESS

    def test_button_set_size(self, qtbot: QtBot) -> None:
        """Test setting button size."""
        button = Button()
        qtbot.addWidget(button)

        button._set_size("small")
        assert button._size == ButtonSize.SMALL

    def test_button_get_variant(self, qtbot: QtBot) -> None:
        """Test getting button variant."""
        button = Button(variant=ButtonVariant.WARNING)
        qtbot.addWidget(button)

        assert button._get_variant() == "warning"

    def test_button_get_size(self, qtbot: QtBot) -> None:
        """Test getting button size."""
        button = Button(size=ButtonSize.LARGE)
        qtbot.addWidget(button)

        assert button._get_size() == "large"

    def test_button_enabled_disabled(self, qtbot: QtBot) -> None:
        """Test enabling/disabling button."""
        button = Button()
        qtbot.addWidget(button)

        assert button.isEnabled()

        button.setEnabled(False)
        assert not button.isEnabled()

        button.setEnabled(True)
        assert button.isEnabled()


class TestButtonProperties:
    """Test Button Qt properties."""

    def test_button_variant_property(self, qtbot: QtBot) -> None:
        """Test variant property."""
        button = Button(variant=ButtonVariant.DANGER)
        qtbot.addWidget(button)

        assert button.property("variant") == "danger"

    def test_button_size_property(self, qtbot: QtBot) -> None:
        """Test size property."""
        button = Button(size=ButtonSize.SMALL)
        qtbot.addWidget(button)

        assert button._get_size() == "small"


class TestButtonInteraction:
    """Test Button interaction."""

    def test_button_click_interaction(self, qtbot: QtBot) -> None:
        """Test button click interaction."""
        from PySide6.QtCore import Qt

        button = Button("Test")
        qtbot.addWidget(button)

        clicked = []
        button.clicked.connect(lambda: clicked.append(True))

        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        assert clicked == [True]

    def test_button_is_enabled(self, qtbot: QtBot) -> None:
        """Test button is enabled by default."""
        button = Button()
        qtbot.addWidget(button)

        assert button.isEnabled()
