"""Router for navigation between views."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, Signal

from qtframework.utils.logger import get_logger


if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtWidgets import QWidget


logger = get_logger(__name__)


@dataclass
class Route:
    """Route definition."""

    path: str
    component: type[QWidget] | Callable[..., QWidget]
    name: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)
    guards: list[Callable[[Route], bool]] = field(default_factory=list)
    children: list[Route] = field(default_factory=list)
    redirect: str | None = None

    def matches(self, path: str) -> tuple[bool, dict[str, str]]:
        """Check if path matches this route.

        Args:
            path: Path to check

        Returns:
            Tuple of (matches, params)
        """
        pattern = self._path_to_pattern()
        match = pattern.match(path)

        if match:
            return True, match.groupdict()
        return False, {}

    def _path_to_pattern(self) -> re.Pattern[str]:
        """Convert path to regex pattern.

        Returns:
            Compiled pattern
        """
        # Convert :param to named groups
        pattern = self.path
        pattern = re.sub(r":(\w+)", r"(?P<\1>[^/]+)", pattern)
        pattern = re.sub(r"\*", r".*", pattern)
        return re.compile(f"^{pattern}$")

    def can_activate(self) -> bool:
        """Check if route can be activated.

        Returns:
            True if all guards pass
        """
        return all(guard(self) for guard in self.guards)


class Router(QObject):
    """Application router for managing navigation."""

    route_changed = Signal(str, dict)
    navigation_blocked = Signal(str, str)

    def __init__(self, routes: list[Route] | None = None) -> None:
        """Initialize router.

        Args:
            routes: List of routes
        """
        super().__init__()
        self._routes: list[Route] = routes or []
        self._current_path: str = "/"
        self._current_route: Route | None = None
        self._history: list[str] = []
        self._future: list[str] = []
        self._route_map: dict[str, Route] = {}
        self._before_hooks: list[Callable[[str, str], bool]] = []
        self._after_hooks: list[Callable[[Route], None]] = []

        self._build_route_map()

    def _build_route_map(self) -> None:
        """Build route name map."""

        def add_to_map(route: Route, parent_path: str = "") -> None:
            full_path = parent_path + route.path
            if route.name:
                self._route_map[route.name] = route

            for child in route.children:
                add_to_map(child, full_path)

        for route in self._routes:
            add_to_map(route)

    def add_route(self, route: Route) -> None:
        """Add a route.

        Args:
            route: Route to add
        """
        self._routes.append(route)
        if route.name:
            self._route_map[route.name] = route

    def remove_route(self, path: str) -> None:
        """Remove a route.

        Args:
            path: Route path
        """
        self._routes = [r for r in self._routes if r.path != path]
        self._route_map = {n: r for n, r in self._route_map.items() if r.path != path}

    def navigate(
        self, path: str, params: dict[str, Any] | None = None, _internal: bool = False
    ) -> bool:
        """Navigate to a path.

        Args:
            path: Path to navigate to
            params: Optional parameters
            _internal: Internal flag for history navigation

        Returns:
            True if navigation successful
        """
        logger.info("Navigating to: %s", path)

        # Check before hooks
        for hook in self._before_hooks:
            if not hook(self._current_path, path):
                logger.warning("Navigation blocked by hook: %s", path)
                self.navigation_blocked.emit(self._current_path, path)
                return False

        # Find matching route
        route = self._find_route(path)
        if not route:
            logger.error("No route found for path: %s", path)
            return False

        # Check route guards
        if not route.can_activate():
            logger.warning("Route guard blocked: %s", path)
            self.navigation_blocked.emit(self._current_path, path)
            return False

        # Handle redirect
        if route.redirect:
            return self.navigate(route.redirect, params)

        # Update history only for normal navigation (not back/forward)
        if not _internal and self._current_path and self._current_path != path:
            self._history.append(self._current_path)
            self._future.clear()

        # Update current state
        self._current_path = path
        self._current_route = route

        # Merge params
        route_params = params or {}
        _, extracted_params = route.matches(path)
        route_params.update(extracted_params)

        # Emit change
        self.route_changed.emit(path, route_params)

        # After hooks
        for hook in self._after_hooks:
            hook(route)  # type: ignore[arg-type]

        return True

    def _find_route(self, path: str) -> Route | None:
        """Find route for path.

        Args:
            path: Path to find

        Returns:
            Matching route or None
        """

        def check_route(route: Route, parent_path: str = "") -> Route | None:
            full_path = parent_path + route.path
            matches, _ = route.matches(path)

            if matches:
                return route

            # Check children
            for child in route.children:
                result = check_route(child, full_path)
                if result:
                    return result

            return None

        for route in self._routes:
            result = check_route(route)
            if result:
                return result

        return None

    def navigate_by_name(self, name: str, params: dict[str, Any] | None = None) -> bool:
        """Navigate to named route.

        Args:
            name: Route name
            params: Route parameters

        Returns:
            True if navigation successful
        """
        route = self._route_map.get(name)
        if not route:
            logger.error("No route found with name: %s", name)
            return False

        # Build path from params
        path = route.path
        if params:
            for key, value in params.items():
                path = path.replace(f":{key}", str(value))

        return self.navigate(path, params)

    def back(self) -> bool:
        """Navigate back in history.

        Returns:
            True if navigation successful
        """
        if not self._history:
            return False

        # Save current path to future
        if self._current_path:
            self._future.append(self._current_path)

        # Get previous path and navigate
        path = self._history.pop()
        return self.navigate(path, _internal=True)

    def forward(self) -> bool:
        """Navigate forward in history.

        Returns:
            True if navigation successful
        """
        if not self._future:
            return False

        # Save current path to history
        if self._current_path:
            self._history.append(self._current_path)

        # Get next path and navigate
        path = self._future.pop()
        return self.navigate(path, _internal=True)

    def reload(self) -> bool:
        """Reload current route.

        Returns:
            True if reload successful
        """
        if self._current_path:
            return self.navigate(self._current_path)
        return False

    @property
    def current_path(self) -> str:
        """Get current path."""
        return self._current_path

    @property
    def current_route(self) -> Route | None:
        """Get current route."""
        return self._current_route

    def get_route_component(self) -> QWidget | None:
        """Get current route's component.

        Returns:
            Component widget or None
        """
        if not self._current_route:
            return None

        component = self._current_route.component
        if callable(component):
            return component()
        return None  # pragma: no cover

    def add_before_hook(self, hook: Callable[[str, str], bool]) -> None:
        """Add before navigation hook.

        Args:
            hook: Hook function (from_path, to_path) -> bool
        """
        self._before_hooks.append(hook)

    def add_after_hook(self, hook: Callable[[Route], None]) -> None:
        """Add after navigation hook.

        Args:
            hook: Hook function
        """
        self._after_hooks.append(hook)

    def get_history(self) -> list[str]:
        """Get navigation history.

        Returns:
            List of paths
        """
        return self._history.copy()

    def clear_history(self) -> None:
        """Clear navigation history."""
        self._history.clear()
        self._future.clear()
