"""State management system for Qt Framework.

This module provides a Redux-inspired state management system for Qt applications,
offering predictable state updates through actions, reducers, and middleware.

Redux-Style Architecture:
    The state system follows Redux principles::

        Application State (single source of truth)
              ↓
        Actions (describe what happened)
              ↓
        Middleware (intercept, log, async operations)
              ↓
        Reducers (pure functions that update state)
              ↓
        New State → UI Updates (via signals)

Usage Patterns:
    Basic store setup and usage::

        from qtframework.state import Store, Action, Reducer, combine_reducers

        # Define state shape
        initial_state = {
            "user": {"name": "", "authenticated": False},
            "settings": {"theme": "light", "language": "en"},
        }


        # Create reducers
        def user_reducer(state, action):
            if action.type == "USER_LOGIN":
                return {**state, "name": action.payload["name"], "authenticated": True}
            elif action.type == "USER_LOGOUT":
                return {"name": "", "authenticated": False}
            return state


        def settings_reducer(state, action):
            if action.type == "SET_THEME":
                return {**state, "theme": action.payload}
            return state


        # Combine reducers
        root_reducer = combine_reducers({
            "user": user_reducer,
            "settings": settings_reducer,
        })

        # Create store
        store = Store(root_reducer, initial_state)


        # Subscribe to state changes
        def on_state_change(state):
            print(f"State updated: {state}")


        store.subscribe(on_state_change)

        # Dispatch actions
        store.dispatch(Action("USER_LOGIN", {"name": "John Doe"}))
        store.dispatch(Action("SET_THEME", "dark"))

    Using middleware for logging::

        from qtframework.state import Middleware


        class LoggingMiddleware(Middleware):
            def process(self, store, action, next_middleware):
                print(f"Dispatching: {action.type}")
                result = next_middleware(store, action)
                print(f"New state: {store.get_state()}")
                return result


        store.add_middleware(LoggingMiddleware())

    Async operations with middleware::

        class AsyncMiddleware(Middleware):
            def process(self, store, action, next_middleware):
                if action.type == "FETCH_DATA":
                    # Start async operation
                    self.fetch_data_async(store, action.payload)
                    return None
                return next_middleware(store, action)

            def fetch_data_async(self, store, url):
                # Async operation that dispatches when complete
                data = fetch_from_api(url)
                store.dispatch(Action("DATA_LOADED", data))

Key Concepts:
    - **Store**: Central state container with dispatch and subscribe
    - **Actions**: Plain objects describing state changes
    - **Reducers**: Pure functions (state, action) -> new state
    - **Middleware**: Intercepts actions for logging, async ops, etc.
    - **Immutability**: State is never mutated, only replaced

Comparison with Redux:
    ============  ===============  ====================
    Redux         Qt Framework     Notes
    ============  ===============  ====================
    store         Store            Same concept
    action        Action           Dataclass vs dict
    reducer       Reducer          Function type alias
    middleware    Middleware       Class-based
    subscribe     subscribe()      Returns unsubscribe fn
    dispatch      dispatch()       Sync by default
    ============  ===============  ====================

See Also:
    :class:`Store`: Main state container
    :class:`Action`: Action definition
    :class:`Reducer`: Reducer type alias
    :class:`Middleware`: Middleware base class
"""

from __future__ import annotations

from qtframework.state.actions import Action, ActionType
from qtframework.state.middleware import Middleware
from qtframework.state.reducers import Reducer, combine_reducers
from qtframework.state.store import Store


__all__ = [
    "Action",
    "ActionType",
    "Middleware",
    "Reducer",
    "Store",
    "combine_reducers",
]
