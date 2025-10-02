#!/usr/bin/env python3
"""Parse ruff output and create clean GitHub annotations."""

from __future__ import annotations

import subprocess  # noqa: S404
import sys


def main() -> int:
    """Run ruff and create GitHub annotations with clean messages."""
    # Run ruff check with JSON output for easier parsing
    result = subprocess.run(
        ["ruff", "check", "src", "tests", "examples", "scripts", "--output-format=json"],
        capture_output=True,
        text=True,
        check=False,
    )

    if not result.stdout.strip():
        return result.returncode

    import json

    try:
        violations = json.loads(result.stdout)
    except json.JSONDecodeError:
        # Fallback to parsing the default format
        return result.returncode

    for violation in violations:
        file = violation.get("filename", "")
        line = violation.get("location", {}).get("row", 0)
        col = violation.get("location", {}).get("column", 0)
        end_line = violation.get("end_location", {}).get("row", line)
        end_col = violation.get("end_location", {}).get("column", col)
        code = violation.get("code", "")
        message = violation.get("message", "")

        # Create annotation with just the code and message (no duplicate file:line)
        annotation_type = "error" if violation.get("fix") is None else "warning"
        title = f"Ruff ({code})" if code else "Ruff"

        print(
            f"::{annotation_type} title={title},file={file},line={line},col={col},"
            f"endLine={end_line},endColumn={end_col}::{code}: {message}"
        )

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
