"""Basic tests for layouts package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtframework.layouts.base import Alignment, Direction, FlexLayout


if TYPE_CHECKING:
    from pytest_qt.qtbot import QtBot


class TestDirection:
    """Test Direction enum."""

    def test_direction_values(self) -> None:
        """Test direction enum values."""
        assert Direction.HORIZONTAL.value == "horizontal"
        assert Direction.VERTICAL.value == "vertical"


class TestAlignment:
    """Test Alignment enum."""

    def test_alignment_values(self) -> None:
        """Test alignment enum values."""
        assert Alignment.START.value == "start"
        assert Alignment.CENTER.value == "center"
        assert Alignment.END.value == "end"
        assert Alignment.STRETCH.value == "stretch"
        assert Alignment.SPACE_BETWEEN.value == "space_between"
        assert Alignment.SPACE_AROUND.value == "space_around"
        assert Alignment.SPACE_EVENLY.value == "space_evenly"


class TestFlexLayout:
    """Test FlexLayout."""

    def test_initialization_default(self, qtbot: QtBot) -> None:
        """Test FlexLayout with default parameters."""
        layout = FlexLayout()
        assert layout is not None
        assert layout.spacing() == 8

    def test_initialization_horizontal(self, qtbot: QtBot) -> None:
        """Test FlexLayout with horizontal direction."""
        layout = FlexLayout(direction=Direction.HORIZONTAL)
        assert layout is not None

    def test_initialization_vertical(self, qtbot: QtBot) -> None:
        """Test FlexLayout with vertical direction."""
        layout = FlexLayout(direction=Direction.VERTICAL)
        assert layout is not None

    def test_custom_spacing(self, qtbot: QtBot) -> None:
        """Test FlexLayout with custom spacing."""
        layout = FlexLayout(spacing=16)
        assert layout.spacing() == 16

    def test_margins_single_value(self, qtbot: QtBot) -> None:
        """Test FlexLayout with single margin value."""
        layout = FlexLayout(margins=10)
        margins = layout.contentsMargins()
        assert margins.left() == 10
        assert margins.top() == 10
        assert margins.right() == 10
        assert margins.bottom() == 10

    def test_margins_tuple(self, qtbot: QtBot) -> None:
        """Test FlexLayout with tuple of margin values."""
        layout = FlexLayout(margins=(5, 10, 15, 20))
        margins = layout.contentsMargins()
        assert margins.left() == 5
        assert margins.top() == 10
        assert margins.right() == 15
        assert margins.bottom() == 20

    def test_alignment_start(self, qtbot: QtBot) -> None:
        """Test FlexLayout with start alignment."""
        layout = FlexLayout(alignment=Alignment.START)
        assert layout is not None

    def test_alignment_center(self, qtbot: QtBot) -> None:
        """Test FlexLayout with center alignment."""
        layout = FlexLayout(alignment=Alignment.CENTER)
        assert layout is not None

    def test_alignment_end(self, qtbot: QtBot) -> None:
        """Test FlexLayout with end alignment."""
        layout = FlexLayout(alignment=Alignment.END)
        assert layout is not None

    def test_alignment_stretch(self, qtbot: QtBot) -> None:
        """Test FlexLayout with stretch alignment."""
        layout = FlexLayout(alignment=Alignment.STRETCH)
        assert layout is not None

    def test_count_empty(self, qtbot: QtBot) -> None:
        """Test FlexLayout starts with no items."""
        layout = FlexLayout()
        assert layout.count() == 0

    def test_add_widget(self, qtbot: QtBot) -> None:
        """Test adding widget to layout."""
        from PySide6.QtWidgets import QPushButton

        layout = FlexLayout()
        button = QPushButton("Test")
        qtbot.addWidget(button)

        layout.addWidget(button)
        assert layout.count() == 1

    def test_add_multiple_widgets(self, qtbot: QtBot) -> None:
        """Test adding multiple widgets."""
        from PySide6.QtWidgets import QPushButton

        layout = FlexLayout()
        for i in range(3):
            button = QPushButton(f"Button {i}")
            qtbot.addWidget(button)
            layout.addWidget(button)

        assert layout.count() == 3

    def test_horizontal_with_widgets(self, qtbot: QtBot) -> None:
        """Test horizontal layout with widgets."""
        from PySide6.QtWidgets import QLabel, QWidget

        widget = QWidget()
        layout = FlexLayout(direction=Direction.HORIZONTAL)
        widget.setLayout(layout)
        qtbot.addWidget(widget)

        label1 = QLabel("Label 1")
        label2 = QLabel("Label 2")

        layout.addWidget(label1)
        layout.addWidget(label2)

        assert layout.count() == 2

    def test_vertical_with_widgets(self, qtbot: QtBot) -> None:
        """Test vertical layout with widgets."""
        from PySide6.QtWidgets import QLabel, QWidget

        widget = QWidget()
        layout = FlexLayout(direction=Direction.VERTICAL)
        widget.setLayout(layout)
        qtbot.addWidget(widget)

        label1 = QLabel("Label 1")
        label2 = QLabel("Label 2")

        layout.addWidget(label1)
        layout.addWidget(label2)

        assert layout.count() == 2
