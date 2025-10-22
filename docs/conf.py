"""Basic Sphinx configuration."""

from __future__ import annotations

import sys
from pathlib import Path


# Add project root to Python path for autodoc
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Basic configuration
project = "Qt Framework"
copyright = "2025, Qt Framework Team"
author = "Qt Framework Team"
release = "0.1.0"

# Extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_design",
]

# Templates and paths
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Import theme colors from framework
from qtframework.themes.builtin_themes import create_dark_theme, create_light_theme


light_theme = create_light_theme()
dark_theme = create_dark_theme()

# Extract colors from theme tokens
light_colors = {
    "color-brand-primary": light_theme.tokens.primitive.primary_600,
    "color-brand-content": light_theme.tokens.primitive.primary_700,
    "color-background-primary": light_theme.tokens.semantic.bg_primary,
    "color-background-secondary": light_theme.tokens.semantic.bg_secondary,
    "color-foreground-primary": light_theme.tokens.semantic.fg_primary,
    "color-foreground-secondary": light_theme.tokens.semantic.fg_secondary,
    "color-foreground-border": light_theme.tokens.semantic.border_default,
}

dark_colors = {
    "color-brand-primary": dark_theme.tokens.primitive.primary_500,
    "color-brand-content": dark_theme.tokens.primitive.primary_600,
    "color-background-primary": dark_theme.tokens.semantic.bg_primary,
    "color-background-secondary": dark_theme.tokens.semantic.bg_secondary,
    "color-foreground-primary": dark_theme.tokens.semantic.fg_primary,
    "color-foreground-secondary": dark_theme.tokens.semantic.fg_secondary,
    "color-foreground-border": dark_theme.tokens.semantic.border_default,
}

# HTML output options
html_theme = "furo"
html_theme_options = {
    "light_css_variables": light_colors,
    "dark_css_variables": dark_colors,
}
html_static_path = []

# MyST parser options
myst_enable_extensions = [
    "deflist",
    "tasklist",
    "colon_fence",
]

# Autodoc options
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
