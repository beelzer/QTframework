"""Animations demonstration page."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSlider,
    QVBoxLayout,
)

from qtframework.widgets import ScrollablePage as DemoPage


class AnimationsPage(DemoPage):
    """Page demonstrating animations and transitions."""

    def __init__(self, animation_type: str = "transitions"):
        """Initialize the animations page."""
        self.animation_type = animation_type
        titles = {
            "transitions": "Transitions",
            "progress": "Animated Progress",
            "effects": "Visual Effects",
        }
        super().__init__(titles.get(animation_type, "Animations"))
        self._init_timers()
        self._create_content()

    def _init_timers(self):
        """Initialize animation timers."""
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._update_progress)
        self.progress_value = 0

        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self._pulse_effect)
        self.pulse_direction = 1

    def _create_content(self):
        """Create content based on animation type."""
        if self.animation_type == "transitions":
            self._create_transitions()
        elif self.animation_type == "progress":
            self._create_progress_animations()
        elif self.animation_type == "effects":
            self._create_visual_effects()

        self.add_stretch()

    def _create_transitions(self):
        """Create transition animations."""
        # Fade transitions
        fade_group = QGroupBox("Fade Transitions")
        fade_layout = QVBoxLayout()

        self.fade_label = QLabel("This element can fade in and out")
        self.fade_label.setAlignment(Qt.AlignCenter)
        self.fade_label.setStyleSheet(
            "background-color: #e0e0e0; padding: 20px; border-radius: 4px;"
        )
        fade_layout.addWidget(self.fade_label)

        fade_controls = QHBoxLayout()
        fade_in_btn = QPushButton("Fade In")
        fade_in_btn.clicked.connect(self._fade_in)
        fade_controls.addWidget(fade_in_btn)

        fade_out_btn = QPushButton("Fade Out")
        fade_out_btn.clicked.connect(self._fade_out)
        fade_controls.addWidget(fade_out_btn)

        fade_controls.addStretch()
        fade_layout.addLayout(fade_controls)

        fade_group.setLayout(fade_layout)
        self.content_layout.addWidget(fade_group)

        # Slide transitions
        slide_group = QGroupBox("Slide Transitions")
        slide_layout = QVBoxLayout()

        self.slide_frame = QFrame()
        self.slide_frame.setStyleSheet(
            "background-color: #007bff; min-height: 50px; border-radius: 4px;"
        )
        slide_layout.addWidget(self.slide_frame)

        slide_controls = QHBoxLayout()
        slide_left_btn = QPushButton("Slide Left")
        slide_left_btn.clicked.connect(self._slide_left)
        slide_controls.addWidget(slide_left_btn)

        slide_right_btn = QPushButton("Slide Right")
        slide_right_btn.clicked.connect(self._slide_right)
        slide_controls.addWidget(slide_right_btn)

        slide_controls.addStretch()
        slide_layout.addLayout(slide_controls)

        slide_group.setLayout(slide_layout)
        self.content_layout.addWidget(slide_group)

    def _create_progress_animations(self):
        """Create animated progress bars."""
        # Linear progress
        linear_group = QGroupBox("Linear Progress Animation")
        linear_layout = QVBoxLayout()

        self.linear_progress = QProgressBar()
        self.linear_progress.setRange(0, 100)
        linear_layout.addWidget(self.linear_progress)

        linear_controls = QHBoxLayout()

        start_btn = QPushButton("Start")
        start_btn.clicked.connect(lambda: self.progress_timer.start(50))
        linear_controls.addWidget(start_btn)

        stop_btn = QPushButton("Stop")
        stop_btn.clicked.connect(self.progress_timer.stop)
        linear_controls.addWidget(stop_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self._reset_progress)
        linear_controls.addWidget(reset_btn)

        linear_controls.addStretch()
        linear_layout.addLayout(linear_controls)

        linear_group.setLayout(linear_layout)
        self.content_layout.addWidget(linear_group)

        # Circular simulation (using progress bar)
        circular_group = QGroupBox("Continuous Animation")
        circular_layout = QVBoxLayout()

        self.continuous_progress = QProgressBar()
        self.continuous_progress.setRange(0, 0)  # Indeterminate
        circular_layout.addWidget(self.continuous_progress)

        circular_group.setLayout(circular_layout)
        self.content_layout.addWidget(circular_group)

        # Speed control
        speed_group = QGroupBox("Animation Speed Control")
        speed_layout = QHBoxLayout()

        speed_layout.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(10, 200)
        self.speed_slider.setValue(50)
        self.speed_slider.valueChanged.connect(self._update_speed)
        speed_layout.addWidget(self.speed_slider)

        self.speed_label = QLabel("50ms")
        speed_layout.addWidget(self.speed_label)

        speed_layout.addStretch()
        speed_group.setLayout(speed_layout)
        self.content_layout.addWidget(speed_group)

    def _create_visual_effects(self):
        """Create visual effect animations."""
        # Pulse effect
        pulse_group = QGroupBox("Pulse Effect")
        pulse_layout = QVBoxLayout()

        self.pulse_frame = QFrame()
        self.pulse_frame.setFixedSize(100, 100)
        self.pulse_frame.setStyleSheet("background-color: #28a745; border-radius: 50px;")
        pulse_layout.addWidget(self.pulse_frame, alignment=Qt.AlignCenter)

        pulse_controls = QHBoxLayout()
        pulse_start_btn = QPushButton("Start Pulse")
        pulse_start_btn.clicked.connect(lambda: self.pulse_timer.start(50))
        pulse_controls.addWidget(pulse_start_btn)

        pulse_stop_btn = QPushButton("Stop Pulse")
        pulse_stop_btn.clicked.connect(self.pulse_timer.stop)
        pulse_controls.addWidget(pulse_stop_btn)

        pulse_controls.addStretch()
        pulse_layout.addLayout(pulse_controls)

        pulse_group.setLayout(pulse_layout)
        self.content_layout.addWidget(pulse_group)

        # Rotation simulation
        rotation_group = QGroupBox("Rotation Effect")
        rotation_layout = QVBoxLayout()

        self.rotation_label = QLabel("🔄")
        self.rotation_label.setStyleSheet("font-size: 48px;")
        self.rotation_label.setAlignment(Qt.AlignCenter)
        rotation_layout.addWidget(self.rotation_label)

        rotation_controls = QHBoxLayout()
        rotate_btn = QPushButton("Rotate")
        rotate_btn.clicked.connect(self._rotate)
        rotation_controls.addWidget(rotate_btn)

        rotation_controls.addStretch()
        rotation_layout.addLayout(rotation_controls)

        rotation_group.setLayout(rotation_layout)
        self.content_layout.addWidget(rotation_group)

    def _fade_in(self):
        """Fade in animation."""
        self.fade_label.setStyleSheet(
            "background-color: #4CAF50; padding: 20px; border-radius: 4px;"
        )

    def _fade_out(self):
        """Fade out animation."""
        self.fade_label.setStyleSheet(
            "background-color: #e0e0e0; padding: 20px; border-radius: 4px;"
        )

    def _slide_left(self):
        """Slide left animation."""
        # Simple color change to simulate movement
        self.slide_frame.setStyleSheet(
            "background-color: #dc3545; min-height: 50px; border-radius: 4px;"
        )

    def _slide_right(self):
        """Slide right animation."""
        # Simple color change to simulate movement
        self.slide_frame.setStyleSheet(
            "background-color: #007bff; min-height: 50px; border-radius: 4px;"
        )

    def _update_progress(self):
        """Update animated progress bar."""
        self.progress_value = (self.progress_value + 2) % 101
        self.linear_progress.setValue(self.progress_value)

    def _reset_progress(self):
        """Reset progress animation."""
        self.progress_timer.stop()
        self.progress_value = 0
        self.linear_progress.setValue(0)

    def _update_speed(self, value):
        """Update animation speed."""
        self.speed_label.setText(f"{value}ms")
        if self.progress_timer.isActive():
            self.progress_timer.setInterval(value)

    def _pulse_effect(self):
        """Create pulse effect."""
        current_size = self.pulse_frame.width()

        if current_size >= 120:
            self.pulse_direction = -1
        elif current_size <= 80:
            self.pulse_direction = 1

        new_size = current_size + (2 * self.pulse_direction)
        self.pulse_frame.setFixedSize(new_size, new_size)

    def _rotate(self):
        """Rotate animation."""
        # Simple rotation through different Unicode arrows
        arrows = ["↑", "↗", "→", "↘", "↓", "↙", "←", "↖"]
        current = self.rotation_label.text()

        if current == "🔄":
            self.rotation_label.setText(arrows[0])
        elif current in arrows:
            idx = (arrows.index(current) + 1) % len(arrows)
            self.rotation_label.setText(arrows[idx])
        else:
            self.rotation_label.setText(arrows[0])

        self.rotation_label.setStyleSheet("font-size: 48px;")
