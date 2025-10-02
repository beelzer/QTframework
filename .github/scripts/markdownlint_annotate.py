#!/usr/bin/env python3
"""Parse markdownlint output and create GitHub annotations."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from annotation_utils import Annotation, parse_json_output, run_tool


def create_markdownlint_config() -> str:
    """Create a temporary .markdownlint.json config file from pyproject.toml."""
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[import-not-found]

    # Read markdownlint config from pyproject.toml
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        return "{}"

    with pyproject_path.open("rb") as f:
        config = tomllib.load(f)

    markdownlint_config = config.get("tool", {}).get("markdownlint", {})

    # Convert to markdownlint JSON format
    json_config = dict(markdownlint_config)

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(json_config, f)
        return f.name


def parse_markdownlint_output(result) -> list[Annotation]:
    """Parse markdownlint JSON output into annotations."""
    violations = parse_json_output(result, prefer_stderr=True)
    if not violations:
        return []

    annotations = []
    for error in violations:
        file = error.get("fileName", "")
        line = error.get("lineNumber", 0)
        rule_names = error.get("ruleNames", [])
        rule_description = error.get("ruleDescription", "")
        error_detail = error.get("errorDetail", "")
        error_context = error.get("errorContext", "")

        # Format the rule code (usually like "MD001")
        rule_code = rule_names[0] if rule_names else "Markdownlint"

        # Build message
        message = rule_description
        if error_detail:
            message += f": {error_detail}"
        if error_context:
            message += f" [{error_context}]"

        annotations.append(
            Annotation(
                file=file,
                line=line,
                message=message,
                title=f"Markdownlint ({rule_code})",
            )
        )

    return annotations


def main() -> int:
    """Run markdownlint and create GitHub annotations."""
    # Create config file
    config_file = create_markdownlint_config()

    try:
        # Determine the npx command (npx.cmd on Windows)
        import platform

        npx_cmd = "npx.cmd" if platform.system() == "Windows" else "npx"

        # Run markdownlint with JSON output
        return run_tool(
            [
                npx_cmd,
                "--yes",
                "markdownlint-cli",
                ".",
                "--config",
                config_file,
                "--ignore",
                "node_modules",
                "--json",
            ],
            parse_markdownlint_output,
        )
    finally:
        # Clean up temp config file
        Path(config_file).unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
