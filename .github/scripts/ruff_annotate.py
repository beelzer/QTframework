#!/usr/bin/env python3
"""Parse ruff output and create clean GitHub annotations."""

from __future__ import annotations

import sys

from annotation_utils import Annotation, parse_json_output, run_tool


def parse_ruff_output(result) -> list[Annotation]:
    """Parse ruff JSON output into annotations."""
    violations = parse_json_output(result)
    if not violations:
        return []

    annotations = []
    for violation in violations:
        file = violation.get("filename", "")
        line = violation.get("location", {}).get("row", 0)
        col = violation.get("location", {}).get("column", 0)
        end_line = violation.get("end_location", {}).get("row", line)
        end_col = violation.get("end_location", {}).get("column", col)
        code = violation.get("code", "")
        message = violation.get("message", "")

        # Create annotation with just the code and message
        annotation_type = "error" if violation.get("fix") is None else "warning"
        title = f"Ruff ({code})" if code else "Ruff"

        annotations.append(
            Annotation(
                file=file,
                line=line,
                col=col,
                end_line=end_line,
                end_col=end_col,
                message=f"{code}: {message}",
                title=title,
                severity=annotation_type,
            )
        )

    return annotations


def main() -> int:
    """Run ruff and create GitHub annotations with clean messages."""
    return run_tool(
        ["ruff", "check", "src", "tests", "examples", "scripts", "--output-format=json"],
        parse_ruff_output,
    )


if __name__ == "__main__":
    sys.exit(main())
