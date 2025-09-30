"""Redux-like state store implementation.

This module provides a centralized state management system based on Redux patterns,
featuring unidirectional data flow, pure reducers, and middleware support.

Example:
    Basic store usage with reducer::

        from qtframework.state import Store, Action, create_reducer

        # Define initial state
        initial_state = {"count": 0, "user": None}


        # Create reducer
        def counter_reducer(state, action):
            if action.type == "INCREMENT":
                return {**state, "count": state["count"] + 1}
            elif action.type == "DECREMENT":
                return {**state, "count": state["count"] - 1}
            elif action.type == "SET_USER":
                return {**state, "user": action.payload}
            return state


        # Create store
        store = Store(reducer=counter_reducer, initial_state=initial_state)


        # Subscribe to changes
        def on_change(state):
            print(f"Count: {state['count']}")


        unsubscribe = store.subscribe(on_change)

        # Dispatch actions
        store.dispatch(Action(type="INCREMENT"))  # Output: Count: 1
        store.dispatch(Action(type="INCREMENT"))  # Output: Count: 2

        # Unsubscribe when done
        unsubscribe()

    With middleware::

        from qtframework.state import logger_middleware, thunk_middleware

        store = Store(
            reducer=counter_reducer,
            initial_state=initial_state,
            middleware=[logger_middleware(), thunk_middleware()],
        )

        # Middleware processes actions before they reach the reducer
        store.dispatch(Action(type="INCREMENT"))
        # Logger middleware will log the action and state changes

    Combining reducers::

        from qtframework.state import combine_reducers


        def user_reducer(state=None, action=None):
            if action.type == "SET_USER":
                return action.payload
            elif action.type == "LOGOUT":
                return None
            return state


        def items_reducer(state=None, action=None):
            if state is None:
                state = []
            if action.type == "ADD_ITEM":
                return [*state, action.payload]
            elif action.type == "REMOVE_ITEM":
                return [item for item in state if item["id"] != action.payload]
            return state


        root_reducer = combine_reducers({
            "user": user_reducer,
            "items": items_reducer,
            "count": counter_reducer,
        })

        store = Store(
            reducer=root_reducer, initial_state={"user": None, "items": [], "count": 0}
        )

See Also:
    - :class:`Action`: Action objects for dispatching
    - :mod:`qtframework.state.middleware`: Middleware implementations
    - :mod:`qtframework.state.reducers`: Reducer utilities
"""

from __future__ import annotations

import collections
import copy
import threading
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, Signal

from qtframework.state.actions import Action
from qtframework.utils.logger import get_logger


if TYPE_CHECKING:
    from qtframework.state.middleware import Middleware
    from qtframework.state.reducers import Reducer


logger = get_logger(__name__)


class Store(QObject):
    """Centralized state store with Redux-like pattern.

    The Store holds the application state and provides methods to:
    - Dispatch actions to modify state
    - Subscribe to state changes
    - Access current state (read-only)
    - Navigate state history (time-travel debugging)

    Signals:
        state_changed(dict): Emitted when state changes
        action_dispatched(dict): Emitted when action is dispatched

    Example:
        Creating and using a store::

            store = Store(reducer=my_reducer, initial_state={"count": 0})

            # Subscribe to changes
            store.state_changed.connect(lambda state: print(state))

            # Dispatch actions
            store.dispatch(Action(type="INCREMENT"))
    """

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
            reducer: Root reducer function that transforms state
            initial_state: Initial state dictionary (default: empty dict)
            middleware: List of middleware to process actions

        Raises:
            TypeError: If reducer is not callable or middleware entries are not callable
        """
        super().__init__()
        self._reducer = reducer
        self._state = initial_state or {}
        self._middleware = middleware or []
        self._subscribers: list[collections.abc.Callable[[dict[str, Any]], None]] = []
        self._lock = threading.RLock()  # Reentrant lock for thread-safe operations
        self._is_dispatching = False
        self._history: list[dict[str, Any]] = []
        self._history_index = -1
        self._max_history = 100

        if not callable(reducer):
            raise TypeError("Reducer must be callable")
        for mw in self._middleware:
            if not callable(mw):
                raise TypeError("Middleware entries must be callable")

        # Initialize state
        self._state = self._reducer(self._state, Action(type="@@INIT"))
        self._save_to_history()

    @property
    def state(self) -> dict[str, Any]:
        """Get current state (read-only copy)."""
        with self._lock:
            return copy.deepcopy(self._state)

    def get_state(self) -> dict[str, Any]:
        """Get current state.

        Returns:
            Copy of current state
        """
        return self.state

    def dispatch(self, action: Action | dict[str, Any]) -> Action:
        """Dispatch an action to update state.

        Actions are processed through middleware (if any) before reaching
        the reducer. The reducer creates a new state, which triggers
        subscriber notifications.

        Args:
            action: Action to dispatch (Action object or dict with type/payload)

        Returns:
            Dispatched action (converted to Action if dict was provided)

        Raises:
            RuntimeError: If dispatch is called while already dispatching
                (prevents nested dispatches which can cause race conditions)
            TypeError: If action cannot be converted to Action

        Example::

            # Dispatch with Action object
            store.dispatch(Action(type="INCREMENT"))

            # Dispatch with dict
            store.dispatch({"type": "SET_USER", "payload": {"id": 1}})
        """
        if isinstance(action, dict):
            action = Action(**action)

        logger.debug(f"Dispatching action: {action.type}")

        # Apply middleware
        dispatch_func: collections.abc.Callable[[Action], Action] = self._dispatch_core
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
        with self._lock:
            if self._is_dispatching:
                raise RuntimeError("Cannot dispatch while reducing")

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

    def subscribe(
        self, callback: collections.abc.Callable[[dict[str, Any]], None]
    ) -> collections.abc.Callable[[], None]:
        """Subscribe to state changes.

        Args:
            callback: Callback function

        Returns:
            Unsubscribe function
        """
        with self._lock:
            self._subscribers.append(callback)

        def unsubscribe() -> None:
            with self._lock:
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
                logger.exception("Subscriber error: %s", e)

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
        with self._lock:
            self._middleware.append(middleware)

    def remove_middleware(self, middleware: Middleware) -> bool:
        """Remove middleware from the store.

        Args:
            middleware: Middleware to remove

        Returns:
            True if middleware was found and removed, False otherwise
        """
        with self._lock:
            try:
                self._middleware.remove(middleware)
                return True
            except ValueError:
                return False

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
        with self._lock:
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
        with self._lock:
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
        with self._lock:
            self._state = state or {}
            self._state = self._reducer(self._state, Action(type="@@RESET"))
            self._history = [copy.deepcopy(self._state)]
            self._history_index = 0
            self.state_changed.emit(self.state)
            self._notify_subscribers()

    def get_history(self) -> list[dict[str, Any]]:
        """Get state history for time-travel debugging.

        Returns:
            Deep copy of all historical states (up to 100 states)

        Note:
            Returns a deep copy of history to prevent external modifications.
            For large state objects, this may be memory-intensive. History is
            automatically limited to the last 100 states (configurable via _max_history).

        Example::

            # Get and display history
            history = store.get_history()
            for i, state in enumerate(history):
                print(f"State {i}: {state}")
        """
        return copy.deepcopy(self._history)

    def select(self, selector: collections.abc.Callable[[dict[str, Any]], Any]) -> Any:
        """Select a value from state.

        Args:
            selector: Selector function

        Returns:
            Selected value
        """
        with self._lock:
            return selector(self._state)

    def select_path(self, path: str) -> Any:
        """Select value by path (e.g., 'user.profile.name').

        Args:
            path: Dot-separated path

        Returns:
            Value at path or None
        """
        with self._lock:
            keys = path.split(".")
            value = self._state

            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None

            return value
