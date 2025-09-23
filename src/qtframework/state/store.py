"""Redux-like state store implementation."""

from __future__ import annotations

import copy
from typing import Any, Callable

from PySide6.QtCore import QObject, Signal

from qtframework.state.actions import Action
from qtframework.state.middleware import Middleware
from qtframework.state.reducers import Reducer
from qtframework.utils.logger import get_logger

logger = get_logger(__name__)


class Store(QObject):
    """Centralized state store with Redux-like pattern."""

    state_changed = Signal(dict)
    action_dispatched = Signal(dict)

    def __init__(
        self,
        reducer: Reducer,
        initial_state: dict[str, Any] | None = None,
        middleware: list[Middleware] | None = None,
    ) -> None:
        """Initialize store.

        Args:
            reducer: Root reducer function
            initial_state: Initial state
            middleware: List of middleware
        """
        super().__init__()
        self._reducer = reducer
        self._state = initial_state or {}
        self._middleware = middleware or []
        self._subscribers: list[Callable[[dict[str, Any]], None]] = []
        self._is_dispatching = False
        self._history: list[dict[str, Any]] = []
        self._history_index = -1
        self._max_history = 100

        # Initialize state
        self._state = self._reducer(self._state, Action(type="@@INIT"))
        self._save_to_history()

    @property
    def state(self) -> dict[str, Any]:
        """Get current state (read-only copy)."""
        return copy.deepcopy(self._state)

    def get_state(self) -> dict[str, Any]:
        """Get current state.

        Returns:
            Copy of current state
        """
        return self.state

    def dispatch(self, action: Action | dict[str, Any]) -> Action:
        """Dispatch an action to update state.

        Args:
            action: Action to dispatch

        Returns:
            Dispatched action
        """
        if self._is_dispatching:
            raise RuntimeError("Cannot dispatch while reducing")

        if isinstance(action, dict):
            action = Action(**action)

        logger.debug(f"Dispatching action: {action.type}")

        # Apply middleware
        dispatch_func = self._dispatch_core
        for middleware in reversed(self._middleware):
            dispatch_func = middleware(self)(dispatch_func)

        return dispatch_func(action)

    def _dispatch_core(self, action: Action) -> Action:
        """Core dispatch logic.

        Args:
            action: Action to dispatch

        Returns:
            Dispatched action
        """
        self._is_dispatching = True

        try:
            old_state = copy.deepcopy(self._state)
            self._state = self._reducer(self._state, action)

            if self._state != old_state:
                self._save_to_history()
                self.state_changed.emit(self.state)
                self._notify_subscribers()

            self.action_dispatched.emit(action.to_dict())

        finally:
            self._is_dispatching = False

        return action

    def subscribe(self, callback: Callable[[dict[str, Any]], None]) -> Callable[[], None]:
        """Subscribe to state changes.

        Args:
            callback: Callback function

        Returns:
            Unsubscribe function
        """
        self._subscribers.append(callback)

        def unsubscribe() -> None:
            if callback in self._subscribers:
                self._subscribers.remove(callback)

        return unsubscribe

    def _notify_subscribers(self) -> None:
        """Notify all subscribers of state change."""
        state = self.state
        for subscriber in self._subscribers[:]:
            try:
                subscriber(state)
            except Exception as e:
                logger.error(f"Subscriber error: {e}")

    def replace_reducer(self, reducer: Reducer) -> None:
        """Replace the root reducer.

        Args:
            reducer: New reducer
        """
        self._reducer = reducer
        self.dispatch(Action(type="@@REPLACE"))

    def add_middleware(self, middleware: Middleware) -> None:
        """Add middleware to the store.

        Args:
            middleware: Middleware to add
        """
        self._middleware.append(middleware)

    def _save_to_history(self) -> None:
        """Save current state to history."""
        # Remove any states after current index
        self._history = self._history[: self._history_index + 1]

        # Add current state
        self._history.append(copy.deepcopy(self._state))
        self._history_index += 1

        # Limit history size
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]
            self._history_index = len(self._history) - 1

    def undo(self) -> bool:
        """Undo last state change.

        Returns:
            True if undo successful
        """
        if self._history_index > 0:
            self._history_index -= 1
            self._state = copy.deepcopy(self._history[self._history_index])
            self.state_changed.emit(self.state)
            self._notify_subscribers()
            return True
        return False

    def redo(self) -> bool:
        """Redo previously undone state change.

        Returns:
            True if redo successful
        """
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self._state = copy.deepcopy(self._history[self._history_index])
            self.state_changed.emit(self.state)
            self._notify_subscribers()
            return True
        return False

    def reset(self, state: dict[str, Any] | None = None) -> None:
        """Reset store to initial or provided state.

        Args:
            state: State to reset to
        """
        self._state = state or {}
        self._state = self._reducer(self._state, Action(type="@@RESET"))
        self._history = [copy.deepcopy(self._state)]
        self._history_index = 0
        self.state_changed.emit(self.state)
        self._notify_subscribers()

    def get_history(self) -> list[dict[str, Any]]:
        """Get state history.

        Returns:
            List of historical states
        """
        return copy.deepcopy(self._history)

    def select(self, selector: Callable[[dict[str, Any]], Any]) -> Any:
        """Select a value from state.

        Args:
            selector: Selector function

        Returns:
            Selected value
        """
        return selector(self._state)

    def select_path(self, path: str) -> Any:
        """Select value by path (e.g., 'user.profile.name').

        Args:
            path: Dot-separated path

        Returns:
            Value at path or None
        """
        keys = path.split(".")
        value = self._state

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None

        return value