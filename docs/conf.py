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

# HTML output options
html_theme = "furo"
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#1e88e5",
        "color-brand-content": "#0d47a1",
    },
    "dark_css_variables": {
        "color-brand-primary": "#1e88e5",
        "color-brand-content": "#0d47a1",
    },
}
html_static_path = ["_static"]

# MyST parser options
myst_enable_extensions = [
    "deflist",
    "tasklist",
    "colon_fence",
]

# Autodoc options
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
