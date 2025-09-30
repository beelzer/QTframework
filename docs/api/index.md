# API Reference

Welcome to the Qt Framework API reference documentation.

## Core Modules

The Qt Framework is organized into several key modules:

### Core (`qtframework.core`)

Core application components for building Qt applications.

```{eval-rst}
.. automodule:: qtframework.core.application
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.core.window
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.core.context
   :members:
   :undoc-members:
   :show-inheritance:
```

### Theming (`qtframework.themes`)

Modern token-based theming system with light, dark, and high contrast themes.

- See {doc}`../guides/theming` for comprehensive theming guide
- Design tokens provide semantic color system
- Hot-reload support for rapid development
- Custom theme creation via Python or YAML

```{eval-rst}
.. automodule:: qtframework.themes.theme
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.themes.theme_manager
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.themes.tokens
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.themes.builtin_themes
   :members:
   :undoc-members:
   :show-inheritance:
```

### State Management (`qtframework.state`)

Redux-inspired state management for predictable application state.

- See {doc}`../guides/state_management` for detailed guide
- Single source of truth for application state
- Pure reducers for state transformations
- Middleware for async operations

```{eval-rst}
.. automodule:: qtframework.state.store
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.state.actions
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.state.reducers
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.state.middleware
   :members:
   :undoc-members:
   :show-inheritance:
```

### Navigation (`qtframework.navigation`)

Declarative routing system for multi-page applications.

- See {doc}`../guides/navigation` for routing guide
- URL-based routing with dynamic parameters
- Route guards for access control
- Nested routes and page transitions

```{eval-rst}
.. automodule:: qtframework.navigation.router
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.navigation.navigator
   :members:
   :undoc-members:
   :show-inheritance:
```

### Internationalization (`qtframework.i18n`)

Comprehensive i18n support powered by Babel.

- See {doc}`../guides/internationalization` for i18n guide
- Translation extraction and compilation
- Runtime language switching
- Plural forms and context support
- Locale-aware number and date formatting

```{eval-rst}
.. automodule:: qtframework.i18n.babel_manager
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.i18n.contexts
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.i18n.widgets
   :members:
   :undoc-members:
   :show-inheritance:
```

### Plugins (`qtframework.plugins`)

Extensible plugin system for modular applications.

- See {doc}`../guides/plugins` for plugin development guide
- Dynamic loading and unloading
- Dependency resolution
- Plugin lifecycle management
- Hot reload support

```{eval-rst}
.. automodule:: qtframework.plugins.base
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.plugins.manager
   :members:
   :undoc-members:
   :show-inheritance:
```

### Configuration (`qtframework.config`)

Application configuration management with multiple providers.

```{eval-rst}
.. automodule:: qtframework.config.config
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.config.manager
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.config.providers
   :members:
   :undoc-members:
   :show-inheritance:
```

### Widgets (`qtframework.widgets`)

Custom widget components and UI elements.

```{eval-rst}
.. automodule:: qtframework.widgets.base
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.widgets.buttons
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.widgets.badge
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.widgets.inputs
   :members:
   :undoc-members:
   :show-inheritance:
```

#### Advanced Widgets

```{eval-rst}
.. automodule:: qtframework.widgets.advanced.tables
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.widgets.advanced.tabs
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.widgets.advanced.dialogs
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.widgets.advanced.notifications
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.widgets.advanced.charts
   :members:
   :undoc-members:
   :show-inheritance:
```

### Layouts (`qtframework.layouts`)

Specialized layout managers for common UI patterns.

```{eval-rst}
.. automodule:: qtframework.layouts.base
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.layouts.sidebar
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.layouts.card
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.layouts.flow
   :members:
   :undoc-members:
   :show-inheritance:
```

### Utilities (`qtframework.utils`)

Helper functions and utility classes.

```{eval-rst}
.. automodule:: qtframework.utils.logger
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.utils.validation
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.utils.paths
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: qtframework.utils.exceptions
   :members:
   :undoc-members:
   :show-inheritance:
```
