"""Middleware for state store."""

from __future__ import annotations

import time
from typing import Any, Callable

from qtframework.state.actions import Action, AsyncAction
from qtframework.utils.logger import get_logger

logger = get_logger(__name__)

Middleware = Callable[["Store"], Callable[[Callable], Callable[[Action], Action]]]


def logger_middleware() -> Middleware:
    """Middleware that logs all actions."""

    def middleware(store: Any) -> Callable:
        def next_wrapper(next_dispatch: Callable) -> Callable:
            def dispatch(action: Action) -> Action:
                logger.debug(f"Action: {action.type}")
                logger.debug(f"Payload: {action.payload}")
                result = next_dispatch(action)
                logger.debug(f"New state: {store.get_state()}")
                return result

            return dispatch

        return next_wrapper

    return middleware


def thunk_middleware() -> Middleware:
    """Middleware for handling thunk actions (functions)."""

    def middleware(store: Any) -> Callable:
        def next_wrapper(next_dispatch: Callable) -> Callable:
            def dispatch(action: Action | Callable) -> Any:
                if callable(action) and not isinstance(action, Action):
                    return action(store.dispatch, store.get_state)
                return next_dispatch(action)

            return dispatch

        return next_wrapper

    return middleware


def promise_middleware() -> Middleware:
    """Middleware for handling promise-based async actions."""

    def middleware(store: Any) -> Callable:
        def next_wrapper(next_dispatch: Callable) -> Callable:
            def dispatch(action: Action) -> Action:
                if isinstance(action, AsyncAction) and action.promise:
                    # Dispatch pending action
                    next_dispatch(
                        Action(
                            type=f"{action.type}_PENDING",
                            payload=action.payload,
                            meta=action.meta,
                        )
                    )

                    # Handle promise
                    def on_success(result: Any) -> None:
                        next_dispatch(
                            Action(
                                type=f"{action.type}_SUCCESS",
                                payload=result,
                                meta=action.meta,
                            )
                        )

                    def on_error(error: Any) -> None:
                        next_dispatch(
                            Action(
                                type=f"{action.type}_ERROR",
                                payload=error,
                                meta=action.meta,
                                error=True,
                            )
                        )

                    # Assuming promise has then/catch methods
                    if hasattr(action.promise, "then"):
                        action.promise.then(on_success).catch(on_error)

                    return action

                return next_dispatch(action)

            return dispatch

        return next_wrapper

    return middleware


def timing_middleware() -> Middleware:
    """Middleware that measures action processing time."""

    def middleware(store: Any) -> Callable:
        def next_wrapper(next_dispatch: Callable) -> Callable:
            def dispatch(action: Action) -> Action:
                start_time = time.perf_counter()
                result = next_dispatch(action)
                elapsed = (time.perf_counter() - start_time) * 1000
                logger.debug(f"Action {action.type} took {elapsed:.2f}ms")
                return result

            return dispatch

        return next_wrapper

    return middleware


def crash_reporter_middleware() -> Middleware:
    """Middleware that reports crashes."""

    def middleware(store: Any) -> Callable:
        def next_wrapper(next_dispatch: Callable) -> Callable:
            def dispatch(action: Action) -> Action:
                try:
                    return next_dispatch(action)
                except Exception as e:
                    logger.error(f"Action {action.type} caused error: {e}")
                    # Dispatch error action
                    next_dispatch(
                        Action(
                            type="ERROR_OCCURRED",
                            payload={"action": action.type, "error": str(e)},
                            error=True,
                        )
                    )
                    raise

            return dispatch

        return next_wrapper

    return middleware


def validation_middleware(validators: dict[str, Callable[[Action], bool]]) -> Middleware:
    """Middleware that validates actions.

    Args:
        validators: Dictionary of action validators

    Returns:
        Middleware function
    """

    def middleware(store: Any) -> Callable:
        def next_wrapper(next_dispatch: Callable) -> Callable:
            def dispatch(action: Action) -> Action:
                action_type = action.type if isinstance(action.type, str) else action.type.value
                validator = validators.get(action_type)

                if validator and not validator(action):
                    logger.warning(f"Action {action_type} failed validation")
                    return action

                return next_dispatch(action)

            return dispatch

        return next_wrapper

    return middleware


def devtools_middleware() -> Middleware:
    """Middleware for Redux DevTools integration."""

    def middleware(store: Any) -> Callable:
        def next_wrapper(next_dispatch: Callable) -> Callable:
            def dispatch(action: Action) -> Action:
                # Before action
                prev_state = store.get_state()

                # Process action
                result = next_dispatch(action)

                # After action
                next_state = store.get_state()

                # Send to devtools (if integrated)
                # This would connect to browser devtools or standalone app
                devtools_data = {
                    "action": action.to_dict(),
                    "prevState": prev_state,
                    "nextState": next_state,
                    "timestamp": time.time(),
                }
                # TODO: Send devtools_data to devtools connection

                return result

            return dispatch

        return next_wrapper

    return middleware