"""Font loading utility for custom theme fonts."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import ClassVar

from PySide6.QtGui import QFontDatabase


logger = logging.getLogger(__name__)


class FontLoader:
    """Loads custom fonts for use in Qt applications."""

    _loaded_fonts: ClassVar[set[str]] = set()

    @classmethod
    def load_font(cls, font_path: str | Path) -> str | None:
        """Load a font file into Qt's font database.

        Args:
            font_path: Absolute or relative path to the font file (.ttf, .otf, etc)

        Returns:
            The font family name if successful, None otherwise
        """
        font_path = Path(font_path)

        if not font_path.exists():
            logger.warning(f"Font file not found: {font_path}")
            return None

        if str(font_path) in cls._loaded_fonts:
            logger.debug(f"Font already loaded: {font_path}")
            # Return the family name by checking the database
            return cls._get_font_family(font_path)

        try:
            font_id = QFontDatabase.addApplicationFont(str(font_path))

            if font_id == -1:
                logger.error(f"Failed to load font: {font_path}")
                print(f"[X] FONT LOAD FAILED: {font_path.name}")
                return None

            families = QFontDatabase.applicationFontFamilies(font_id)

            if not families:
                logger.error(f"No font families found in: {font_path}")
                print(f"[X] NO FAMILIES: {font_path.name}")
                return None

            family_name: str = families[0]
            cls._loaded_fonts.add(str(font_path))
            logger.info(f"Loaded font '{family_name}' from {font_path.name}")
            print(f"[OK] LOADED FONT: '{family_name}' from {font_path.name}")

            return family_name

        except Exception:
            logger.exception(f"Error loading font {font_path}")
            return None

    @classmethod
    def _get_font_family(cls, font_path: Path) -> str | None:
        """Get the font family name for an already loaded font."""
        # This is a simplified approach - in a real implementation,
        # you'd want to cache the family names when fonts are first loaded
        return font_path.stem

    @classmethod
    def load_theme_fonts(cls, theme_path: Path) -> dict[str, str]:
        """Load all fonts from a theme's fonts directory.

        Args:
            theme_path: Path to the theme directory (e.g., pserver_manager/themes/runescape)

        Returns:
            Dictionary mapping font file names to their family names
        """
        fonts_dir = theme_path / "fonts"
        print(f"      Looking for fonts in: {fonts_dir}")

        if not fonts_dir.exists():
            logger.debug(f"No fonts directory found in theme: {theme_path}")
            print("      [X] Fonts directory not found")
            return {}

        loaded_fonts = {}

        # Load TTF fonts first (prefer TTF over OTF for better compatibility)
        ttf_files = list(fonts_dir.rglob("*.ttf"))
        print(f"      Found {len(ttf_files)} TTF files")
        for font_file in ttf_files:
            family = cls.load_font(font_file)
            if family:
                loaded_fonts[font_file.stem] = family

        # Load OTF fonts
        otf_files = list(fonts_dir.rglob("*.otf"))
        print(f"      Found {len(otf_files)} OTF files")
        for font_file in otf_files:
            if font_file.stem not in loaded_fonts:  # Only if TTF version not already loaded
                family = cls.load_font(font_file)
                if family:
                    loaded_fonts[font_file.stem] = family

        return loaded_fonts
