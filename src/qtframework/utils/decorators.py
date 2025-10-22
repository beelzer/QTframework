"""Decorators for common patterns in Qt applications.

Provides reusable decorators for:
- Error handling and logging
- Retry logic
- Performance monitoring
- Deprecation warnings
"""

from __future__ import annotations

import functools
import time
from typing import TYPE_CHECKING, Any, TypeVar, cast


if TYPE_CHECKING:
    from collections.abc import Callable

from qtframework.utils.logger import get_logger


logger = get_logger(__name__)

T = TypeVar("T")


def with_error_logging(
    operation_name: str | None = None,
    default_return: Any = None,
    log_level: str = "error",
    reraise: bool = False,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to handle and log errors consistently.

    Args:
        operation_name: Name of the operation for logging (defaults to function name)
        default_return: Value to return on error (default: None)
        log_level: Log level to use (error, warning, debug)
        reraise: Whether to reraise the exception after logging

    Returns:
        Decorated function with error handling

    Example:
        @with_error_logging("fetch data", default_return=[])
        def fetch_data():
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            op_name = operation_name or func.__name__
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_func = getattr(logger, log_level, logger.error)
                log_func(f"{op_name} failed: {e}")
                if reraise:
                    raise
                return cast("T", default_return)

        return wrapper

    return decorator


def with_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to retry a function on failure.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function with retry logic

    Example:
        @with_retry(max_attempts=3, delay=0.5)
        def fetch_url(url):
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.debug(
                            f"{func.__name__} attempt {attempt}/{max_attempts} failed: {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.warning(f"{func.__name__} failed after {max_attempts} attempts: {e}")

            # All attempts failed
            assert last_exception is not None, "No exception was raised during retry attempts"
            raise last_exception

        return wrapper

    return decorator


def with_timing(log_threshold_ms: float = 100.0) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to log slow operations.

    Args:
        log_threshold_ms: Only log if operation takes longer than this (milliseconds)

    Returns:
        Decorated function with timing

    Example:
        @with_timing(log_threshold_ms=500)
        def slow_operation():
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            start_time = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                if elapsed_ms > log_threshold_ms:
                    logger.debug(f"{func.__name__} took {elapsed_ms:.1f}ms")

        return wrapper

    return decorator


def deprecated(message: str = "") -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to mark functions as deprecated.

    Args:
        message: Optional deprecation message

    Returns:
        Decorated function that logs deprecation warning

    Example:
        @deprecated("Use new_function() instead")
        def old_function():
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            warning = f"{func.__name__} is deprecated"
            if message:
                warning += f": {message}"
            logger.warning(warning)
            return func(*args, **kwargs)

        return wrapper

    return decorator
