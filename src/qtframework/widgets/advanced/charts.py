"""Chart widgets for data visualization."""

from __future__ import annotations

import math
from enum import Enum
from typing import Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPaintEvent
from PySide6.QtWidgets import QWidget


class ChartType(Enum):
    """Chart types."""

    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"


class ChartWidget(QWidget):
    """Base chart widget with custom painting."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize chart widget."""
        super().__init__(parent)
        self._data: list[float] = []
        self._title = ""
        self._labels: list[str] = []
        self._colors: list[QColor] | None = None  # Will be set based on theme
        self._margin = 40
        self._show_grid = True
        self._show_legend = False
        self.setMinimumSize(300, 200)

    def set_data(self, data: list[float], labels: list[str] | None = None) -> None:
        """Set chart data."""
        self._data = data
        if labels:
            self._labels = labels
        else:
            self._labels = [str(i) for i in range(len(data))]
        self.update()

    def set_title(self, title: str) -> None:
        """Set chart title."""
        self._title = title
        self.update()

    def set_colors(self, colors: list[QColor]) -> None:
        """Set custom colors."""
        self._colors = colors
        self.update()

    def set_show_grid(self, show: bool) -> None:
        """Toggle grid display."""
        self._show_grid = show
        self.update()

    def set_show_legend(self, show: bool) -> None:
        """Toggle legend display."""
        self._show_legend = show
        self.update()

    def get_color(self, index: int) -> QColor:
        """Get color for index based on current theme."""
        colors = self.get_data_colors()
        return colors[index % len(colors)]

    def is_dark_theme(self) -> bool:
        """Check if dark theme is active."""
        # Compare background luminance
        bg = self.palette().color(self.palette().ColorRole.Window)
        luminance = (0.299 * bg.red() + 0.587 * bg.green() + 0.114 * bg.blue()) / 255
        return luminance < 0.5

    def get_theme_name(self) -> str:
        """Get current theme name by analyzing colors."""
        bg = self.palette().color(self.palette().ColorRole.Window)
        # Check for monokai's specific background color
        if abs(bg.red() - 39) < 5 and abs(bg.green() - 40) < 5 and abs(bg.blue() - 34) < 5:
            return "monokai"
        elif self.is_dark_theme():
            return "dark"
        else:
            return "light"

    def get_theme_colors(self) -> dict:
        """Get colors based on current theme."""
        if self.is_dark_theme():
            return {
                'background': QColor("#2b2b2b"),
                'text': QColor("#ffffff"),
                'grid': QColor("#404040"),
                'axis': QColor("#808080"),
            }
        else:
            return {
                'background': QColor("#f8f9fa"),
                'text': QColor("#2c3e50"),
                'grid': QColor("#e0e0e0"),
                'axis': QColor("#2c3e50"),
            }

    def get_data_colors(self) -> list[QColor]:
        """Get data series colors based on current theme."""
        # Return custom colors if set
        if self._colors is not None:
            return self._colors

        theme_name = self.get_theme_name()

        if theme_name == "monokai":
            # Monokai-inspired colors
            return [
                QColor("#66d9ef"),  # Cyan (Monokai blue)
                QColor("#a6e22e"),  # Green (Monokai green)
                QColor("#fd971f"),  # Orange
                QColor("#f92672"),  # Pink/Magenta (Monokai red)
                QColor("#ae81ff"),  # Purple
                QColor("#e6db74"),  # Yellow
                QColor("#75715e"),  # Brown/Gray
                QColor("#f8f8f2"),  # Light gray
            ]
        elif theme_name == "dark":
            # Brighter, more vibrant colors for dark theme
            return [
                QColor("#5dade2"),  # Bright blue
                QColor("#58d68d"),  # Bright green
                QColor("#f5b041"),  # Bright orange
                QColor("#ec7063"),  # Bright red
                QColor("#af7ac5"),  # Bright purple
                QColor("#48c9b0"),  # Bright turquoise
                QColor("#f4d03f"),  # Bright yellow
                QColor("#85929e"),  # Light gray
            ]
        else:
            # Deeper, richer colors for light theme
            return [
                QColor("#2874a6"),  # Deep blue
                QColor("#239b56"),  # Deep green
                QColor("#d68910"),  # Deep orange
                QColor("#cb4335"),  # Deep red
                QColor("#7d3c98"),  # Deep purple
                QColor("#17a589"),  # Deep turquoise
                QColor("#d4ac0d"),  # Deep yellow
                QColor("#566573"),  # Dark gray
            ]


class LineChart(ChartWidget):
    """Line chart widget with custom painting."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize line chart."""
        super().__init__(parent)
        self._show_points = True
        self._line_width = 2

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the line chart."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()

        # Get theme colors
        theme_colors = self.get_theme_colors()

        # Draw background
        painter.fillRect(0, 0, width, height, theme_colors['background'])

        # Draw title
        if self._title:
            font = QFont("Arial", 12, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QPen(theme_colors['text'], 2))
            painter.drawText(0, 0, width, 30, Qt.AlignmentFlag.AlignCenter, self._title)

        if not self._data:
            return

        # Calculate chart area
        chart_left = self._margin
        chart_top = 40 if self._title else 20
        chart_right = width - self._margin
        chart_bottom = height - self._margin
        chart_width = chart_right - chart_left
        chart_height = chart_bottom - chart_top

        # Find min/max values
        min_val = min(self._data)
        max_val = max(self._data)
        value_range = max_val - min_val if max_val != min_val else 1

        # Draw grid
        if self._show_grid:
            painter.setPen(QPen(theme_colors['grid'], 1))
            # Horizontal grid lines
            for i in range(5):
                y = chart_top + (chart_height * i / 4)
                painter.drawLine(chart_left, int(y), chart_right, int(y))
            # Vertical grid lines
            for i, _ in enumerate(self._data):
                x = chart_left + (chart_width * i / max(1, len(self._data) - 1))
                painter.drawLine(int(x), chart_top, int(x), chart_bottom)

        # Draw axes
        painter.setPen(QPen(theme_colors['axis'], 2))
        painter.drawLine(chart_left, chart_top, chart_left, chart_bottom)  # Y-axis
        painter.drawLine(chart_left, chart_bottom, chart_right, chart_bottom)  # X-axis

        # Draw data line
        painter.setPen(QPen(self.get_color(0), self._line_width))
        points = []
        for i, value in enumerate(self._data):
            x = chart_left + (chart_width * i / max(1, len(self._data) - 1))
            y = chart_bottom - ((value - min_val) / value_range * chart_height)
            points.append(QPointF(x, y))

        # Draw line segments
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i + 1])

        # Draw points
        if self._show_points:
            painter.setBrush(QBrush(self.get_color(0)))
            for point in points:
                painter.drawEllipse(point, 4, 4)

        # Draw labels
        if self._labels:
            font = QFont("Arial", 8)
            painter.setFont(font)
            painter.setPen(QPen(theme_colors['text'], 1))
            for i, label in enumerate(self._labels[:len(self._data)]):
                x = chart_left + (chart_width * i / max(1, len(self._data) - 1))
                painter.drawText(
                    int(x - 20), chart_bottom + 5, 40, 20,
                    Qt.AlignmentFlag.AlignCenter, label
                )

        # Draw value labels on Y-axis
        painter.setPen(QPen(theme_colors['text'], 1))
        for i in range(5):
            y = chart_top + (chart_height * i / 4)
            value = max_val - (value_range * i / 4)
            painter.drawText(
                5, int(y - 10), chart_left - 10, 20,
                Qt.AlignmentFlag.AlignRight, f"{value:.1f}"
            )


class BarChart(ChartWidget):
    """Bar chart widget with custom painting."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize bar chart."""
        super().__init__(parent)
        self._bar_spacing = 0.2  # 20% spacing between bars

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the bar chart."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()

        # Get theme colors
        theme_colors = self.get_theme_colors()

        # Draw background
        painter.fillRect(0, 0, width, height, theme_colors['background'])

        # Draw title
        if self._title:
            font = QFont("Arial", 12, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QPen(theme_colors['text'], 2))
            painter.drawText(0, 0, width, 30, Qt.AlignmentFlag.AlignCenter, self._title)

        if not self._data:
            return

        # Calculate chart area
        chart_left = self._margin + 20
        chart_top = 40 if self._title else 20
        chart_right = width - self._margin
        chart_bottom = height - self._margin - 20
        chart_width = chart_right - chart_left
        chart_height = chart_bottom - chart_top

        # Find max value
        max_val = max(self._data) if self._data else 1

        # Draw grid
        if self._show_grid:
            painter.setPen(QPen(theme_colors['grid'], 1))
            # Horizontal grid lines
            for i in range(5):
                y = chart_top + (chart_height * i / 4)
                painter.drawLine(chart_left, int(y), chart_right, int(y))

        # Draw axes
        painter.setPen(QPen(theme_colors['axis'], 2))
        painter.drawLine(chart_left, chart_top, chart_left, chart_bottom)  # Y-axis
        painter.drawLine(chart_left, chart_bottom, chart_right, chart_bottom)  # X-axis

        # Draw bars
        if len(self._data) > 0:
            bar_width = chart_width / len(self._data) * (1 - self._bar_spacing)
            bar_spacing = chart_width / len(self._data) * self._bar_spacing

            for i, value in enumerate(self._data):
                x = chart_left + i * (bar_width + bar_spacing) + bar_spacing / 2
                bar_height = (value / max_val) * chart_height if max_val > 0 else 0
                y = chart_bottom - bar_height

                # Draw bar
                color = self.get_color(i)
                painter.fillRect(
                    QRectF(x, y, bar_width, bar_height),
                    QBrush(color)
                )

                # Draw value on top of bar
                font = QFont("Arial", 9)
                painter.setFont(font)
                painter.setPen(QPen(theme_colors['text'], 1))
                painter.drawText(
                    int(x), int(y - 20), int(bar_width), 20,
                    Qt.AlignmentFlag.AlignCenter, str(value)
                )

                # Draw label
                if i < len(self._labels):
                    font = QFont("Arial", 8)
                    painter.setFont(font)
                    painter.setPen(QPen(theme_colors['text'], 1))
                    painter.drawText(
                        int(x), chart_bottom + 5, int(bar_width), 30,
                        Qt.AlignmentFlag.AlignCenter, self._labels[i]
                    )

        # Draw value labels on Y-axis
        font = QFont("Arial", 8)
        painter.setFont(font)
        painter.setPen(QPen(theme_colors['text'], 1))
        for i in range(5):
            y = chart_top + (chart_height * i / 4)
            value = max_val - (max_val * i / 4)
            painter.drawText(
                5, int(y - 10), chart_left - 10, 20,
                Qt.AlignmentFlag.AlignRight, f"{value:.1f}"
            )


class PieChart(ChartWidget):
    """Pie chart widget with custom painting."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize pie chart."""
        super().__init__(parent)
        self._show_percentage = True

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the pie chart."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()

        # Get theme colors
        theme_colors = self.get_theme_colors()

        # Draw background
        painter.fillRect(0, 0, width, height, theme_colors['background'])

        # Draw title
        if self._title:
            font = QFont("Arial", 12, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QPen(theme_colors['text'], 2))
            painter.drawText(0, 0, width, 30, Qt.AlignmentFlag.AlignCenter, self._title)

        if not self._data:
            return

        # Calculate total
        total = sum(self._data)
        if total == 0:
            return

        # Calculate pie dimensions
        title_height = 40 if self._title else 20
        available_height = height - title_height - 40
        size = min(width - 100, available_height) - 40
        x = (width - size) / 2
        y = title_height + (available_height - size) / 2

        # Draw pie slices
        start_angle = 90 * 16  # Start at 12 o'clock (Qt uses 1/16 degree units)

        for i, value in enumerate(self._data):
            # Calculate angle
            percentage = value / total
            span_angle = int(percentage * 360 * 16)

            # Draw slice
            color = self.get_color(i)
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.GlobalColor.white, 2))
            painter.drawPie(QRectF(x, y, size, size), start_angle, span_angle)

            # Calculate label position (middle of slice)
            mid_angle = start_angle + span_angle / 2
            angle_rad = mid_angle / 16 * math.pi / 180
            label_radius = size / 3
            label_x = x + size / 2 + label_radius * math.cos(angle_rad)
            label_y = y + size / 2 - label_radius * math.sin(angle_rad)

            # Draw percentage label
            if self._show_percentage and percentage > 0.05:  # Only show if > 5%
                font = QFont("Arial", 9, QFont.Weight.Bold)
                painter.setFont(font)
                painter.setPen(QPen(Qt.GlobalColor.white, 1))
                label_text = f"{percentage*100:.1f}%"
                painter.drawText(
                    int(label_x - 30), int(label_y - 10), 60, 20,
                    Qt.AlignmentFlag.AlignCenter, label_text
                )

            start_angle += span_angle

        # Draw legend
        if self._labels and self._show_legend:
            font = QFont("Arial", 9)
            painter.setFont(font)
            legend_x = x + size + 20
            legend_y = y + 20

            for i, (label, value) in enumerate(zip(self._labels, self._data)):
                if i >= len(self._data):
                    break

                # Draw color box
                color = self.get_color(i)
                painter.fillRect(
                    QRectF(legend_x, legend_y + i * 25, 15, 15),
                    QBrush(color)
                )

                # Draw label
                painter.setPen(QPen(theme_colors['text'], 1))
                percentage = value / total * 100
                legend_text = f"{label}: {value} ({percentage:.1f}%)"
                painter.drawText(
                    int(legend_x + 20), int(legend_y + i * 25), 200, 20,
                    Qt.AlignmentFlag.AlignVCenter, legend_text
                )


class ScatterChart(ChartWidget):
    """Scatter chart widget with custom painting."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize scatter chart."""
        super().__init__(parent)
        self._point_size = 6
        self._data_points: list[tuple[float, float]] = []

    def set_points(self, points: list[tuple[float, float]]) -> None:
        """Set scatter plot points."""
        self._data_points = points
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the scatter chart."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()

        # Get theme colors
        theme_colors = self.get_theme_colors()

        # Draw background
        painter.fillRect(0, 0, width, height, theme_colors['background'])

        # Draw title
        if self._title:
            font = QFont("Arial", 12, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QPen(theme_colors['text'], 2))
            painter.drawText(0, 0, width, 30, Qt.AlignmentFlag.AlignCenter, self._title)

        if not self._data_points:
            return

        # Calculate chart area
        chart_left = self._margin + 20
        chart_top = 40 if self._title else 20
        chart_right = width - self._margin
        chart_bottom = height - self._margin
        chart_width = chart_right - chart_left
        chart_height = chart_bottom - chart_top

        # Find min/max values
        x_values = [p[0] for p in self._data_points]
        y_values = [p[1] for p in self._data_points]
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        x_range = x_max - x_min if x_max != x_min else 1
        y_range = y_max - y_min if y_max != y_min else 1

        # Draw grid
        if self._show_grid:
            painter.setPen(QPen(theme_colors['grid'], 1))
            # Horizontal grid lines
            for i in range(5):
                y = chart_top + (chart_height * i / 4)
                painter.drawLine(chart_left, int(y), chart_right, int(y))
            # Vertical grid lines
            for i in range(5):
                x = chart_left + (chart_width * i / 4)
                painter.drawLine(int(x), chart_top, int(x), chart_bottom)

        # Draw axes
        painter.setPen(QPen(theme_colors['axis'], 2))
        painter.drawLine(chart_left, chart_top, chart_left, chart_bottom)  # Y-axis
        painter.drawLine(chart_left, chart_bottom, chart_right, chart_bottom)  # X-axis

        # Draw points
        color = self.get_color(0)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color.darker(), 1))

        for x_val, y_val in self._data_points:
            x = chart_left + ((x_val - x_min) / x_range * chart_width)
            y = chart_bottom - ((y_val - y_min) / y_range * chart_height)
            painter.drawEllipse(QPointF(x, y), self._point_size, self._point_size)