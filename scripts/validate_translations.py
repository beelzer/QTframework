#!/usr/bin/env python3
"""Validate translation files."""

from __future__ import annotations

import sys
from pathlib import Path


try:
    import polib
except ImportError:
    print("polib is required. Install with: pip install polib")
    sys.exit(1)


def validate_translations(locale_dir: str = "src/qtframework/locales") -> bool:
    """Validate all .po translation files."""
    locale_path = Path(locale_dir)
    if not locale_path.exists():
        print(f"Locale directory {locale_dir} not found")
        return True  # Not an error if no translations yet

    errors = []
    for po_file in locale_path.rglob("*.po"):
        try:
            po = polib.pofile(str(po_file))
            if po.percent_translated() < 50:
                errors.append(f"{po_file}: Only {po.percent_translated():.0f}% translated")
            # Check for errors
            if po.check():
                errors.extend([f"{po_file}: {err}" for err in po.check()])
        except Exception as e:
            errors.append(f"{po_file}: {e}")

    if errors:
        print("Translation validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    print("All translations valid!")
    return True


if __name__ == "__main__":
    success = validate_translations()
    sys.exit(0 if success else 1)
