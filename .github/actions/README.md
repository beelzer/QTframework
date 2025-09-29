# Reusable GitHub Actions

## Available Actions

### setup-environment

Sets up Python environment with all dependencies and system requirements.

**Usage:**

```yaml
- uses: ./.github/actions/setup-environment
  with:
    python-version: "3.13" # Default: 3.13
    install-type: "dev" # Options: minimal, dev, full
```

**Features:**

- Configures Python with pip caching
- Installs Qt system dependencies on Linux
- Handles different installation types:
  - `minimal`: Just the package
  - `dev`: Package with dev dependencies
  - `full`: Package with dev and docs dependencies

### build-docs

Builds Sphinx documentation ready for deployment.

**Usage:**

```yaml
- uses: ./.github/actions/build-docs
  with:
    python-version: "3.13" # Default: 3.13
    docs-folder: "docs" # Default: docs
    output-folder: "docs/_build/html" # Default: docs/_build/html
```

**Features:**

- Uses setup-environment action for dependencies
- Builds HTML documentation with Sphinx
- Creates .nojekyll file for GitHub Pages
- Validates build output

## Adding New Actions

To add a new reusable action:

1. Create a new directory: `.github/actions/[action-name]/`
2. Add `action.yml` with inputs, outputs, and steps
3. Use composite actions for maximum reusability
4. Document the action in this README

## Design Principles

- **Modular**: Each action does one thing well
- **Reusable**: Can be used across different workflows
- **Configurable**: Inputs for customization
- **Cached**: Use caching where possible for speed
- **Simple**: Start simple, add complexity as needed
