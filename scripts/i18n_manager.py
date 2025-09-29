#!/usr/bin/env python
"""i18n management script for Qt Framework.

Commands:
    extract    Extract translatable strings from source code
    init       Initialize a new locale
    update     Update existing translations
    compile    Compile .po files to .mo files
    stats      Show translation statistics
"""

from __future__ import annotations

import argparse
import subprocess  # noqa: S404
import sys
from pathlib import Path
from shutil import copy2


# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import polib

    HAS_POLIB = True
except ImportError:
    HAS_POLIB = False
    print("Warning: polib not installed. Some features will be limited.")


class I18nManager:
    """Manage translations using pybabel."""

    def __init__(self) -> None:
        self.project_root = PROJECT_ROOT
        self.locale_dir = self.project_root / "src" / "qtframework" / "i18n" / "locale"
        self.pot_file = self.locale_dir / "qtframework.pot"
        self.babel_cfg = self.project_root / "babel.cfg"
        self.domain = "qtframework"

    def extract(self, keywords: list[str] | None = None) -> bool:
        """Extract translatable strings to .pot file."""
        print(f"Extracting translatable strings to {self.pot_file}...")

        # Ensure locale directory exists
        self.locale_dir.mkdir(parents=True, exist_ok=True)

        # Build extraction command
        cmd = [
            sys.executable,
            "-m",
            "babel.messages.frontend",
            "extract",
            "-F",
            str(self.babel_cfg),
            "-o",
            str(self.pot_file),
            "--project",
            "Qt Framework",
            "--version",
            "1.0.0",
            "--copyright-holder",
            "Qt Framework Team",
            "--msgid-bugs-address",
            "support@qtframework.com",
        ]

        # Add custom keywords if provided
        if keywords:
            for keyword in keywords:
                cmd.extend(["-k", keyword])
        else:
            # Default keywords
            cmd.extend([
                "-k",
                "_",
                "-k",
                "t:1",
                "-k",
                "gettext:1",
                "-k",
                "pgettext:1c,2",
                "-k",
                "plural:1,2",
                "-k",
                "ngettext:1,2",
                "-k",
                "npgettext:1c,2,3",
                "-k",
                "lazy_gettext:1",
            ])

        # Add source directory
        cmd.append(str(self.project_root / "src"))

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                print(f"[OK] Successfully extracted strings to {self.pot_file}")
                self._show_pot_stats()
                return True
            print(f"[ERROR] Extraction failed: {result.stderr}")
            return False
        except Exception as e:
            print(f"[ERROR] Error during extraction: {e}")
            return False

    def init_locale(self, locale: str) -> bool:
        """Initialize a new locale."""
        locale_path = self.locale_dir / locale / "LC_MESSAGES"
        po_file = locale_path / f"{self.domain}.po"

        if po_file.exists():
            print(f"[ERROR] Locale {locale} already exists at {po_file}")
            return False

        print(f"Initializing locale {locale}...")

        # Ensure POT file exists
        if not self.pot_file.exists():
            print("POT file not found. Extracting strings first...")
            if not self.extract():
                return False

        # Create locale directory
        locale_path.mkdir(parents=True, exist_ok=True)

        # Initialize translation
        cmd = [
            sys.executable,
            "-m",
            "babel.messages.frontend",
            "init",
            "-i",
            str(self.pot_file),
            "-d",
            str(self.locale_dir),
            "-D",
            self.domain,
            "-l",
            locale,
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                print(f"[OK] Successfully initialized locale {locale}")
                print(f"  Translation file: {po_file}")
                return True
            print(f"[ERROR] Initialization failed: {result.stderr}")
            return False
        except Exception as e:
            print(f"[ERROR] Error during initialization: {e}")
            return False

    def update_locales(self, locales: list[str] | None = None) -> bool:
        """Update existing locale translations."""
        if not self.pot_file.exists():
            print("POT file not found. Extracting strings first...")
            if not self.extract():
                return False

        # Get locales to update
        if locales:
            locale_list = locales
        else:
            # Find all existing locales
            locale_list = []
            if self.locale_dir.exists():
                for locale_path in self.locale_dir.iterdir():
                    if locale_path.is_dir():
                        po_file = locale_path / "LC_MESSAGES" / f"{self.domain}.po"
                        if po_file.exists():
                            locale_list.append(locale_path.name)

        if not locale_list:
            print("No locales found to update")
            return False

        print(f"Updating {len(locale_list)} locale(s): {', '.join(locale_list)}")

        success = True
        for locale in locale_list:
            po_file = self.locale_dir / locale / "LC_MESSAGES" / f"{self.domain}.po"

            # Backup existing file
            backup_file = po_file.with_suffix(".po.bak")
            if po_file.exists():
                copy2(po_file, backup_file)

            cmd = [
                sys.executable,
                "-m",
                "babel.messages.frontend",
                "update",
                "-i",
                str(self.pot_file),
                "-d",
                str(self.locale_dir),
                "-D",
                self.domain,
                "-l",
                locale,
                "--previous",  # Keep previous msgids as comments
                "--no-fuzzy-matching",  # Disable fuzzy matching by default
            ]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    print(f"  [OK] Updated {locale}")
                    if HAS_POLIB:
                        I18nManager._show_po_stats(po_file)
                else:
                    print(f"  [ERROR] Failed to update {locale}: {result.stderr}")
                    success = False
            except Exception as e:
                print(f"  [ERROR] Error updating {locale}: {e}")
                success = False

        return success

    def compile_locales(self, locales: list[str] | None = None, quiet: bool = False) -> bool:
        """Compile .po files to .mo files."""
        # Get locales to compile
        if locales:
            locale_list = locales
        else:
            # Find all existing locales
            locale_list = []
            if self.locale_dir.exists():
                for locale_path in self.locale_dir.iterdir():
                    if locale_path.is_dir():
                        po_file = locale_path / "LC_MESSAGES" / f"{self.domain}.po"
                        if po_file.exists():
                            locale_list.append(locale_path.name)

        if not locale_list:
            if not quiet:
                print("No locales found to compile")
            return False

        if not quiet:
            print(f"Compiling {len(locale_list)} locale(s): {', '.join(locale_list)}")

        success = True
        for locale in locale_list:
            po_file = self.locale_dir / locale / "LC_MESSAGES" / f"{self.domain}.po"
            mo_file = po_file.with_suffix(".mo")

            cmd = [
                sys.executable,
                "-m",
                "babel.messages.frontend",
                "compile",
                "-d",
                str(self.locale_dir),
                "-D",
                self.domain,
                "-l",
                locale,
                "-f",  # Include fuzzy translations
                "--statistics",  # Show statistics
            ]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    if not quiet:
                        print(f"  [OK] Compiled {locale} -> {mo_file.name}")
                else:
                    if not quiet:
                        print(f"  [ERROR] Failed to compile {locale}: {result.stderr}")
                    success = False
            except Exception as e:
                if not quiet:
                    print(f"  [ERROR] Error compiling {locale}: {e}")
                success = False

        return success

    def show_stats(self) -> None:
        """Show translation statistics."""
        if not HAS_POLIB:
            print("Statistics require polib. Install with: pip install polib")
            return

        print("\nTranslation Statistics:")
        print("-" * 60)

        # Show POT stats
        if self.pot_file.exists():
            self._show_pot_stats()
            print("-" * 60)

        # Show stats for each locale
        if self.locale_dir.exists():
            locales_found = False
            for locale_path in sorted(self.locale_dir.iterdir()):
                if locale_path.is_dir():
                    po_file = locale_path / "LC_MESSAGES" / f"{self.domain}.po"
                    if po_file.exists():
                        locales_found = True
                        print(f"\n{locale_path.name}:")
                        I18nManager._show_po_stats(po_file)

            if not locales_found:
                print("No translation files found")

    def _show_pot_stats(self) -> None:
        """Show statistics for POT file."""
        if not HAS_POLIB or not self.pot_file.exists():
            return

        try:
            pot = polib.pofile(str(self.pot_file))
            print(f"Template ({self.pot_file.name}):")
            print(f"  Total strings: {len(pot)}")

            # Count plural forms
            plural_count = sum(1 for entry in pot if entry.msgid_plural)
            if plural_count:
                print(f"  Plural forms: {plural_count}")

        except Exception as e:
            print(f"  Error reading POT file: {e}")

    @staticmethod
    def _show_po_stats(po_file: Path) -> None:
        """Show statistics for a PO file."""
        if not HAS_POLIB or not po_file.exists():
            return

        try:
            po = polib.pofile(str(po_file))
            total = len(po)
            translated = len(po.translated_entries())
            fuzzy = len(po.fuzzy_entries())
            untranslated = len(po.untranslated_entries())
            percent = po.percent_translated()

            print(f"  Total: {total} | Translated: {translated} ({percent:.1f}%)")

            if fuzzy:
                print(f"  Fuzzy: {fuzzy}")
            if untranslated:
                print(f"  Untranslated: {untranslated}")

            # Check for obsolete entries
            obsolete = len(po.obsolete_entries())
            if obsolete:
                print(f"  Obsolete: {obsolete} (can be removed)")

        except Exception as e:
            print(f"  Error reading PO file: {e}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage Qt Framework translations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all translatable strings
  python scripts/i18n_manager.py extract

  # Initialize a new locale
  python scripts/i18n_manager.py init fr_FR

  # Update all existing translations
  python scripts/i18n_manager.py update

  # Update specific locale
  python scripts/i18n_manager.py update -l es_ES

  # Compile all translations
  python scripts/i18n_manager.py compile

  # Show translation statistics
  python scripts/i18n_manager.py stats
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract translatable strings")
    extract_parser.add_argument(
        "-k", "--keyword", action="append", help="Additional extraction keyword"
    )

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new locale")
    init_parser.add_argument("locale", help="Locale code (e.g., fr_FR, es_ES)")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update existing translations")
    update_parser.add_argument(
        "-l",
        "--locale",
        action="append",
        help="Specific locale to update (can be used multiple times)",
    )

    # Compile command
    compile_parser = subparsers.add_parser("compile", help="Compile .po files to .mo files")
    compile_parser.add_argument(
        "-l",
        "--locale",
        action="append",
        help="Specific locale to compile (can be used multiple times)",
    )
    compile_parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress output (useful for pre-commit hooks)"
    )

    # Stats command
    subparsers.add_parser("stats", help="Show translation statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = I18nManager()

    if args.command == "extract":
        manager.extract(keywords=args.keyword)
    elif args.command == "init":
        manager.init_locale(args.locale)
    elif args.command == "update":
        manager.update_locales(locales=args.locale)
    elif args.command == "compile":
        manager.compile_locales(locales=args.locale, quiet=args.quiet)
    elif args.command == "stats":
        manager.show_stats()


if __name__ == "__main__":
    main()
