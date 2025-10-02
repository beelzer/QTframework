#!/usr/bin/env python3
"""Parse mypy output and create GitHub annotations."""

from __future__ import annotations

import re
import subprocess  # noqa: S404
import sys


def main() -> int:
    """Run mypy and create GitHub annotations."""
    result = subprocess.run(
        ["mypy", "src"],
        capture_output=True,
        text=True,
        check=False,
    )

    # Parse mypy output format: file.py:line:col: error: message [code]
    pattern = re.compile(r"^(.+?):(\d+):(\d+):\s+(error|warning|note):\s+(.+?)(?:\s+\[(.+?)\])?$")

    lines = result.stdout.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        match = pattern.match(line)
        if match:
            file, line_num, col, severity, message, code = match.groups()

            # Collect continuation lines (indented lines after error)
            full_message = message
            j = i + 1
            while j < len(lines) and (lines[j].startswith(" " * 4) or not lines[j].strip()):
                if lines[j].strip():
                    full_message += " " + lines[j].strip()
                j += 1

            code_str = f" [{code}]" if code else ""
            annotation_type = "error" if severity == "error" else "warning"

            print(
                f"::{annotation_type} title=Mypy{code_str},file={file},line={line_num},col={col}::{full_message}"
            )
            i = j
        else:
            i += 1

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
