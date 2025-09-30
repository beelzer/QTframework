# Navigation and Routing Guide

Qt Framework provides a declarative routing system for building multi-page applications with navigation, URL-based routing, and page transitions.

## Overview

The navigation system includes:

- **Router** - Define routes and handle navigation
- **Navigator** - Programmatic navigation API
- **Route Guards** - Control access to routes
- **Nested Routes** - Create hierarchical page structures
- **History Management** - Back/forward navigation

## Quick Start

### Basic Routing

```python
from qtframework.core import Application, MainWindow
from qtframework.navigation import Router, Route
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

# Define pages
class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Home Page"))
        self.setLayout(layout)

class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("About Page"))
        self.setLayout(layout)

class ProfilePage(QWidget):
    def __init__(self, user_id=None):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Profile Page - User ID: {user_id}"))
        self.setLayout(layout)

# Create router
router = Router(routes=[
    Route(path="/", component=HomePage, name="home"),
    Route(path="/about", component=AboutPage, name="about"),
    Route(path="/profile/:id", component=ProfilePage, name="profile"),
])

# Create app
app = Application()
window = MainWindow()

# Set router outlet (where pages render)
window.setCentralWidget(router.outlet)

# Navigate
router.push("/")  # Go to home
router.push("/about")  # Go to about
router.push("/profile/123")  # Go to profile with ID=123

window.show()
app.exec()
```

## Defining Routes

### Simple Routes

```python
from qtframework.navigation import Route

routes = [
    Route(path="/", component=HomePage, name="home"),
    Route(path="/about", component=AboutPage, name="about"),
    Route(path="/contact", component=ContactPage, name="contact"),
]
```

### Dynamic Routes

Use `:param` syntax for dynamic segments:

```python
routes = [
    Route(path="/user/:id", component=UserPage, name="user"),
    Route(path="/post/:id/edit", component=EditPostPage, name="edit_post"),
    Route(path="/category/:name/items", component=CategoryPage, name="category"),
]
```

The component receives params as keyword arguments:

```python
class UserPage(QWidget):
    def __init__(self, id=None):
        super().__init__()
        self.user_id = id
        # Load user data using self.user_id
```

### Catch-All Routes

```python
routes = [
    Route(path="/", component=HomePage),
    Route(path="/about", component=AboutPage),
    # Catch-all for 404
    Route(path="*", component=NotFoundPage, name="404"),
]
```

## Navigation

### Programmatic Navigation

```python
from qtframework.navigation import Navigator

navigator = Navigator(router)

# Push new route
navigator.push("/about")

# Push with params
navigator.push("/user/123")

# Navigate by name
navigator.push_named("profile", params={"id": "456"})

# Go back
navigator.back()

# Go forward
navigator.forward()

# Go to specific history entry
navigator.go(-2)  # Go back 2 pages
navigator.go(1)   # Go forward 1 page

# Replace current route (no history entry)
navigator.replace("/login")
```

### Navigation from Widgets

```python
from PySide6.QtWidgets import QPushButton

class NavBar(QWidget):
    def __init__(self, router):
        super().__init__()
        self.router = router

        home_btn = QPushButton("Home")
        about_btn = QPushButton("About")
        profile_btn = QPushButton("Profile")

        home_btn.clicked.connect(lambda: router.push("/"))
        about_btn.clicked.connect(lambda: router.push("/about"))
        profile_btn.clicked.connect(lambda: router.push("/profile/me"))

        layout = QHBoxLayout()
        layout.addWidget(home_btn)
        layout.addWidget(about_btn)
        layout.addWidget(profile_btn)
        self.setLayout(layout)
```

## Route Guards

Control access to routes with guards:

### Before Navigation Guards

```python
from qtframework.navigation import Route, NavigationGuard

class AuthGuard(NavigationGuard):
    """Require authentication to access route."""

    def __init__(self, auth_service):
        self.auth_service = auth_service

    def can_activate(self, to_route, from_route):
        """Return True to allow navigation, False to block."""
        if self.auth_service.is_authenticated():
            return True
        else:
            # Redirect to login
            router.push("/login")
            return False

class AdminGuard(NavigationGuard):
    """Require admin role."""

    def __init__(self, auth_service):
        self.auth_service = auth_service

    def can_activate(self, to_route, from_route):
        user = self.auth_service.get_current_user()
        if user and user.get("role") == "admin":
            return True
        else:
            router.push("/unauthorized")
            return False

# Apply guards to routes
routes = [
    Route(path="/", component=HomePage),
    Route(
        path="/dashboard",
        component=DashboardPage,
        guards=[AuthGuard(auth_service)]
    ),
    Route(
        path="/admin",
        component=AdminPage,
        guards=[AuthGuard(auth_service), AdminGuard(auth_service)]
    ),
]
```

### Leave Guards

Prompt before leaving a route:

```python
class UnsavedChangesGuard(NavigationGuard):
    """Warn about unsaved changes."""

    def __init__(self, form_widget):
        self.form_widget = form_widget

    def can_deactivate(self, from_route, to_route):
        """Return True to allow leaving, False to block."""
        if self.form_widget.has_unsaved_changes():
            # Show confirmation dialog
            reply = QMessageBox.question(
                None,
                "Unsaved Changes",
                "You have unsaved changes. Leave anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            return reply == QMessageBox.Yes
        return True

# Apply to route
Route(
    path="/edit/:id",
    component=EditPage,
    guards=[UnsavedChangesGuard(edit_form)]
)
```

## Nested Routes

Create hierarchical page structures:

```python
class DashboardLayout(QWidget):
    """Parent layout with sidebar and outlet for child routes."""

    def __init__(self, router):
        super().__init__()
        self.router = router

        # Sidebar navigation
        sidebar = QWidget()
        overview_btn = QPushButton("Overview")
        stats_btn = QPushButton("Statistics")
        settings_btn = QPushButton("Settings")

        overview_btn.clicked.connect(lambda: router.push("/dashboard/overview"))
        stats_btn.clicked.connect(lambda: router.push("/dashboard/stats"))
        settings_btn.clicked.connect(lambda: router.push("/dashboard/settings"))

        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(overview_btn)
        sidebar_layout.addWidget(stats_btn)
        sidebar_layout.addWidget(settings_btn)
        sidebar.setLayout(sidebar_layout)

        # Main content area (router outlet)
        self.content = QWidget()

        # Layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content)
        self.setLayout(main_layout)

# Define nested routes
routes = [
    Route(path="/", component=HomePage),
    Route(
        path="/dashboard",
        component=DashboardLayout,
        children=[
            Route(path="overview", component=OverviewPage, name="dashboard.overview"),
            Route(path="stats", component=StatsPage, name="dashboard.stats"),
            Route(path="settings", component=SettingsPage, name="dashboard.settings"),
        ]
    ),
]
```

## Query Parameters

### Setting Query Parameters

```python
# Navigate with query params
router.push("/search", query={"q": "python", "page": "1"})

# Access in component
class SearchPage(QWidget):
    def __init__(self, query=None):
        super().__init__()
        self.search_query = query.get("q", "") if query else ""
        self.page = int(query.get("page", "1")) if query else 1
```

### Updating Query Parameters

```python
# Update query params without navigation
router.replace("/search", query={"q": "python", "page": "2"})
```

## Navigation Events

Listen to navigation events:

```python
from qtframework.navigation import NavigationEvent

class NavigationLogger:
    def __init__(self, router):
        router.on_navigation.connect(self.on_navigate)
        router.on_navigation_error.connect(self.on_error)

    def on_navigate(self, event: NavigationEvent):
        print(f"Navigated from {event.from_route} to {event.to_route}")

    def on_error(self, error):
        print(f"Navigation error: {error}")
```

## Page Transitions

Add animations between pages:

```python
from PySide6.QtCore import QPropertyAnimation, QEasingCurve

class FadeRouter(Router):
    """Router with fade transitions."""

    def _show_component(self, component):
        """Override to add fade effect."""
        # Fade out current
        if self.current_component:
            fade_out = QPropertyAnimation(self.current_component, b"windowOpacity")
            fade_out.setDuration(200)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.0)
            fade_out.setEasingCurve(QEasingCurve.OutCubic)
            fade_out.finished.connect(lambda: self._swap_component(component))
            fade_out.start()
        else:
            self._swap_component(component)

    def _swap_component(self, component):
        """Swap and fade in new component."""
        super()._show_component(component)

        # Fade in new
        fade_in = QPropertyAnimation(component, b"windowOpacity")
        fade_in.setDuration(200)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.InCubic)
        fade_in.start()
```

## Complete Example

```python
from qtframework.core import Application, MainWindow
from qtframework.navigation import Router, Route, Navigator, NavigationGuard
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget
)

# Auth service (simplified)
class AuthService:
    def __init__(self):
        self._user = None

    def login(self, username):
        self._user = {"username": username}

    def logout(self):
        self._user = None

    def is_authenticated(self):
        return self._user is not None

# Auth guard
class AuthGuard(NavigationGuard):
    def __init__(self, auth_service):
        self.auth = auth_service

    def can_activate(self, to_route, from_route):
        if not self.auth.is_authenticated():
            router.push("/login")
            return False
        return True

# Pages
class LoginPage(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel("Login Page")
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.do_login)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.login_btn)
        self.setLayout(layout)

    def do_login(self):
        auth.login("user")
        router.push("/dashboard")

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Dashboard (Protected)"))
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.do_logout)
        layout.addWidget(logout_btn)
        self.setLayout(layout)

    def do_logout(self):
        auth.logout()
        router.push("/login")

# Setup
auth = AuthService()

routes = [
    Route(path="/login", component=LoginPage, name="login"),
    Route(
        path="/dashboard",
        component=DashboardPage,
        name="dashboard",
        guards=[AuthGuard(auth)]
    ),
]

router = Router(routes=routes)

# Run
app = Application()
window = MainWindow()
window.setCentralWidget(router.outlet)
router.push("/login")
window.show()
app.exec()
```

## Best Practices

1. **Use Named Routes** - Easier refactoring and maintenance
2. **Guard Sensitive Routes** - Always protect admin/authenticated routes
3. **Lazy Load Pages** - Load page components on demand for large apps
4. **Handle 404s** - Always include a catch-all route
5. **Keep URLs Meaningful** - Use RESTful URL patterns
6. **Validate Params** - Check and validate route parameters in components
7. **Centralize Navigation** - Use navigator service instead of direct router access

## Advanced Topics

### Lazy Loading

```python
def lazy_load(module_path, class_name):
    """Lazy load a component."""
    def loader():
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    return loader

routes = [
    Route(
        path="/admin",
        component=lazy_load("myapp.pages.admin", "AdminPage"),
        name="admin"
    ),
]
```

### Route Meta Data

```python
routes = [
    Route(
        path="/admin",
        component=AdminPage,
        meta={"requiresAuth": True, "roles": ["admin"], "title": "Admin Panel"}
    ),
]

# Access in guards
class MetaAuthGuard(NavigationGuard):
    def can_activate(self, to_route, from_route):
        if to_route.meta.get("requiresAuth"):
            # Check auth...
            pass
```
