# State Management Guide

Qt Framework includes a Redux-inspired state management system for predictable application state handling. This guide covers actions, reducers, middleware, and the store.

## Overview

The state management system follows these principles:

1. **Single Source of Truth** - Application state lives in a single store
2. **State is Read-Only** - State can only be changed by dispatching actions
3. **Changes via Pure Functions** - Reducers are pure functions that transform state
4. **Middleware for Side Effects** - Async operations and side effects handled by middleware

## Quick Start

### Basic Setup

```python
from qtframework.state import Store, create_action, create_reducer

# Define initial state
initial_state = {
    "counter": 0,
    "user": None,
    "items": []
}

# Create actions
increment = create_action("INCREMENT")
decrement = create_action("DECREMENT")
set_user = create_action("SET_USER")

# Create reducer
def counter_reducer(state, action):
    if action.type == "INCREMENT":
        return {**state, "counter": state["counter"] + 1}
    elif action.type == "DECREMENT":
        return {**state, "counter": state["counter"] - 1}
    elif action.type == "SET_USER":
        return {**state, "user": action.payload}
    return state

# Create store
store = Store(initial_state, counter_reducer)

# Dispatch actions
store.dispatch(increment())
store.dispatch(increment())
print(store.get_state()["counter"])  # 2

store.dispatch(set_user({"name": "Alice", "id": 1}))
print(store.get_state()["user"])  # {"name": "Alice", "id": 1}
```

## Actions

Actions are payloads of information that send data to your store.

### Creating Actions

```python
from qtframework.state import Action, create_action

# Simple action
logout = create_action("LOGOUT")
store.dispatch(logout())

# Action with payload
add_item = create_action("ADD_ITEM")
store.dispatch(add_item({"id": 1, "name": "Item 1"}))

# Action with multiple parameters
update_user = create_action("UPDATE_USER")
store.dispatch(update_user({
    "id": 1,
    "name": "Alice",
    "email": "alice@example.com"
}))
```

### Action Creators

For complex actions, create action creator functions:

```python
def fetch_user_success(user_data):
    return Action(
        type="FETCH_USER_SUCCESS",
        payload=user_data,
        meta={"timestamp": time.time()}
    )

def fetch_user_error(error):
    return Action(
        type="FETCH_USER_ERROR",
        payload=error,
        error=True
    )
```

### Async Actions

For async operations, use middleware (see Middleware section):

```python
async def fetch_user(user_id):
    return Action(
        type="FETCH_USER",
        payload=user_id,
        meta={"async": True}
    )
```

## Reducers

Reducers specify how the application's state changes in response to actions.

### Basic Reducer

```python
def app_reducer(state, action):
    """Main application reducer."""
    if action.type == "SET_THEME":
        return {**state, "theme": action.payload}

    elif action.type == "SET_LANGUAGE":
        return {**state, "language": action.payload}

    elif action.type == "TOGGLE_SIDEBAR":
        return {**state, "sidebar_open": not state.get("sidebar_open", True)}

    return state
```

### Combining Reducers

Split your reducer into smaller functions:

```python
from qtframework.state import combine_reducers

def user_reducer(state, action):
    """Handle user-related state."""
    if action.type == "SET_USER":
        return action.payload
    elif action.type == "LOGOUT":
        return None
    return state

def items_reducer(state, action):
    """Handle items list."""
    if action.type == "ADD_ITEM":
        return [*state, action.payload]
    elif action.type == "REMOVE_ITEM":
        return [item for item in state if item["id"] != action.payload]
    elif action.type == "CLEAR_ITEMS":
        return []
    return state

def settings_reducer(state, action):
    """Handle application settings."""
    if action.type == "UPDATE_SETTING":
        return {**state, **action.payload}
    return state

# Combine into root reducer
root_reducer = combine_reducers({
    "user": user_reducer,
    "items": items_reducer,
    "settings": settings_reducer
})

# Initial state must match structure
initial_state = {
    "user": None,
    "items": [],
    "settings": {
        "theme": "light",
        "language": "en",
        "notifications": True
    }
}

store = Store(initial_state, root_reducer)
```

### Immutable Updates

Always return new state objects, never mutate:

```python
# ❌ BAD - Mutates state
def bad_reducer(state, action):
    if action.type == "ADD_ITEM":
        state["items"].append(action.payload)  # Mutates!
        return state

# ✅ GOOD - Returns new state
def good_reducer(state, action):
    if action.type == "ADD_ITEM":
        return {
            **state,
            "items": [*state["items"], action.payload]
        }
    return state
```

## Store

The store holds your application state.

### Creating a Store

```python
from qtframework.state import Store

store = Store(
    initial_state=initial_state,
    reducer=root_reducer,
    middleware=[logger_middleware, async_middleware]
)
```

### Store API

```python
# Get current state
current_state = store.get_state()

# Dispatch an action
store.dispatch(add_item({"id": 1, "name": "Item"}))

# Subscribe to state changes
def on_state_change(state):
    print(f"State updated: {state}")

unsubscribe = store.subscribe(on_state_change)

# Unsubscribe when done
unsubscribe()

# Replace the reducer (useful for code splitting)
store.replace_reducer(new_reducer)
```

## Middleware

Middleware provides extension points for custom behavior.

### Logger Middleware

```python
from qtframework.state import Middleware

class LoggerMiddleware(Middleware):
    """Logs all actions and state changes."""

    def process(self, store, action, next_dispatch):
        print(f"Dispatching: {action.type}")
        print(f"Payload: {action.payload}")

        # Call next middleware or reducer
        result = next_dispatch(store, action)

        print(f"New state: {store.get_state()}")
        return result
```

### Async Middleware

Handle async operations:

```python
import asyncio
from qtframework.state import Middleware, Action

class AsyncMiddleware(Middleware):
    """Handle async actions."""

    def process(self, store, action, next_dispatch):
        if not action.meta or not action.meta.get("async"):
            return next_dispatch(store, action)

        # Handle async action
        async def run_async():
            try:
                # Dispatch loading action
                store.dispatch(Action(
                    type=f"{action.type}_LOADING",
                    payload=True
                ))

                # Perform async operation (mock example)
                await asyncio.sleep(1)
                result = {"data": "fetched"}

                # Dispatch success action
                store.dispatch(Action(
                    type=f"{action.type}_SUCCESS",
                    payload=result
                ))

            except Exception as e:
                # Dispatch error action
                store.dispatch(Action(
                    type=f"{action.type}_ERROR",
                    payload=str(e),
                    error=True
                ))

        # Run async task
        asyncio.create_task(run_async())
        return action
```

### Applying Middleware

```python
store = Store(
    initial_state=initial_state,
    reducer=root_reducer,
    middleware=[
        LoggerMiddleware(),
        AsyncMiddleware(),
        # ... other middleware
    ]
)
```

## Connecting to UI

### Subscribe to State in Widgets

```python
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton

class CounterWidget(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store

        # UI
        self.label = QLabel("0")
        self.inc_btn = QPushButton("+")
        self.dec_btn = QPushButton("-")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.inc_btn)
        layout.addWidget(self.dec_btn)
        self.setLayout(layout)

        # Connect buttons
        self.inc_btn.clicked.connect(lambda: store.dispatch(increment()))
        self.dec_btn.clicked.connect(lambda: store.dispatch(decrement()))

        # Subscribe to state
        self.store.subscribe(self.on_state_change)
        self.on_state_change(store.get_state())

    def on_state_change(self, state):
        """Update UI when state changes."""
        self.label.setText(str(state["counter"]))
```

### Selective Subscriptions

Only update when specific state changes:

```python
class UserWidget(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.previous_user = None

        self.label = QLabel()
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        store.subscribe(self.on_state_change)
        self.on_state_change(store.get_state())

    def on_state_change(self, state):
        """Only update if user changed."""
        user = state.get("user")
        if user != self.previous_user:
            self.previous_user = user
            if user:
                self.label.setText(f"Hello, {user['name']}!")
            else:
                self.label.setText("Not logged in")
```

## Complete Example

```python
from qtframework.core import Application
from qtframework.state import Store, Action, Middleware, combine_reducers
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

# Actions
increment = lambda: Action("INCREMENT")
decrement = lambda: Action("DECREMENT")
reset = lambda: Action("RESET")

# Reducers
def counter_reducer(state=0, action=None):
    if action.type == "INCREMENT":
        return state + 1
    elif action.type == "DECREMENT":
        return state - 1
    elif action.type == "RESET":
        return 0
    return state

def history_reducer(state=None, action=None):
    if state is None:
        state = []
    return [*state, action.type]

root_reducer = combine_reducers({
    "counter": counter_reducer,
    "history": history_reducer
})

# Middleware
class LoggerMiddleware(Middleware):
    def process(self, store, action, next_dispatch):
        print(f"Action: {action.type}")
        return next_dispatch(store, action)

# Create store
initial_state = {"counter": 0, "history": []}
store = Store(
    initial_state,
    root_reducer,
    middleware=[LoggerMiddleware()]
)

# UI
class CounterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.counter_label = QLabel("0")
        self.history_label = QLabel("")

        inc_btn = QPushButton("Increment")
        dec_btn = QPushButton("Decrement")
        reset_btn = QPushButton("Reset")

        inc_btn.clicked.connect(lambda: store.dispatch(increment()))
        dec_btn.clicked.connect(lambda: store.dispatch(decrement()))
        reset_btn.clicked.connect(lambda: store.dispatch(reset()))

        layout = QVBoxLayout()
        layout.addWidget(self.counter_label)
        layout.addWidget(inc_btn)
        layout.addWidget(dec_btn)
        layout.addWidget(reset_btn)
        layout.addWidget(self.history_label)
        self.setLayout(layout)

        store.subscribe(self.update_ui)
        self.update_ui(store.get_state())

    def update_ui(self, state):
        self.counter_label.setText(f"Counter: {state['counter']}")
        self.history_label.setText(f"History: {', '.join(state['history'][-5:])}")

# Run app
app = Application()
window = CounterApp()
window.show()
app.exec()
```

## Best Practices

1. **Keep Reducers Pure** - No side effects, API calls, or random values
2. **Normalize State** - Store data in normalized form (keyed by ID)
3. **Use Action Creators** - Encapsulate action creation logic
4. **Middleware for Side Effects** - Use middleware for async operations
5. **Selective Updates** - Only update UI when relevant state changes
6. **Single Store** - Use one store per application
7. **Immutable Updates** - Never mutate state directly

## Debugging

### DevTools Integration

```python
from qtframework.state import DevToolsMiddleware

store = Store(
    initial_state,
    root_reducer,
    middleware=[DevToolsMiddleware()]
)
```

### State Inspection

```python
# Print current state
print(store.get_state())

# Log all state changes
store.subscribe(lambda state: print(f"State: {state}"))
```
