"""Router for navigation between views.

This module provides a powerful routing system for managing navigation between
different views in a Qt application. It supports route parameters, guards,
nested routes, and navigation hooks.

Example:
    Basic router setup with routes and navigation::

        from qtframework.navigation.router import Router, Route
        from PySide6.QtWidgets import QWidget, QLabel


        # Define view components
        class HomeView(QWidget):
            def __init__(self):
                super().__init__()
                layout = QVBoxLayout(self)
                layout.addWidget(QLabel("Home Page"))


        class UserView(QWidget):
            def __init__(self, user_id=None):
                super().__init__()
                layout = QVBoxLayout(self)
                layout.addWidget(QLabel(f"User Profile: {user_id}"))


        # Define routes
        routes = [
            Route(path="/", component=HomeView, name="home"),
            Route(path="/user/:id", component=UserView, name="user_profile"),
            Route(
                path="/admin",
                component=AdminView,
                name="admin",
                guards=[lambda route: check_admin_permission()],
            ),
        ]

        # Create router
        router = Router(routes)


        # Connect to route changes
        def on_route_change(path, params):
            print(f"Navigated to: {path} with params: {params}")
            component = router.get_route_component()
            # Add component to your UI container


        router.route_changed.connect(on_route_change)

        # Navigate to routes
        router.navigate("/")  # Go to home
        router.navigate("/user/123")  # Go to user with id=123
        router.navigate_by_name("home")  # Navigate by route name

See Also:
    :class:`Route`: Route definition with parameters and guards
    :mod:`qtframework.core.window`: Window system that integrates with router
"""

from __future__ import annotations

import collections
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast

from PySide6.QtCore import QObject, Signal

from qtframework.utils.logger import get_logger


if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


logger = get_logger(__name__)


@dataclass
class Route:
    """Route definition.

    A route maps a URL path pattern to a widget component, with support for
    parameters, guards, and nested routes.

    Example:
        Define routes with parameter extraction::

            # Simple route
            home_route = Route(path="/", component=HomeView, name="home")

            # Route with parameters
            user_route = Route(path="/user/:id", component=UserView, name="user_profile")


            # Route with guard for authentication
            def auth_guard(route: Route) -> bool:
                return current_user.is_authenticated


            admin_route = Route(
                path="/admin", component=AdminView, name="admin", guards=[auth_guard]
            )

            # Nested routes
            settings_route = Route(
                path="/settings",
                component=SettingsLayout,
                children=[
                    Route(path="/profile", component=ProfileSettings),
                    Route(path="/preferences", component=PreferencesSettings),
                ],
            )

            # Route with redirect
            old_route = Route(path="/old-path", redirect="/new-path")
    """

    path: str
    component: type[QWidget] | collections.abc.Callable[..., QWidget]
    name: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)
    guards: list[collections.abc.Callable[[Route], bool]] = field(default_factory=list)
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

        Transforms path patterns like '/user/:id' into regex patterns
        with named capture groups for parameter extraction.

        Returns:
            Compiled pattern
        """
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
        self._before_hooks: list[collections.abc.Callable[[str, str], bool]] = []
        self._after_hooks: list[collections.abc.Callable[[Route], None]] = []

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

        Raises:
            ValueError: If path is invalid or malformed
            RuntimeError: If navigation fails due to circular redirects

        Note:
            Navigation can fail in several ways:
            - Route not found (returns False, logs error)
            - Guard blocks navigation (returns False, emits navigation_blocked)
            - Before hook blocks navigation (returns False, emits navigation_blocked)
        """
        logger.info("Navigating to: %s", path)

        for hook in self._before_hooks:
            if not hook(self._current_path, path):
                logger.warning("Navigation blocked by hook: %s", path)
                self.navigation_blocked.emit(self._current_path, path)
                return False

        route = self._find_route(path)
        if not route:
            logger.error("No route found for path: %s", path)
            return False

        if not route.can_activate():
            logger.warning("Route guard blocked: %s", path)
            self.navigation_blocked.emit(self._current_path, path)
            return False

        if route.redirect:
            return self.navigate(route.redirect, params)

        # Preserve history for back/forward navigation
        if not _internal and self._current_path and self._current_path != path:
            self._history.append(self._current_path)
            self._future.clear()

        self._current_path = path
        self._current_route = route

        route_params = params or {}
        _, extracted_params = route.matches(path)
        route_params.update(extracted_params)

        self.route_changed.emit(path, route_params)

        for after_hook in self._after_hooks:
            after_hook(route)

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

        component_callable = cast(
            "collections.abc.Callable[[], QWidget]", self._current_route.component
        )
        return component_callable()

    def add_before_hook(self, hook: collections.abc.Callable[[str, str], bool]) -> None:
        """Add before navigation hook.

        Args:
            hook: Hook function (from_path, to_path) -> bool
        """
        if not callable(hook):
            raise TypeError("Before hook must be callable")
        self._before_hooks.append(hook)

    def add_after_hook(self, hook: collections.abc.Callable[[Route], None]) -> None:
        """Add after navigation hook.

        Args:
            hook: Hook function
        """
        if not callable(hook):
            raise TypeError("After hook must be callable")
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
