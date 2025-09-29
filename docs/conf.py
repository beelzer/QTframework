"""Minimal Sphinx configuration using sphinx-pyproject."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml
from sphinx_pyproject import SphinxConfig


# Add project root to Python path for autodoc
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load configuration from pyproject.toml
config = SphinxConfig("../pyproject.toml", globalns=globals())

# Load theme colors from your actual theme files
def load_theme_colors():
    """Load colors from the QT Framework theme files."""
    themes_path = Path(__file__).parent.parent / "resources" / "themes"

    # You can load from any of your theme files
    # Let's use solarized_dark as an example
    solarized_dark_path = themes_path / "solarized_dark.yaml"

    if solarized_dark_path.exists():
        with open(solarized_dark_path) as f:
            theme = yaml.safe_load(f)

        # Extract relevant colors from your theme
        return {
            "primary": theme.get("colors", {}).get("primary", "#1e88e5"),
            "accent": theme.get("colors", {}).get("accent", "#0d47a1"),
            "background": theme.get("colors", {}).get("background", "#002b36"),
            "surface": theme.get("colors", {}).get("surface", "#073642"),
        }

    # Default colors if theme file not found
    return {
        "primary": "#1e88e5",
        "accent": "#0d47a1",
        "background": "#002b36",
        "surface": "#073642",
    }

# Load theme colors
theme_colors = load_theme_colors()

# Configure Furo theme with dynamic colors from your themes
html_theme_options = {
    "light_css_variables": {
        # Use lighter variants for light mode
        "color-brand-primary": theme_colors["accent"],
        "color-brand-content": theme_colors["primary"],
    },
    "dark_css_variables": {
        # Use your actual theme colors for dark mode
        "color-brand-primary": theme_colors["primary"],
        "color-brand-content": theme_colors["accent"],
    },
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
}

# You could also dynamically load all available themes and document them
def get_all_themes():
    """Get all available themes for documentation."""
    themes_path = Path(__file__).parent.parent / "resources" / "themes"
    themes = {}

    if themes_path.exists():
        for theme_file in themes_path.glob("*.yaml"):
            with open(theme_file) as f:
                themes[theme_file.stem] = yaml.safe_load(f)

    return themes

# Store themes for potential use in documentation
available_themes = get_all_themes()

# Intersphinx mapping - must be in Python format (tuples)
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pyside6": ("https://doc.qt.io/qtforpython-6/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org/en/20/", None),
}

# Any additional configuration that can't be in pyproject.toml
# The version can be dynamically set if needed
# import qtframework
# release = qtframework.__version__
