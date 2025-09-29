"""Translation key extraction tools."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from qtframework.utils.logger import get_logger


logger = get_logger(__name__)


class TranslationExtractor:
    """Extract translation keys from source code."""

    def __init__(self) -> None:
        """Initialize the extractor."""
        self.translation_functions = ["t", "plural", "_t", "_plural"]
        self.keys: set[str] = set()
        self.key_locations: dict[str, list[tuple[str, int]]] = {}

    def extract_from_python(self, file_path: Path) -> set[str]:
        """Extract translation keys from Python files."""
        keys = set()
        try:
            with Path(file_path).open(encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content, filename=str(file_path))

            # Visit all nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Check if it's a translation function
                    func_name = self._get_function_name(node)
                    if func_name in self.translation_functions:
                        # Extract the key (first argument)
                        if node.args and isinstance(node.args[0], ast.Constant):
                            key = node.args[0].value
                            if isinstance(key, str):
                                keys.add(key)
                                # Track location
                                if key not in self.key_locations:
                                    self.key_locations[key] = []
                                if hasattr(node, "lineno"):
                                    self.key_locations[key].append((str(file_path), node.lineno))

        except Exception as e:
            logger.exception("Failed to extract from %s: %s", file_path, e)

        return keys

    def _get_function_name(self, node: ast.Call) -> str:
        """Get the function name from a Call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            return node.func.attr
        return ""

    def extract_from_qml(self, file_path: Path) -> set[str]:
        """Extract translation keys from QML files."""
        keys = set()
        try:
            with Path(file_path).open(encoding="utf-8") as f:
                content = f.read()

            # Simple regex patterns for QML
            patterns = [
                r'qsTr\("([^"]+)"\)',
                r"qsTr\('([^']+)'\)",
                r'qsTrId\("([^"]+)"\)',
                r"qsTrId\('([^']+)'\)",
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content)
                keys.update(matches)

        except Exception as e:
            logger.exception("Failed to extract from %s: %s", file_path, e)

        return keys

    def extract_from_directory(
        self, directory: Path, file_patterns: list[str] | None = None
    ) -> set[str]:
        """Extract translation keys from all files in a directory.

        Args:
            directory: Directory to scan
            file_patterns: File patterns to include (default: ["*.py", "*.qml"])

        Returns:
            Set of translation keys
        """
        if file_patterns is None:
            file_patterns = ["*.py", "*.qml"]

        all_keys = set()

        for pattern in file_patterns:
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    if file_path.suffix == ".py":
                        keys = self.extract_from_python(file_path)
                    elif file_path.suffix == ".qml":
                        keys = self.extract_from_qml(file_path)
                    else:
                        continue

                    all_keys.update(keys)
                    if keys:
                        logger.debug(f"Extracted {len(keys)} keys from {file_path}")

        self.keys = all_keys
        return all_keys

    def generate_template(self, keys: set[str] | None = None) -> dict[str, str]:
        """Generate a translation template from extracted keys.

        Args:
            keys: Keys to include (uses extracted keys if None)

        Returns:
            Dictionary template for translations
        """
        if keys is None:
            keys = self.keys

        template: dict[str, Any] = {}

        for key in sorted(keys):
            # Create nested structure from dot notation
            parts = key.split(".")
            current = template

            for _i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Set the final value
            final_key = parts[-1]
            current[final_key] = f"TODO: Translate {key}"

        return template

    def find_unused_keys(
        self, translation_keys: set[str], source_keys: set[str] | None = None
    ) -> set[str]:
        """Find translation keys that are not used in source code.

        Args:
            translation_keys: Keys from translation files
            source_keys: Keys from source code (uses extracted keys if None)

        Returns:
            Set of unused translation keys
        """
        if source_keys is None:
            source_keys = self.keys

        return translation_keys - source_keys

    def find_missing_keys(
        self, translation_keys: set[str], source_keys: set[str] | None = None
    ) -> set[str]:
        """Find keys used in source code but missing from translations.

        Args:
            translation_keys: Keys from translation files
            source_keys: Keys from source code (uses extracted keys if None)

        Returns:
            Set of missing translation keys
        """
        if source_keys is None:
            source_keys = self.keys

        return source_keys - translation_keys

    def validate_placeholders(self, translations: dict[str, Any]) -> list[str]:
        """Validate that placeholders match across translations.

        Args:
            translations: Dictionary of translations by locale

        Returns:
            List of validation errors
        """
        errors = []
        placeholder_pattern = re.compile(r"\{(\w+)\}")

        # Get all keys from all locales
        all_keys: set[str] = set()
        for locale_translations in translations.values():
            all_keys.update(self._flatten_dict(locale_translations).keys())

        for key in all_keys:
            placeholders_by_locale = {}

            # Extract placeholders from each locale
            for locale, locale_translations in translations.items():
                flat = self._flatten_dict(locale_translations)
                if key in flat:
                    value = flat[key]
                    if isinstance(value, str):
                        placeholders = set(placeholder_pattern.findall(value))
                        placeholders_by_locale[locale] = placeholders

            # Compare placeholders across locales
            if len(placeholders_by_locale) > 1:
                first_locale = next(iter(placeholders_by_locale))
                first_placeholders = placeholders_by_locale[first_locale]

                for locale, placeholders in placeholders_by_locale.items():
                    if locale != first_locale and placeholders != first_placeholders:
                        errors.append(
                            f"Placeholder mismatch for key '{key}': "
                            f"{first_locale}={first_placeholders}, {locale}={placeholders}"
                        )

        return errors

    def _flatten_dict(self, d: dict, parent_key: str = "") -> dict[str, Any]:
        """Flatten nested dictionary with dot notation keys."""
        items: list[tuple[str, Any]] = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key).items())
            else:
                items.append((new_key, v))
        return dict(items)


def extract_and_update(
    source_dir: Path,
    translations_dir: Path,
    locales: list[str] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Extract keys and update translation files.

    Args:
        source_dir: Directory containing source code
        translations_dir: Directory containing translation files
        locales: Locales to update (defaults to all existing)
        dry_run: If True, don't write changes

    Returns:
        Report of changes made
    """
    import json

    extractor = TranslationExtractor()
    report: dict[str, Any] = {
        "extracted_keys": 0,
        "missing_keys": {},
        "unused_keys": {},
        "updated_files": [],
    }

    # Extract keys from source
    source_keys = extractor.extract_from_directory(source_dir)
    report["extracted_keys"] = len(source_keys)
    logger.info(f"Extracted {len(source_keys)} translation keys from source")

    # Get locales to process
    if locales is None:
        locales = [f.stem for f in translations_dir.glob("*.json")]

    for locale in locales:
        file_path = translations_dir / f"{locale}.json"

        # Load existing translations
        if file_path.exists():
            with Path(file_path).open(encoding="utf-8") as f:
                translations = json.load(f)
        else:
            translations = {}

        # Flatten to get all keys
        flat_translations = extractor._flatten_dict(translations)
        translation_keys = set(flat_translations.keys())

        # Find missing and unused keys
        missing = extractor.find_missing_keys(translation_keys, source_keys)
        unused = extractor.find_unused_keys(translation_keys, source_keys)

        report["missing_keys"][locale] = list(missing)
        report["unused_keys"][locale] = list(unused)

        if missing:
            logger.info(f"{locale}: {len(missing)} missing keys")

        if unused:
            logger.warning(f"{locale}: {len(unused)} unused keys")

        # Add missing keys
        if missing and not dry_run:
            template = extractor.generate_template(missing)

            # Merge template into existing translations
            def merge_nested(target, source) -> None:
                for key, value in source.items():
                    if key not in target:
                        target[key] = value
                    elif isinstance(target[key], dict) and isinstance(value, dict):
                        merge_nested(target[key], value)

            merge_nested(translations, template)

            # Save updated translations
            with Path(file_path).open("w", encoding="utf-8") as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)

            report["updated_files"].append(str(file_path))
            logger.info("Updated %s", file_path)

    return report


__all__ = ["TranslationExtractor", "extract_and_update"]
