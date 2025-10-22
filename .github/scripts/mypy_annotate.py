#!/usr/bin/env python3
"""Parse mypy output and create GitHub annotations."""

from __future__ import annotations

import re
import sys

from annotation_utils import Annotation, run_tool


def parse_mypy_output(result) -> list[Annotation]:
    """Parse mypy text output into annotations."""
    # Parse mypy output format: file.py:line:col: error: message [code]
    pattern = re.compile(r"^(.+?):(\d+):(\d+):\s+(error|warning|note):\s+(.+?)(?:\s+\[(.+?)\])?$")

    annotations = []
    lines = result.stdout.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        match = pattern.match(line)
        if match:
            file, line_num, col, severity, message, code = match.groups()

            # Collect continuation lines
            # Mypy can split messages across lines in different ways:
            # 1. Continuation of the error message (no indentation, before code context)
            # 2. Code context lines (indented, can include ^~~ markers)
            full_message = message
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                # Stop if this is a new error (starts with file:line:col pattern)
                if re.match(r"^.+?:\d+:\d+:\s+(error|warning|note):", next_line):
                    break
                # Stop if this looks like a summary line
                if next_line.strip().startswith("Found ") or next_line.strip().startswith(
                    "Success:"
                ):
                    break
                # Stop if we hit the code context markers (lines with just ^~~)
                if re.match(r"^\s+\^[~^]+\s*$", next_line):
                    break
                # Include non-indented continuation lines (part of error message)
                # Skip code context lines (indented source code)
                if not next_line.startswith(" "):
                    if next_line.strip():
                        full_message += " " + next_line.strip()
                    j += 1
                else:
                    # This is indented - likely code context, skip it
                    j += 1

            code_str = f" [{code}]" if code else ""
            annotation_type = "error" if severity == "error" else "warning"

            annotations.append(
                Annotation(
                    file=file,
                    line=int(line_num),
                    col=int(col),
                    message=full_message,
                    title=f"Mypy{code_str}",
                    severity=annotation_type,
                )
            )
            i = j
        else:
            i += 1

    return annotations


def main() -> int:
    """Run mypy and create GitHub annotations."""
    return run_tool(
        ["mypy", "--config-file=config/mypy.ini", "src"],
        parse_mypy_output,
    )


if __name__ == "__main__":
    sys.exit(main())
