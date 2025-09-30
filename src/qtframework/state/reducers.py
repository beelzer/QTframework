"""Reducer functions for state management."""

from __future__ import annotations

import copy
from collections.abc import Callable
from typing import Any, TypeVar

from qtframework.state.actions import Action


State = TypeVar("State", bound=dict)
Reducer = Callable[[State, Action], State]


def combine_reducers(reducers: dict[str, Reducer]) -> Reducer:
    """Combine multiple reducers into one.

    Args:
        reducers: Dictionary of reducers

    Returns:
        Combined reducer function
    """

    def combined_reducer(state: dict[str, Any], action: Action) -> dict[str, Any]:
        next_state = {}
        has_changed = False

        for key, reducer in reducers.items():
            previous_state_for_key = state.get(key, {})
            next_state_for_key = reducer(previous_state_for_key, action)
            next_state[key] = next_state_for_key
            has_changed = has_changed or next_state_for_key != previous_state_for_key

        return next_state if has_changed else state

    return combined_reducer


def create_reducer(
    initial_state: State,
    handlers: dict[str, Callable[[State, Action], State]],
) -> Reducer:
    """Create a reducer with handlers.

    Args:
        initial_state: Initial state
        handlers: Dictionary of action handlers

    Returns:
        Reducer function
    """

    def reducer(state: State | None, action: Action) -> State:
        if state is None:
            state = copy.deepcopy(initial_state)

        handler = handlers.get(action.type if isinstance(action.type, str) else action.type.value)
        if handler:
            return handler(state, action)

        return state

    return reducer


class ReducerBuilder:
    """Builder for creating reducers."""

    def __init__(self, initial_state: dict[str, Any] | None = None) -> None:
        """Initialize reducer builder.

        Args:
            initial_state: Initial state
        """
        self._initial_state = initial_state or {}
        self._handlers: dict[str, Callable] = {}

    def handle(
        self, action_type: str
    ) -> Callable[[Callable[[State, Action], State]], ReducerBuilder]:
        """Add handler for action type.

        Args:
            action_type: Action type to handle

        Returns:
            Decorator function
        """

        def decorator(handler: Callable[[State, Action], State]) -> ReducerBuilder:
            self._handlers[action_type] = handler
            return self

        return decorator

    def build(self) -> Reducer:
        """Build the reducer.

        Returns:
            Reducer function
        """
        return create_reducer(self._initial_state, self._handlers)


def immutable_update(state: dict[str, Any], path: str, value: Any) -> dict[str, Any]:
    """Immutably update nested state.

    Args:
        state: Current state
        path: Dot-separated path (e.g., "user.profile.name")
        value: New value to set at the path

    Returns:
        A deep copy of the state with the update applied. Original state is unchanged.
    """
    keys = path.split(".")
    new_state = copy.deepcopy(state)

    current = new_state
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    current[keys[-1]] = value
    return new_state


def immutable_delete(state: dict[str, Any], path: str) -> dict[str, Any]:
    """Immutably delete from nested state.

    Args:
        state: Current state
        path: Dot-separated path to the key to delete

    Returns:
        A deep copy of the state with the key removed. Original state is unchanged.
        Returns unmodified copy if path doesn't exist.
    """
    keys = path.split(".")
    new_state = copy.deepcopy(state)

    current = new_state
    for key in keys[:-1]:
        if key not in current:
            return new_state
        current = current[key]

    if keys[-1] in current:
        del current[keys[-1]]

    return new_state


def create_slice_reducer(
    slice_name: str,
    initial_state: Any,
    reducers: dict[str, Callable[[Any, Any], Any]],
) -> tuple[Reducer, dict[str, Callable[..., Action]]]:
    """Create a slice reducer with action creators.

    Args:
        slice_name: Name of the slice
        initial_state: Initial state for slice
        reducers: Reducer functions

    Returns:
        Tuple of (reducer, action_creators)
    """
    action_creators = {}

    def slice_reducer(state: Any | None = None, action: Action = Action(type="")) -> Any:
        if state is None:
            state = initial_state
        action_type_str = str(action.type)
        if not action_type_str.startswith(f"{slice_name}/"):
            return state

        action_name = action_type_str[len(f"{slice_name}/") :]
        if action_name in reducers:
            return reducers[action_name](state, action.payload)

        return state

    for action_name in reducers:
        action_type = f"{slice_name}/{action_name}"

        def make_action_creator(act_type: str) -> Callable[..., Action]:
            def action_creator(payload: Any = None) -> Action:
                return Action(type=act_type, payload=payload)

            return action_creator

        action_creators[action_name] = make_action_creator(action_type)

    return slice_reducer, action_creators
