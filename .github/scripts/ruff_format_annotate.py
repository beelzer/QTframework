#!/usr/bin/env python3
"""Parse ruff format output and create GitHub annotations."""

from __future__ import annotations

import sys

from annotation_utils import Annotation, run_tool


def parse_ruff_format_output(result) -> list[Annotation]:
    """Parse ruff format text output into annotations."""
    # Parse output looking for "Would reformat: filename"
    annotations = []
    for line in result.stdout.splitlines():
        if line.strip().startswith("Would reformat:"):
            filename = line.split(":", 1)[1].strip()
            annotations.append(
                Annotation(
                    file=filename,
                    line=1,
                    message=f"File needs formatting. Run `ruff format {filename}` to fix.",
                    title="Ruff Format",
                )
            )

    return annotations


def main() -> int:
    """Run ruff format and create annotations for files that need formatting."""
    return run_tool(
        ["ruff", "format", "--check", "src", "tests", "examples", "scripts"],
        parse_ruff_format_output,
    )


if __name__ == "__main__":
    sys.exit(main())
