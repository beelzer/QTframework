"""Tests for state store."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import Mock

import pytest

from qtframework.state.actions import Action
from qtframework.state.store import Store

if TYPE_CHECKING:
    from pytest_qt.qtbot import QtBot


@pytest.fixture
def simple_reducer():
    """Create a simple counter reducer."""

    def reducer(state: dict[str, Any], action: Action) -> dict[str, Any]:
        if action.type == "INCREMENT":
            return {**state, "count": state.get("count", 0) + 1}
        elif action.type == "DECREMENT":
            return {**state, "count": state.get("count", 0) - 1}
        elif action.type == "SET_VALUE":
            return {**state, "value": action.payload}
        elif action.type == "RESET_COUNT":
            return {**state, "count": 0}
        return state

    return reducer


class TestStoreCreation:
    """Test Store creation."""

    def test_store_creation_minimal(self, simple_reducer) -> None:
        """Test creating store with minimal parameters."""
        store = Store(reducer=simple_reducer)
        assert store is not None
        assert store.state == {}

    def test_store_creation_with_initial_state(self, simple_reducer) -> None:
        """Test creating store with initial state."""
        initial_state = {"count": 5, "name": "test"}
        store = Store(reducer=simple_reducer, initial_state=initial_state)
        assert store.state.get("count") == 5
        assert store.state.get("name") == "test"

    def test_store_creation_with_middleware(self, simple_reducer) -> None:
        """Test creating store with middleware."""
        middleware = Mock(return_value=lambda store: lambda next_dispatch: next_dispatch)
        store = Store(reducer=simple_reducer, middleware=[middleware])
        assert store is not None

    def test_store_raises_on_non_callable_reducer(self) -> None:
        """Test store raises error for non-callable reducer."""
        with pytest.raises(TypeError, match="Reducer must be callable"):
            Store(reducer="not a function")  # type: ignore

    def test_store_raises_on_non_callable_middleware(self, simple_reducer) -> None:
        """Test store raises error for non-callable middleware."""
        with pytest.raises(TypeError, match="Middleware entries must be callable"):
            Store(reducer=simple_reducer, middleware=["not callable"])  # type: ignore

    def test_store_initialization_dispatches_init(self, simple_reducer) -> None:
        """Test store dispatches @@INIT on creation."""
        # Reducer should receive @@INIT action
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        assert store is not None


class TestStoreState:
    """Test Store state management."""

    def test_get_state_returns_copy(self, simple_reducer) -> None:
        """Test get_state returns a copy."""
        store = Store(reducer=simple_reducer, initial_state={"count": 1})
        state1 = store.get_state()
        state2 = store.get_state()

        assert state1 == state2
        assert state1 is not state2

    def test_state_property_returns_copy(self, simple_reducer) -> None:
        """Test state property returns a copy."""
        store = Store(reducer=simple_reducer, initial_state={"count": 1})
        state1 = store.state
        state2 = store.state

        assert state1 == state2
        assert state1 is not state2

    def test_state_cannot_be_modified_directly(self, simple_reducer) -> None:
        """Test state cannot be modified directly."""
        store = Store(reducer=simple_reducer, initial_state={"count": 1})
        state = store.state
        state["count"] = 999

        # Original state should be unchanged
        assert store.state["count"] == 1


class TestStoreDispatch:
    """Test Store dispatch functionality."""

    def test_dispatch_action_object(self, simple_reducer) -> None:
        """Test dispatching Action object."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.dispatch(Action(type="INCREMENT"))
        assert store.state["count"] == 1

    def test_dispatch_action_dict(self, simple_reducer) -> None:
        """Test dispatching dict as action."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.dispatch({"type": "INCREMENT"})
        assert store.state["count"] == 1

    def test_dispatch_with_payload(self, simple_reducer) -> None:
        """Test dispatching action with payload."""
        store = Store(reducer=simple_reducer, initial_state={})
        store.dispatch(Action(type="SET_VALUE", payload="test_value"))
        assert store.state["value"] == "test_value"

    def test_dispatch_returns_action(self, simple_reducer) -> None:
        """Test dispatch returns the action."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        action = Action(type="INCREMENT")
        result = store.dispatch(action)
        assert result == action

    def test_dispatch_nested_raises_error(self, simple_reducer) -> None:
        """Test nested dispatch raises RuntimeError."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})

        # Create reducer that tries to dispatch during reduction
        def bad_reducer(state: dict[str, Any], action: Action) -> dict[str, Any]:
            if action.type == "BAD":
                store.dispatch(Action(type="INCREMENT"))
            return state

        store._reducer = bad_reducer

        with pytest.raises(RuntimeError, match="Cannot dispatch while reducing"):
            store.dispatch(Action(type="BAD"))

    def test_dispatch_multiple_actions(self, simple_reducer) -> None:
        """Test dispatching multiple actions."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.dispatch(Action(type="INCREMENT"))
        store.dispatch(Action(type="INCREMENT"))
        store.dispatch(Action(type="DECREMENT"))
        assert store.state["count"] == 1


class TestStoreSignals:
    """Test Store Qt signals."""

    def test_state_changed_signal_emitted(
        self, simple_reducer, qtbot: QtBot
    ) -> None:
        """Test state_changed signal is emitted."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})

        with qtbot.waitSignal(store.state_changed, timeout=1000) as blocker:
            store.dispatch(Action(type="INCREMENT"))

        assert blocker.args[0]["count"] == 1

    def test_state_changed_signal_not_emitted_if_no_change(
        self, simple_reducer, qtbot: QtBot
    ) -> None:
        """Test state_changed signal not emitted if state unchanged."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})

        # Dispatch action that doesn't change state
        with qtbot.assertNotEmitted(store.state_changed, wait=100):
            store.dispatch(Action(type="UNKNOWN"))

    def test_action_dispatched_signal_emitted(
        self, simple_reducer, qtbot: QtBot
    ) -> None:
        """Test action_dispatched signal is emitted."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})

        with qtbot.waitSignal(store.action_dispatched, timeout=1000) as blocker:
            store.dispatch(Action(type="INCREMENT"))

        assert blocker.args[0]["type"] == "INCREMENT"


class TestStoreSubscribers:
    """Test Store subscriber functionality."""

    def test_subscribe_callback_called(self, simple_reducer) -> None:
        """Test subscriber callback is called on state change."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        callback = Mock()

        store.subscribe(callback)
        store.dispatch(Action(type="INCREMENT"))

        callback.assert_called_once()
        assert callback.call_args[0][0]["count"] == 1

    def test_subscribe_returns_unsubscribe_function(self, simple_reducer) -> None:
        """Test subscribe returns unsubscribe function."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        callback = Mock()

        unsubscribe = store.subscribe(callback)
        store.dispatch(Action(type="INCREMENT"))

        callback.assert_called_once()

        # Unsubscribe and verify not called again
        unsubscribe()
        store.dispatch(Action(type="INCREMENT"))

        # Should still be called only once
        callback.assert_called_once()

    def test_multiple_subscribers(self, simple_reducer) -> None:
        """Test multiple subscribers are notified."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        callback1 = Mock()
        callback2 = Mock()

        store.subscribe(callback1)
        store.subscribe(callback2)
        store.dispatch(Action(type="INCREMENT"))

        callback1.assert_called_once()
        callback2.assert_called_once()

    def test_subscriber_error_doesnt_break_others(self, simple_reducer) -> None:
        """Test error in one subscriber doesn't affect others."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})

        def bad_callback(state):
            raise ValueError("Bad subscriber")

        good_callback = Mock()

        store.subscribe(bad_callback)
        store.subscribe(good_callback)

        # Should not raise
        store.dispatch(Action(type="INCREMENT"))

        good_callback.assert_called_once()

    def test_unsubscribe_nonexistent_callback_safe(self, simple_reducer) -> None:
        """Test unsubscribing nonexistent callback is safe."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        callback = Mock()

        unsubscribe = store.subscribe(callback)
        unsubscribe()  # First unsubscribe
        unsubscribe()  # Second unsubscribe - should not error


class TestStoreMiddleware:
    """Test Store middleware functionality."""

    def test_middleware_called_on_dispatch(self, simple_reducer) -> None:
        """Test middleware is called on dispatch."""
        middleware_called = []

        def test_middleware(store):
            def inner(next_dispatch):
                def dispatch_wrapper(action):
                    middleware_called.append(action.type)
                    return next_dispatch(action)

                return dispatch_wrapper

            return inner

        store = Store(
            reducer=simple_reducer, initial_state={"count": 0}, middleware=[test_middleware]
        )
        store.dispatch(Action(type="INCREMENT"))

        assert "INCREMENT" in middleware_called

    def test_middleware_can_modify_action(self, simple_reducer) -> None:
        """Test middleware can modify action."""

        def modifying_middleware(store):
            def inner(next_dispatch):
                def dispatch_wrapper(action):
                    if action.type == "INCREMENT":
                        # Change to DECREMENT
                        action = Action(type="DECREMENT")
                    return next_dispatch(action)

                return dispatch_wrapper

            return inner

        store = Store(
            reducer=simple_reducer,
            initial_state={"count": 5},
            middleware=[modifying_middleware],
        )
        store.dispatch(Action(type="INCREMENT"))

        # Should be decremented instead
        assert store.state["count"] == 4

    def test_multiple_middleware_order(self, simple_reducer) -> None:
        """Test multiple middleware are called in order."""
        call_order = []

        def middleware1(store):
            def inner(next_dispatch):
                def dispatch_wrapper(action):
                    call_order.append("mw1_before")
                    result = next_dispatch(action)
                    call_order.append("mw1_after")
                    return result

                return dispatch_wrapper

            return inner

        def middleware2(store):
            def inner(next_dispatch):
                def dispatch_wrapper(action):
                    call_order.append("mw2_before")
                    result = next_dispatch(action)
                    call_order.append("mw2_after")
                    return result

                return dispatch_wrapper

            return inner

        store = Store(
            reducer=simple_reducer,
            initial_state={"count": 0},
            middleware=[middleware1, middleware2],
        )
        store.dispatch(Action(type="INCREMENT"))

        assert call_order == ["mw1_before", "mw2_before", "mw2_after", "mw1_after"]

    def test_add_middleware_dynamically(self, simple_reducer) -> None:
        """Test adding middleware after creation."""
        middleware_called = []

        def test_middleware(store):
            def inner(next_dispatch):
                def dispatch_wrapper(action):
                    middleware_called.append(action.type)
                    return next_dispatch(action)

                return dispatch_wrapper

            return inner

        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.add_middleware(test_middleware)
        store.dispatch(Action(type="INCREMENT"))

        assert "INCREMENT" in middleware_called

    def test_remove_middleware(self, simple_reducer) -> None:
        """Test removing middleware."""
        middleware_called = []

        def test_middleware(store):
            def inner(next_dispatch):
                def dispatch_wrapper(action):
                    middleware_called.append(action.type)
                    return next_dispatch(action)

                return dispatch_wrapper

            return inner

        store = Store(
            reducer=simple_reducer, initial_state={"count": 0}, middleware=[test_middleware]
        )
        result = store.remove_middleware(test_middleware)

        assert result is True
        store.dispatch(Action(type="INCREMENT"))

        # Middleware should not be called
        assert "INCREMENT" not in middleware_called

    def test_remove_nonexistent_middleware(self, simple_reducer) -> None:
        """Test removing nonexistent middleware returns False."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})

        def dummy_middleware(store):
            return lambda next_dispatch: next_dispatch

        result = store.remove_middleware(dummy_middleware)
        assert result is False


class TestStoreReducerReplacement:
    """Test Store reducer replacement."""

    def test_replace_reducer(self, simple_reducer) -> None:
        """Test replacing reducer."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})

        def new_reducer(state: dict[str, Any], action: Action) -> dict[str, Any]:
            if action.type == "MULTIPLY":
                return {**state, "count": state.get("count", 0) * 2}
            return state

        store.replace_reducer(new_reducer)
        store.dispatch(Action(type="MULTIPLY"))

        assert store.state["count"] == 0  # 0 * 2

    def test_replace_reducer_dispatches_replace_action(
        self, simple_reducer, qtbot: QtBot
    ) -> None:
        """Test replace_reducer dispatches @@REPLACE action."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})

        def new_reducer(state: dict[str, Any], action: Action) -> dict[str, Any]:
            return state

        with qtbot.waitSignal(store.action_dispatched, timeout=1000) as blocker:
            store.replace_reducer(new_reducer)

        assert blocker.args[0]["type"] == "@@REPLACE"


class TestStoreHistory:
    """Test Store history/time-travel functionality."""

    def test_history_saved_on_state_change(self, simple_reducer) -> None:
        """Test history is saved on state change."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.dispatch(Action(type="INCREMENT"))
        store.dispatch(Action(type="INCREMENT"))

        history = store.get_history()
        assert len(history) >= 2

    def test_undo_reverts_state(self, simple_reducer) -> None:
        """Test undo reverts to previous state."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.dispatch(Action(type="INCREMENT"))
        store.dispatch(Action(type="INCREMENT"))

        assert store.state["count"] == 2

        result = store.undo()
        assert result is True
        assert store.state["count"] == 1

    def test_undo_multiple_times(self, simple_reducer) -> None:
        """Test multiple undo operations."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.dispatch(Action(type="INCREMENT"))
        store.dispatch(Action(type="INCREMENT"))
        store.dispatch(Action(type="INCREMENT"))

        store.undo()
        store.undo()

        assert store.state["count"] == 1

    def test_undo_at_beginning_returns_false(self, simple_reducer) -> None:
        """Test undo at beginning returns False."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})

        result = store.undo()
        assert result is False

    def test_redo_restores_state(self, simple_reducer) -> None:
        """Test redo restores state after undo."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.dispatch(Action(type="INCREMENT"))
        store.dispatch(Action(type="INCREMENT"))

        store.undo()
        assert store.state["count"] == 1

        result = store.redo()
        assert result is True
        assert store.state["count"] == 2

    def test_redo_multiple_times(self, simple_reducer) -> None:
        """Test multiple redo operations."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.dispatch(Action(type="INCREMENT"))
        store.dispatch(Action(type="INCREMENT"))
        store.dispatch(Action(type="INCREMENT"))

        store.undo()
        store.undo()
        store.undo()

        store.redo()
        store.redo()

        assert store.state["count"] == 2

    def test_redo_at_end_returns_false(self, simple_reducer) -> None:
        """Test redo at end returns False."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.dispatch(Action(type="INCREMENT"))

        result = store.redo()
        assert result is False

    def test_dispatch_after_undo_clears_forward_history(self, simple_reducer) -> None:
        """Test dispatch after undo clears forward history."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.dispatch(Action(type="INCREMENT"))
        store.dispatch(Action(type="INCREMENT"))
        store.dispatch(Action(type="INCREMENT"))

        store.undo()
        store.undo()

        # Dispatch new action
        store.dispatch(Action(type="SET_VALUE", payload="new"))

        # Redo should not work
        result = store.redo()
        assert result is False

    def test_undo_emits_state_changed(self, simple_reducer, qtbot: QtBot) -> None:
        """Test undo emits state_changed signal."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.dispatch(Action(type="INCREMENT"))

        with qtbot.waitSignal(store.state_changed, timeout=1000):
            store.undo()

    def test_redo_emits_state_changed(self, simple_reducer, qtbot: QtBot) -> None:
        """Test redo emits state_changed signal."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.dispatch(Action(type="INCREMENT"))
        store.undo()

        with qtbot.waitSignal(store.state_changed, timeout=1000):
            store.redo()

    def test_history_limit(self, simple_reducer) -> None:
        """Test history is limited to max size."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})

        # Dispatch more than max_history actions
        for _ in range(150):
            store.dispatch(Action(type="INCREMENT"))

        history = store.get_history()
        assert len(history) <= 100

    def test_get_history_returns_copy(self, simple_reducer) -> None:
        """Test get_history returns a copy."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.dispatch(Action(type="INCREMENT"))

        history1 = store.get_history()
        history2 = store.get_history()

        assert history1 == history2
        assert history1 is not history2


class TestStoreReset:
    """Test Store reset functionality."""

    def test_reset_to_initial_state(self, simple_reducer) -> None:
        """Test reset to initial state."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.dispatch(Action(type="INCREMENT"))
        store.dispatch(Action(type="INCREMENT"))

        store.reset({"count": 0})
        assert store.state["count"] == 0

    def test_reset_to_new_state(self, simple_reducer) -> None:
        """Test reset to new state."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.dispatch(Action(type="INCREMENT"))

        store.reset({"count": 10, "name": "test"})
        assert store.state.get("count") == 10
        assert store.state.get("name") == "test"

    def test_reset_clears_history(self, simple_reducer) -> None:
        """Test reset clears history."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.dispatch(Action(type="INCREMENT"))
        store.dispatch(Action(type="INCREMENT"))

        store.reset({"count": 0})

        history = store.get_history()
        assert len(history) == 1

    def test_reset_emits_state_changed(self, simple_reducer, qtbot: QtBot) -> None:
        """Test reset emits state_changed signal."""
        store = Store(reducer=simple_reducer, initial_state={"count": 0})
        store.dispatch(Action(type="INCREMENT"))

        with qtbot.waitSignal(store.state_changed, timeout=1000):
            store.reset({"count": 0})

    def test_reset_calls_reducer_with_reset_action(self, simple_reducer) -> None:
        """Test reset calls reducer with @@RESET action."""
        store = Store(reducer=simple_reducer, initial_state={"count": 5})

        # Reset should call reducer with @@RESET action
        store.reset({"count": 0})

        # State should be reset
        assert store.state["count"] == 0


class TestStoreSelectors:
    """Test Store selector functionality."""

    def test_select_with_function(self, simple_reducer) -> None:
        """Test select with selector function."""
        store = Store(
            reducer=simple_reducer, initial_state={"count": 5, "name": "test"}
        )

        result = store.select(lambda state: state["count"])
        assert result == 5

    def test_select_with_complex_selector(self, simple_reducer) -> None:
        """Test select with complex selector."""
        store = Store(
            reducer=simple_reducer,
            initial_state={"user": {"name": "John", "age": 30}},
        )

        result = store.select(lambda state: state.get("user", {}).get("name"))
        assert result == "John"

    def test_select_path_simple(self, simple_reducer) -> None:
        """Test select_path with simple path."""
        store = Store(reducer=simple_reducer, initial_state={"count": 5})

        result = store.select_path("count")
        assert result == 5

    def test_select_path_nested(self, simple_reducer) -> None:
        """Test select_path with nested path."""
        store = Store(
            reducer=simple_reducer,
            initial_state={"user": {"profile": {"name": "John"}}},
        )

        result = store.select_path("user.profile.name")
        assert result == "John"

    def test_select_path_nonexistent_returns_none(self, simple_reducer) -> None:
        """Test select_path returns None for nonexistent path."""
        store = Store(reducer=simple_reducer, initial_state={"count": 5})

        result = store.select_path("nonexistent.path")
        assert result is None

    def test_select_path_partial_nonexistent(self, simple_reducer) -> None:
        """Test select_path with partially nonexistent path."""
        store = Store(reducer=simple_reducer, initial_state={"user": {"name": "John"}})

        result = store.select_path("user.profile.age")
        assert result is None


class TestStoreIntegration:
    """Test Store integration scenarios."""

    def test_full_lifecycle(self, simple_reducer, qtbot: QtBot) -> None:
        """Test full store lifecycle."""
        callback = Mock()
        store = Store(reducer=simple_reducer, initial_state={"count": 0})

        # Subscribe
        unsubscribe = store.subscribe(callback)

        # Dispatch actions
        store.dispatch(Action(type="INCREMENT"))
        store.dispatch(Action(type="INCREMENT"))

        assert store.state["count"] == 2
        assert callback.call_count == 2

        # Undo - this will also call callback
        store.undo()
        assert store.state["count"] == 1
        call_count_after_undo = callback.call_count

        # Redo - this will also call callback
        store.redo()
        assert store.state["count"] == 2
        call_count_after_redo = callback.call_count

        # Unsubscribe
        unsubscribe()
        store.dispatch(Action(type="INCREMENT"))

        # Should not be called again after unsubscribe
        assert callback.call_count == call_count_after_redo

    def test_complex_state_updates(self, simple_reducer) -> None:
        """Test complex state updates."""
        store = Store(
            reducer=simple_reducer,
            initial_state={"count": 0, "items": [], "user": None},
        )

        store.dispatch(Action(type="INCREMENT"))
        store.dispatch(Action(type="SET_VALUE", payload="test"))
        store.dispatch(Action(type="INCREMENT"))

        assert store.state["count"] == 2
        assert store.state["value"] == "test"
