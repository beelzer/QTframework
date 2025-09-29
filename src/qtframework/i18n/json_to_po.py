"""Convert JSON translations to Gettext .po format."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, TextIO


class JsonToPoConverter:
    """Convert JSON translation files to Gettext .po format."""

    def __init__(self, project_name: str = "Qt Framework", version: str = "1.0.0") -> None:
        """Initialize converter.

        Args:
            project_name: Name of the project
            version: Project version
        """
        self.project_name = project_name
        self.version = version
        self.entries: list[dict[str, Any]] = []

    def convert_json_to_po(
        self,
        json_file: Path,
        po_file: Path,
        locale: str,
        source_locale: str = "en_US",
    ) -> None:
        """Convert a JSON translation file to .po format.

        Args:
            json_file: Path to JSON file
            po_file: Output .po file path
            locale: Target locale
            source_locale: Source locale for msgid
        """
        # Load JSON translations
        with Path(json_file).open(encoding="utf-8") as f:
            translations = json.load(f)

        # Load source translations if different locale
        source_translations = translations
        if locale != source_locale:
            source_json = json_file.parent / f"{source_locale}.json"
            if source_json.exists():
                with Path(source_json).open(encoding="utf-8") as f:
                    source_translations = json.load(f)

        # Convert to flat entries
        self.entries = []
        self._flatten_dict(translations, source_translations)

        # Write .po file
        po_file.parent.mkdir(parents=True, exist_ok=True)
        with Path(po_file).open("w", encoding="utf-8") as f:
            self._write_po_header(f, locale)
            self._write_po_entries(f)

    def _flatten_dict(
        self,
        translations: dict[str, Any],
        source: dict[str, Any],
        prefix: str = "",
    ) -> None:
        """Flatten nested dictionary into translation entries.

        Args:
            translations: Target translations
            source: Source translations for msgid
            prefix: Current key prefix
        """
        for key, value in translations.items():
            full_key = f"{prefix}.{key}" if prefix else key

            # Get source value
            source_value: Any = source
            for k in full_key.split("."):
                if isinstance(source_value, dict) and k in source_value:
                    source_value = source_value[k]
                else:
                    source_value = full_key
                    break

            if isinstance(value, dict):
                # Handle plural forms specially
                if self._is_plural_form(value):
                    self._add_plural_entry(full_key, value, source_value)
                else:
                    # Recurse for nested dictionaries
                    self._flatten_dict(
                        value, source_value if isinstance(source_value, dict) else {}, full_key
                    )
            else:
                # For .po format, use English text as msgid
                # The msgctxt provides the original key for reference
                if isinstance(source_value, str):
                    msgid = source_value
                else:
                    msgid = str(value) if prefix == "" else str(source_value)

                self.entries.append({
                    "msgctxt": full_key,
                    "msgid": msgid,
                    "msgstr": str(value),
                })

    def _is_plural_form(self, value: dict) -> bool:
        """Check if a dict represents plural forms."""
        plural_keys = {"zero", "one", "two", "few", "many", "other"}
        return any(k in value for k in plural_keys)

    def _add_plural_entry(self, key: str, value: dict, source_value: Any) -> None:
        """Add a plural translation entry."""
        # Get singular and plural forms
        value.get("one", value.get("other", ""))
        value.get("other", "")

        # Get source forms
        if isinstance(source_value, dict):
            source_singular = source_value.get("one", source_value.get("other", ""))
            source_plural = source_value.get("other", "")
        else:
            source_singular = source_plural = str(source_value)

        # Create plural entry
        msgstr_plural = [
            str(value[form])
            for form in ["zero", "one", "two", "few", "many", "other"]
            if form in value
        ]

        self.entries.append({
            "msgctxt": key,
            "msgid": source_singular,
            "msgid_plural": source_plural,
            "msgstr_plural": msgstr_plural,
        })

    def _write_po_header(self, f: TextIO, locale: str) -> None:
        """Write .po file header.

        Args:
            f: File handle
            locale: Target locale
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M%z")

        header = f"""# Translation file for {self.project_name}
# Copyright (C) {datetime.now().year}
# This file is distributed under the same license as the {self.project_name} package.
#
msgid ""
msgstr ""
"Project-Id-Version: {self.project_name} {self.version}\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: {now}\\n"
"PO-Revision-Date: {now}\\n"
"Last-Translator: \\n"
"Language-Team: \\n"
"Language: {locale}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: {self._get_plural_forms(locale)}\\n"

"""
        f.write(header)

    def _get_plural_forms(self, locale: str) -> str:
        """Get plural forms rule for locale.

        Args:
            locale: Locale code

        Returns:
            Plural forms rule string
        """
        # Common plural form rules
        plural_rules = {
            "en": "nplurals=2; plural=(n != 1);",
            "es": "nplurals=2; plural=(n != 1);",
            "fr": "nplurals=2; plural=(n > 1);",
            "de": "nplurals=2; plural=(n != 1);",
            "it": "nplurals=2; plural=(n != 1);",
            "pt": "nplurals=2; plural=(n != 1);",
            "ru": "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);",
            "pl": "nplurals=3; plural=(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);",
            "ja": "nplurals=1; plural=0;",
            "zh": "nplurals=1; plural=0;",
            "ko": "nplurals=1; plural=0;",
            "ar": "nplurals=6; plural=(n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5);",
        }

        # Extract language code from locale
        lang = locale.split("_", maxsplit=1)[0].lower()
        return plural_rules.get(lang, "nplurals=2; plural=(n != 1);")

    def _write_po_entries(self, f: TextIO) -> None:
        """Write translation entries to .po file.

        Args:
            f: File handle
        """
        for entry in self.entries:
            # Write context if present
            if "msgctxt" in entry:
                f.write(f'msgctxt "{self._escape_string(entry["msgctxt"])}"\n')

            # Write msgid
            f.write(f'msgid "{self._escape_string(entry["msgid"])}"\n')

            # Handle plural forms
            if "msgid_plural" in entry:
                f.write(f'msgid_plural "{self._escape_string(entry["msgid_plural"])}"\n')
                f.writelines(
                    f'msgstr[{i}] "{self._escape_string(msgstr)}"\n'
                    for i, msgstr in enumerate(entry.get("msgstr_plural", []))
                )
            else:
                # Write msgstr
                f.write(f'msgstr "{self._escape_string(entry.get("msgstr", ""))}"\n')

            f.write("\n")

    def _escape_string(self, s: str) -> str:
        """Escape string for .po format.

        Args:
            s: String to escape

        Returns:
            Escaped string
        """
        return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def convert_all_json_to_po(
    json_dir: Path,
    po_dir: Path,
    domain: str = "qtframework",
) -> None:
    """Convert all JSON translation files to .po format.

    Args:
        json_dir: Directory containing JSON files
        po_dir: Output directory for .po files
        domain: Translation domain
    """
    converter = JsonToPoConverter()

    for json_file in json_dir.glob("*.json"):
        locale = json_file.stem

        # Create locale directory structure
        locale_dir = po_dir / locale / "LC_MESSAGES"
        locale_dir.mkdir(parents=True, exist_ok=True)

        po_file = locale_dir / f"{domain}.po"

        print(f"Converting {json_file} to {po_file}")
        converter.convert_json_to_po(json_file, po_file, locale)


def create_pot_template(
    source_json: Path,
    pot_file: Path,
    domain: str = "qtframework",
) -> None:
    """Create a .pot template file from source JSON.

    Args:
        source_json: Source JSON file (usually en_US.json)
        pot_file: Output .pot file
        domain: Translation domain
    """
    converter = JsonToPoConverter()

    # Load source translations
    with Path(source_json).open(encoding="utf-8") as f:
        translations = json.load(f)

    # Flatten to entries with empty msgstr
    converter.entries = []
    converter._flatten_dict(translations, translations)

    # Clear msgstr values for template
    for entry in converter.entries:
        if "msgstr" in entry:
            entry["msgstr"] = ""
        if "msgstr_plural" in entry:
            entry["msgstr_plural"] = [""] * len(entry["msgstr_plural"])

    # Write .pot file
    pot_file.parent.mkdir(parents=True, exist_ok=True)
    with Path(pot_file).open("w", encoding="utf-8") as f:
        converter._write_po_header(f, "")
        converter._write_po_entries(f)

    print(f"Created template: {pot_file}")


if __name__ == "__main__":
    # Convert existing JSON translations to .po format
    json_dir = Path(__file__).parent / "translations"
    po_dir = Path(__file__).parent / "locale"

    if json_dir.exists():
        convert_all_json_to_po(json_dir, po_dir)

        # Create .pot template from English
        en_json = json_dir / "en_US.json"
        if en_json.exists():
            pot_file = po_dir / "qtframework.pot"
            create_pot_template(en_json, pot_file)
