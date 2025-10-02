#!/usr/bin/env python3
"""Parse markdownlint output and create GitHub annotations."""

from __future__ import annotations

import json
import subprocess  # noqa: S404
import sys
import tempfile
from pathlib import Path


def create_markdownlint_config() -> str:
    """Create a temporary .markdownlint.json config file from pyproject.toml."""
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

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


def main() -> int:
    """Run markdownlint and create GitHub annotations."""
    # Create config file
    config_file = create_markdownlint_config()

    try:
        # Determine the npx command (npx.cmd on Windows)
        import platform

        npx_cmd = "npx.cmd" if platform.system() == "Windows" else "npx"

        # Run markdownlint with JSON output
        result = subprocess.run(
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
            capture_output=True,
            text=True,
            check=False,
        )

        if not result.stdout.strip():
            return result.returncode

        try:
            violations = json.loads(result.stdout)
        except json.JSONDecodeError:
            print("Failed to parse markdownlint JSON output", file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return result.returncode

        # violations is an array of error objects
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

            print(f"::error title=Markdownlint ({rule_code}),file={file},line={line}::{message}")

        return result.returncode
    finally:
        # Clean up temp config file
        Path(config_file).unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
