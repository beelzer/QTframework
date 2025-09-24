"""Action definitions for state management."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ActionType(Enum):
    """Common action types."""

    INIT = "@@INIT"
    RESET = "@@RESET"
    REPLACE = "@@REPLACE"
    UPDATE = "UPDATE"
    SET = "SET"
    DELETE = "DELETE"
    CLEAR = "CLEAR"
    BATCH = "BATCH"


@dataclass
class Action:
    """Redux-style action."""

    type: str | ActionType
    payload: Any = None
    meta: dict[str, Any] = field(default_factory=dict)
    error: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert action to dictionary.

        Returns:
            Action as dictionary
        """
        action_type = self.type.value if isinstance(self.type, ActionType) else self.type
        return {
            "type": action_type,
            "payload": self.payload,
            "meta": self.meta,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Action:
        """Create action from dictionary.

        Args:
            data: Action dictionary

        Returns:
            Action instance
        """
        return cls(
            type=data.get("type", ""),
            payload=data.get("payload"),
            meta=data.get("meta", {}),
            error=data.get("error", False),
        )


class AsyncAction(Action):
    """Async action with promise support."""

    def __init__(
        self,
        type: str | ActionType,
        payload: Any = None,
        meta: dict[str, Any] | None = None,
        promise: Any = None,
    ) -> None:
        """Initialize async action.

        Args:
            type: Action type
            payload: Action payload
            meta: Action metadata
            promise: Promise or future
        """
        super().__init__(type, payload, meta or {})
        self.promise = promise


def create_action(
    action_type: str | ActionType,
    payload: Any = None,
    **meta: Any,
) -> Action:
    """Helper to create an action.

    Args:
        action_type: Action type
        payload: Action payload
        **meta: Additional metadata

    Returns:
        Action instance
    """
    return Action(type=action_type, payload=payload, meta=meta)


def create_async_action(
    action_type: str | ActionType,
    promise: Any,
    payload: Any = None,
    **meta: Any,
) -> AsyncAction:
    """Helper to create an async action.

    Args:
        action_type: Action type
        promise: Promise or future
        payload: Action payload
        **meta: Additional metadata

    Returns:
        AsyncAction instance
    """
    return AsyncAction(type=action_type, payload=payload, meta=meta, promise=promise)


class ActionCreator:
    """Factory for creating typed actions."""

    def __init__(self, namespace: str = "") -> None:
        """Initialize action creator.

        Args:
            namespace: Action namespace
        """
        self.namespace = namespace

    def create(self, action_type: str, payload: Any = None, **meta: Any) -> Action:
        """Create an action with namespace.

        Args:
            action_type: Action type
            payload: Action payload
            **meta: Additional metadata

        Returns:
            Action instance
        """
        full_type = f"{self.namespace}/{action_type}" if self.namespace else action_type
        return create_action(full_type, payload, **meta)

    def update(self, path: str, value: Any) -> Action:
        """Create update action.

        Args:
            path: State path
            value: New value

        Returns:
            Update action
        """
        return self.create("UPDATE", {"path": path, "value": value})

    def set(self, data: dict[str, Any]) -> Action:
        """Create set action.

        Args:
            data: Data to set

        Returns:
            Set action
        """
        return self.create("SET", data)

    def delete(self, path: str) -> Action:
        """Create delete action.

        Args:
            path: Path to delete

        Returns:
            Delete action
        """
        return self.create("DELETE", path)

    def batch(self, actions: list[Action]) -> Action:
        """Create batch action.

        Args:
            actions: List of actions to batch

        Returns:
            Batch action
        """
        return self.create("BATCH", actions)
