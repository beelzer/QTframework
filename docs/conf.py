"""Simplified Sphinx configuration."""

from __future__ import annotations

import sys
from pathlib import Path

from sphinx_pyproject import SphinxConfig


# Add project root to Python path for autodoc
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load configuration from pyproject.toml
config = SphinxConfig("../pyproject.toml", globalns=globals())

# Simple theme configuration
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
