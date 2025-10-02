"""Basic tests for state management package."""

from __future__ import annotations

from qtframework.state.actions import (
    Action,
    ActionCreator,
    ActionType,
    AsyncAction,
    create_action,
    create_async_action,
)


class TestActionType:
    """Test ActionType enum."""

    def test_action_type_values(self) -> None:
        """Test action type enum values."""
        assert ActionType.INIT.value == "@@INIT"
        assert ActionType.RESET.value == "@@RESET"
        assert ActionType.REPLACE.value == "@@REPLACE"
        assert ActionType.UPDATE.value == "UPDATE"
        assert ActionType.SET.value == "SET"
        assert ActionType.DELETE.value == "DELETE"
        assert ActionType.CLEAR.value == "CLEAR"
        assert ActionType.BATCH.value == "BATCH"


class TestAction:
    """Test Action class."""

    def test_action_creation_minimal(self) -> None:
        """Test creating action with minimal parameters."""
        action = Action(type="TEST_ACTION")
        assert action.type == "TEST_ACTION"
        assert action.payload is None
        assert action.meta == {}
        assert action.error is False

    def test_action_creation_with_payload(self) -> None:
        """Test creating action with payload."""
        action = Action(type="TEST_ACTION", payload={"key": "value"})
        assert action.type == "TEST_ACTION"
        assert action.payload == {"key": "value"}

    def test_action_creation_with_meta(self) -> None:
        """Test creating action with metadata."""
        action = Action(type="TEST_ACTION", meta={"source": "test"})
        assert action.meta == {"source": "test"}

    def test_action_creation_with_error(self) -> None:
        """Test creating error action."""
        action = Action(type="ERROR_ACTION", error=True)
        assert action.error is True

    def test_action_with_enum_type(self) -> None:
        """Test creating action with ActionType enum."""
        action = Action(type=ActionType.INIT)
        assert action.type == ActionType.INIT

    def test_action_to_dict_string_type(self) -> None:
        """Test converting action to dictionary with string type."""
        action = Action(
            type="TEST_ACTION",
            payload={"key": "value"},
            meta={"source": "test"},
            error=False,
        )
        data = action.to_dict()

        assert data["type"] == "TEST_ACTION"
        assert data["payload"] == {"key": "value"}
        assert data["meta"] == {"source": "test"}
        assert data["error"] is False

    def test_action_to_dict_enum_type(self) -> None:
        """Test converting action to dictionary with enum type."""
        action = Action(type=ActionType.INIT)
        data = action.to_dict()

        assert data["type"] == "@@INIT"

    def test_action_from_dict(self) -> None:
        """Test creating action from dictionary."""
        data = {
            "type": "TEST_ACTION",
            "payload": {"key": "value"},
            "meta": {"source": "test"},
            "error": False,
        }
        action = Action.from_dict(data)

        assert action.type == "TEST_ACTION"
        assert action.payload == {"key": "value"}
        assert action.meta == {"source": "test"}
        assert action.error is False

    def test_action_from_dict_minimal(self) -> None:
        """Test creating action from minimal dictionary."""
        data = {"type": "TEST_ACTION"}
        action = Action.from_dict(data)

        assert action.type == "TEST_ACTION"
        assert action.payload is None
        assert action.meta == {}
        assert action.error is False

    def test_action_from_dict_empty_type(self) -> None:
        """Test creating action from dictionary with missing type."""
        data: dict[str, str] = {}
        action = Action.from_dict(data)

        assert action.type == ""

    def test_action_round_trip(self) -> None:
        """Test converting action to dict and back."""
        original = Action(
            type="TEST_ACTION",
            payload={"data": 123},
            meta={"timestamp": 456},
            error=False,
        )
        data = original.to_dict()
        reconstructed = Action.from_dict(data)

        assert reconstructed.type == original.type
        assert reconstructed.payload == original.payload
        assert reconstructed.meta == original.meta
        assert reconstructed.error == original.error


class TestAsyncAction:
    """Test AsyncAction class."""

    def test_async_action_creation(self) -> None:
        """Test creating async action."""
        action = AsyncAction(type="ASYNC_ACTION")
        assert action.type == "ASYNC_ACTION"
        assert action.payload is None

    def test_async_action_with_payload(self) -> None:
        """Test creating async action with payload."""
        action = AsyncAction(type="ASYNC_ACTION", payload={"data": "value"})
        assert action.payload == {"data": "value"}

    def test_async_action_with_meta(self) -> None:
        """Test creating async action with metadata."""
        action = AsyncAction(type="ASYNC_ACTION", meta={"async": True})
        assert action.meta == {"async": True}

    def test_async_action_with_promise(self) -> None:
        """Test creating async action with promise."""
        promise = object()
        action = AsyncAction(type="ASYNC_ACTION", promise=promise)
        assert hasattr(action, "promise")

    def test_async_action_inherits_from_action(self) -> None:
        """Test that AsyncAction inherits from Action."""
        action = AsyncAction(type="ASYNC_ACTION")
        assert isinstance(action, Action)

    def test_async_action_to_dict(self) -> None:
        """Test converting async action to dictionary."""
        action = AsyncAction(
            type="ASYNC_ACTION",
            payload={"data": "value"},
            meta={"async": True},
        )
        data = action.to_dict()

        assert data["type"] == "ASYNC_ACTION"
        assert data["payload"] == {"data": "value"}
        assert data["meta"] == {"async": True}


class TestActionIntegration:
    """Test action integration scenarios."""

    def test_multiple_action_types(self) -> None:
        """Test creating multiple action types."""
        actions = [
            Action(type=ActionType.INIT),
            Action(type=ActionType.UPDATE, payload={"key": "value"}),
            Action(type=ActionType.DELETE, payload={"id": 123}),
            Action(type=ActionType.CLEAR),
        ]

        assert len(actions) == 4
        assert actions[0].type == ActionType.INIT
        assert actions[1].type == ActionType.UPDATE
        assert actions[2].type == ActionType.DELETE
        assert actions[3].type == ActionType.CLEAR

    def test_action_serialization_batch(self) -> None:
        """Test serializing multiple actions."""
        actions = [
            Action(type="ACTION_1", payload=1),
            Action(type="ACTION_2", payload=2),
            Action(type="ACTION_3", payload=3),
        ]

        serialized = [action.to_dict() for action in actions]
        assert len(serialized) == 3
        assert serialized[0]["payload"] == 1
        assert serialized[1]["payload"] == 2
        assert serialized[2]["payload"] == 3

    def test_action_deserialization_batch(self) -> None:
        """Test deserializing multiple actions."""
        data_list = [
            {"type": "ACTION_1", "payload": 1},
            {"type": "ACTION_2", "payload": 2},
            {"type": "ACTION_3", "payload": 3},
        ]

        actions = [Action.from_dict(data) for data in data_list]
        assert len(actions) == 3
        assert actions[0].payload == 1
        assert actions[1].payload == 2
        assert actions[2].payload == 3


class TestCreateAction:
    """Test create_action helper function."""

    def test_create_action_minimal(self) -> None:
        """Test creating action with minimal parameters."""
        action = create_action("TEST")
        assert action.type == "TEST"
        assert action.payload is None
        assert action.meta == {}

    def test_create_action_with_payload(self) -> None:
        """Test creating action with payload."""
        action = create_action("TEST", payload={"key": "value"})
        assert action.type == "TEST"
        assert action.payload == {"key": "value"}

    def test_create_action_with_meta(self) -> None:
        """Test creating action with metadata."""
        action = create_action("TEST", meta_key="meta_value", another="data")
        assert action.type == "TEST"
        assert action.meta["meta_key"] == "meta_value"
        assert action.meta["another"] == "data"

    def test_create_action_with_enum(self) -> None:
        """Test creating action with ActionType enum."""
        action = create_action(ActionType.UPDATE, payload=123)
        assert action.type == ActionType.UPDATE
        assert action.payload == 123


class TestCreateAsyncAction:
    """Test create_async_action helper function."""

    def test_create_async_action_minimal(self) -> None:
        """Test creating async action with minimal parameters."""
        promise = object()
        action = create_async_action("ASYNC_TEST", promise)
        assert action.type == "ASYNC_TEST"
        assert action.promise == promise
        assert action.payload is None

    def test_create_async_action_with_payload(self) -> None:
        """Test creating async action with payload."""
        promise = object()
        action = create_async_action("ASYNC_TEST", promise, payload={"data": 123})
        assert action.payload == {"data": 123}
        assert action.promise == promise

    def test_create_async_action_with_meta(self) -> None:
        """Test creating async action with metadata."""
        promise = object()
        action = create_async_action("ASYNC_TEST", promise, timeout=5000)
        assert action.meta["timeout"] == 5000
        assert action.promise == promise


class TestActionCreator:
    """Test ActionCreator factory class."""

    def test_action_creator_creation_no_namespace(self) -> None:
        """Test creating ActionCreator without namespace."""
        creator = ActionCreator()
        assert creator.namespace == ""

    def test_action_creator_creation_with_namespace(self) -> None:
        """Test creating ActionCreator with namespace."""
        creator = ActionCreator(namespace="app")
        assert creator.namespace == "app"

    def test_action_creator_create_without_namespace(self) -> None:
        """Test creating action without namespace."""
        creator = ActionCreator()
        action = creator.create("TEST", payload=123)
        assert action.type == "TEST"
        assert action.payload == 123

    def test_action_creator_create_with_namespace(self) -> None:
        """Test creating action with namespace."""
        creator = ActionCreator(namespace="user")
        action = creator.create("LOGIN", payload={"username": "test"})
        assert action.type == "user/LOGIN"
        assert action.payload == {"username": "test"}

    def test_action_creator_update(self) -> None:
        """Test ActionCreator.update method."""
        creator = ActionCreator(namespace="data")
        action = creator.update("user.name", "John")
        assert action.type == "data/UPDATE"
        assert action.payload == {"path": "user.name", "value": "John"}

    def test_action_creator_set(self) -> None:
        """Test ActionCreator.set method."""
        creator = ActionCreator(namespace="config")
        action = creator.set({"theme": "dark", "font": 12})
        assert action.type == "config/SET"
        assert action.payload == {"theme": "dark", "font": 12}

    def test_action_creator_delete(self) -> None:
        """Test ActionCreator.delete method."""
        creator = ActionCreator(namespace="items")
        action = creator.delete("items.123")
        assert action.type == "items/DELETE"
        assert action.payload == "items.123"

    def test_action_creator_batch(self) -> None:
        """Test ActionCreator.batch method."""
        creator = ActionCreator(namespace="bulk")
        actions_list = [
            Action(type="ACTION1"),
            Action(type="ACTION2"),
        ]
        action = creator.batch(actions_list)
        assert action.type == "bulk/BATCH"
        assert action.payload == actions_list
        assert len(action.payload) == 2
