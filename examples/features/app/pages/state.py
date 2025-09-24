"""
State management demonstration page.
"""

import json

from PySide6.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QPushButton,
                               QTextEdit, QVBoxLayout)

from .base import DemoPage


class StatePage(DemoPage):
    """Page demonstrating state management."""

    def __init__(self, parent_window=None):
        """Initialize the state page."""
        super().__init__("State Management")
        self.parent_window = parent_window
        self.counter = 0
        self.history = []
        self._create_content()

    def _create_content(self):
        """Create the page content."""
        # Current state display
        state_group = self._create_state_display()
        self.add_section("", state_group)

        # State controls
        controls_group = self._create_state_controls()
        self.add_section("", controls_group)

        # Action history
        history_group = self._create_action_history()
        self.add_section("", history_group)

        self.add_stretch()

        # Initialize display
        self._update_displays()

    def _create_state_display(self):
        """Create state display section."""
        group = QGroupBox("Current State")
        layout = QVBoxLayout()

        self.state_display = QTextEdit()
        self.state_display.setReadOnly(True)
        self.state_display.setMaximumHeight(150)
        layout.addWidget(self.state_display)

        group.setLayout(layout)
        return group

    def _create_state_controls(self):
        """Create state control buttons."""
        group = QGroupBox("State Actions")
        layout = QVBoxLayout()

        # Counter controls
        counter_layout = QHBoxLayout()
        counter_layout.addWidget(QLabel("Counter:"))

        increment_btn = QPushButton("Increment (+1)")
        increment_btn.clicked.connect(self._increment)
        counter_layout.addWidget(increment_btn)

        decrement_btn = QPushButton("Decrement (-1)")
        decrement_btn.clicked.connect(self._decrement)
        counter_layout.addWidget(decrement_btn)

        add5_btn = QPushButton("Add 5")
        add5_btn.clicked.connect(lambda: self._add_value(5))
        counter_layout.addWidget(add5_btn)

        counter_layout.addStretch()
        layout.addLayout(counter_layout)

        # State management controls
        mgmt_layout = QHBoxLayout()
        mgmt_layout.addWidget(QLabel("Management:"))

        reset_btn = QPushButton("Reset State")
        reset_btn.setProperty("variant", "warning")
        reset_btn.clicked.connect(self._reset_state)
        mgmt_layout.addWidget(reset_btn)

        clear_history_btn = QPushButton("Clear History")
        clear_history_btn.clicked.connect(self._clear_history)
        mgmt_layout.addWidget(clear_history_btn)

        mgmt_layout.addStretch()
        layout.addLayout(mgmt_layout)

        group.setLayout(layout)
        return group

    def _create_action_history(self):
        """Create action history display."""
        group = QGroupBox("Action History")
        layout = QVBoxLayout()

        self.history_display = QTextEdit()
        self.history_display.setReadOnly(True)
        self.history_display.setMaximumHeight(100)
        layout.addWidget(self.history_display)

        group.setLayout(layout)
        return group

    def _increment(self):
        """Increment the counter."""
        self._dispatch_action("INCREMENT", 1)
        self.counter += 1

        # Update store if available
        if self.parent_window and hasattr(self.parent_window, 'state_store'):
            from qtframework.state import Action
            self.parent_window.state_store.dispatch(Action(type="INCREMENT"))

        self._update_displays()

    def _decrement(self):
        """Decrement the counter."""
        self._dispatch_action("DECREMENT", 1)
        self.counter -= 1

        # Update store if available
        if self.parent_window and hasattr(self.parent_window, 'state_store'):
            from qtframework.state import Action
            self.parent_window.state_store.dispatch(Action(type="DECREMENT"))

        self._update_displays()

    def _add_value(self, value: int):
        """Add a specific value to counter."""
        self._dispatch_action("ADD", value)
        self.counter += value

        # Update store if available
        if self.parent_window and hasattr(self.parent_window, 'state_store'):
            from qtframework.state import Action
            self.parent_window.state_store.dispatch(
                Action(type="SET_COUNTER", payload=self.counter)
            )

        self._update_displays()

    def _reset_state(self):
        """Reset the state."""
        self._dispatch_action("RESET", None)
        self.counter = 0

        # Update store if available
        if self.parent_window and hasattr(self.parent_window, 'state_store'):
            from qtframework.state import Action
            self.parent_window.state_store.dispatch(Action(type="RESET"))

        self._update_displays()

    def _clear_history(self):
        """Clear action history."""
        self.history = []
        self._update_displays()

    def _dispatch_action(self, action_type: str, value):
        """Dispatch an action and record it."""
        action = {
            "type": action_type,
            "value": value,
            "timestamp": QDateTime.currentDateTime().toString("hh:mm:ss")
        }
        self.history.append(action)

        # Keep only last 10 actions
        if len(self.history) > 10:
            self.history.pop(0)

    def _update_displays(self):
        """Update all display widgets."""
        # Update state display
        state = {
            "counter": self.counter,
            "lastAction": self.history[-1] if self.history else None,
            "historyLength": len(self.history)
        }

        # Use the parent window's state store if available
        if self.parent_window and hasattr(self.parent_window, 'state_store'):
            state.update(self.parent_window.state_store.get_state())

        self.state_display.setText(json.dumps(state, indent=2))

        # Update history display
        history_text = "\n".join([
            f"[{action['timestamp']}] {action['type']}" +
            (f"({action['value']})" if action['value'] is not None else "")
            for action in self.history
        ])
        self.history_display.setText(history_text or "No actions yet")


# Import QDateTime for timestamps
from PySide6.QtCore import QDateTime
