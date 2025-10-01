"""Middleware for state store."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from qtframework.state.actions import Action, AsyncAction
from qtframework.utils.logger import get_logger


if TYPE_CHECKING:
    from qtframework.state.store import Store

logger = get_logger(__name__)

Middleware = Callable[["Store"], Callable[[Callable], Callable[[Action], Action]]]


def logger_middleware() -> Middleware:
    """Middleware that logs all actions."""

    def middleware(store: Store) -> Callable[[Callable], Callable[[Action], Action]]:
        """Create middleware with access to store.

        Args:
            store: The Redux store instance

        Returns:
            Middleware wrapper function
        """

        def next_wrapper(next_dispatch: Callable) -> Callable:
            """Wrap the next dispatch function.

            Args:
                next_dispatch: The next dispatch function in the chain

            Returns:
                Enhanced dispatch function
            """

            def dispatch(action: Action) -> Action:
                """Dispatch action with logging.

                Args:
                    action: The action to dispatch

                Returns:
                    The dispatched action
                """
                logger.debug(f"Action: {action.type}")
                logger.debug(f"Payload: {action.payload}")
                result: Action = next_dispatch(action)
                logger.debug(f"New state: {store.get_state()}")
                return result

            return dispatch

        return next_wrapper

    return middleware


def thunk_middleware() -> Middleware:
    """Middleware for handling thunk actions (functions).

    Allows dispatching functions that receive dispatch and getState as arguments,
    enabling async action creators and complex logic before dispatching actions.
    """

    def middleware(store: Store) -> Callable[[Callable], Callable[[Action], Action]]:
        """Create middleware with access to store.

        Args:
            store: The Redux store instance

        Returns:
            Middleware wrapper function
        """

        def next_wrapper(next_dispatch: Callable) -> Callable:
            """Wrap the next dispatch function.

            Args:
                next_dispatch: The next dispatch function in the chain

            Returns:
                Enhanced dispatch function
            """

            def dispatch(action: Action | Callable) -> Any:
                """Dispatch action or execute thunk function.

                Args:
                    action: Action object or thunk function to execute

                Returns:
                    Result of thunk execution or dispatched action
                """
                if callable(action) and not isinstance(action, Action):
                    return action(store.dispatch, store.get_state)
                return next_dispatch(action)

            return dispatch

        return next_wrapper

    return middleware


def promise_middleware() -> Middleware:
    """Middleware for handling promise-based async actions.

    Automatically dispatches PENDING, SUCCESS, and ERROR actions for AsyncAction
    instances with promises, following the Redux async action pattern.
    """

    def middleware(store: Store) -> Callable[[Callable], Callable[[Action], Action]]:
        """Create middleware with access to store.

        Args:
            store: The Redux store instance

        Returns:
            Middleware wrapper function
        """

        def next_wrapper(next_dispatch: Callable) -> Callable:
            """Wrap the next dispatch function.

            Args:
                next_dispatch: The next dispatch function in the chain

            Returns:
                Enhanced dispatch function
            """

            def dispatch(action: Action) -> Action:
                """Dispatch async action with promise handling.

                Args:
                    action: The action to dispatch

                Returns:
                    The dispatched action
                """
                if isinstance(action, AsyncAction) and action.promise:
                    next_dispatch(
                        Action(
                            type=f"{action.type}_PENDING",
                            payload=action.payload,
                            meta=action.meta,
                        )
                    )

                    def on_success(result: Any) -> None:
                        """Handle promise success.

                        Args:
                            result: The promise result
                        """
                        next_dispatch(
                            Action(
                                type=f"{action.type}_SUCCESS",
                                payload=result,
                                meta=action.meta,
                            )
                        )

                    def on_error(error: Any) -> None:
                        """Handle promise error.

                        Args:
                            error: The error that occurred
                        """
                        next_dispatch(
                            Action(
                                type=f"{action.type}_ERROR",
                                payload=error,
                                meta=action.meta,
                                error=True,
                            )
                        )

                    if hasattr(action.promise, "then"):
                        action.promise.then(on_success).catch(on_error)

                    return action

                return next_dispatch(action)  # type: ignore[no-any-return]

            return dispatch

        return next_wrapper

    return middleware


def timing_middleware() -> Middleware:
    """Middleware that measures action processing time.

    Logs the execution time of each action dispatch in milliseconds,
    useful for performance monitoring and optimization.
    """

    def middleware(store: Store) -> Callable[[Callable], Callable[[Action], Action]]:
        """Create middleware with access to store.

        Args:
            store: The Redux store instance

        Returns:
            Middleware wrapper function
        """

        def next_wrapper(next_dispatch: Callable) -> Callable:
            """Wrap the next dispatch function.

            Args:
                next_dispatch: The next dispatch function in the chain

            Returns:
                Enhanced dispatch function
            """

            def dispatch(action: Action) -> Action:
                """Dispatch action with timing measurement.

                Args:
                    action: The action to dispatch

                Returns:
                    The dispatched action
                """
                start_time = time.perf_counter()
                result = next_dispatch(action)
                elapsed = (time.perf_counter() - start_time) * 1000
                logger.debug(f"Action {action.type} took {elapsed:.2f}ms")
                return result  # type: ignore[no-any-return]

            return dispatch

        return next_wrapper

    return middleware


def crash_reporter_middleware() -> Middleware:
    """Middleware that reports crashes and dispatches error actions.

    Catches exceptions during action processing, logs them, and dispatches
    an ERROR_OCCURRED action before re-raising the exception.
    """

    def middleware(store: Store) -> Callable[[Callable], Callable[[Action], Action]]:
        """Create middleware with access to store.

        Args:
            store: The Redux store instance

        Returns:
            Middleware wrapper function
        """

        def next_wrapper(next_dispatch: Callable) -> Callable:
            """Wrap the next dispatch function.

            Args:
                next_dispatch: The next dispatch function in the chain

            Returns:
                Enhanced dispatch function
            """

            def dispatch(action: Action) -> Action:
                """Dispatch action with error handling.

                Args:
                    action: The action to dispatch

                Returns:
                    The dispatched action

                Raises:
                    Exception: Re-raises any exception that occurs during dispatch
                """
                try:
                    return next_dispatch(action)  # type: ignore[no-any-return]
                except Exception as e:
                    logger.exception(f"Action {action.type} caused error: {e}")
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
    """Middleware that validates actions before dispatching.

    Args:
        validators: Dictionary mapping action types to validation functions

    Returns:
        Middleware function
    """

    def middleware(store: Store) -> Callable[[Callable], Callable[[Action], Action]]:
        """Create middleware with access to store.

        Args:
            store: The Redux store instance

        Returns:
            Middleware wrapper function
        """

        def next_wrapper(next_dispatch: Callable) -> Callable:
            """Wrap the next dispatch function.

            Args:
                next_dispatch: The next dispatch function in the chain

            Returns:
                Enhanced dispatch function
            """

            def dispatch(action: Action) -> Action:
                """Dispatch action with validation.

                Args:
                    action: The action to validate and dispatch

                Returns:
                    The dispatched action, or the original action if validation fails
                """
                action_type = action.type if isinstance(action.type, str) else action.type.value
                validator = validators.get(action_type)

                if validator and not validator(action):
                    logger.warning("Action %s failed validation", action_type)
                    return action

                return next_dispatch(action)  # type: ignore[no-any-return]

            return dispatch

        return next_wrapper

    return middleware


def devtools_middleware() -> Middleware:
    """Middleware for Redux DevTools integration.

    Note: DevTools connection not yet implemented. Currently captures
    state snapshots but doesn't transmit to external devtools.
    """

    def middleware(store: Store) -> Callable[[Callable], Callable[[Action], Action]]:
        """Create middleware with access to store.

        Args:
            store: The Redux store instance

        Returns:
            Middleware wrapper function
        """

        def next_wrapper(next_dispatch: Callable) -> Callable:
            """Wrap the next dispatch function.

            Args:
                next_dispatch: The next dispatch function in the chain

            Returns:
                Enhanced dispatch function
            """

            def dispatch(action: Action) -> Action:
                """Dispatch action with state snapshot capture.

                Args:
                    action: The action to dispatch

                Returns:
                    The dispatched action
                """
                prev_state = store.get_state()
                result = next_dispatch(action)
                next_state = store.get_state()

                # DevTools integration pending - data structure prepared for future use
                {
                    "action": action.to_dict(),
                    "prevState": prev_state,
                    "nextState": next_state,
                    "timestamp": time.time(),
                }

                return result  # type: ignore[no-any-return]

            return dispatch

        return next_wrapper

    return middleware
