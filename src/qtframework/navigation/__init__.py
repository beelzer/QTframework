"""Navigation and routing system.

This module provides a comprehensive routing and navigation system for Qt applications,
supporting route parameters, guards, nested routes, and programmatic navigation.

Routing Concepts:
    Routes map URL-like paths to widget components::

        Path Pattern         Component       Example URL
        ───────────────      ─────────       ────────────
        /                    HomeView        /
        /users               UserList        /users
        /user/:id            UserProfile     /user/123
        /settings/*          SettingsView    /settings/profile

    Key features:
    - **Parameters**: Extract values from URLs (e.g., :id, :name)
    - **Guards**: Control access to routes (authentication, permissions)
    - **Nested Routes**: Hierarchical route structures
    - **Navigation Hooks**: Before/after navigation callbacks
    - **History**: Browser-like back/forward navigation

Quick Start:
    Basic routing setup::

        from qtframework.navigation import Router, Route, Navigator
        from PySide6.QtWidgets import QWidget, QStackedWidget


        # Define view components
        class HomeView(QWidget):
            pass


        class UserView(QWidget):
            def __init__(self, user_id=None):
                super().__init__()
                self.user_id = user_id


        # Define routes
        routes = [
            Route(path="/", component=HomeView, name="home"),
            Route(path="/user/:id", component=UserView, name="user"),
        ]

        # Create router
        router = Router(routes)

        # Set up navigation UI
        container = QStackedWidget()
        navigator = Navigator(router, container)

        # Navigate programmatically
        router.navigate("/user/123")
        router.navigate_by_name("home")
        router.back()  # Go back in history

    Route guards for authentication::

        def require_auth(route: Route) -> bool:
            '''Guard that checks authentication'''
            return current_user.is_authenticated


        protected_route = Route(
            path="/admin", component=AdminView, guards=[require_auth]
        )

    Navigation hooks::

        def before_navigate(from_path: str, to_path: str) -> bool:
            '''Called before navigation'''
            if has_unsaved_changes():
                return confirm_navigation()
            return True


        router.add_before_hook(before_navigate)

See Also:
    :class:`Router`: Core routing engine
    :class:`Route`: Route definition
    :class:`Navigator`: UI integration for routing
"""

from __future__ import annotations

from qtframework.navigation.navigator import Navigator
from qtframework.navigation.router import Route, Router


__all__ = ["Navigator", "Route", "Router"]
