#!/usr/bin/env python3
"""Parse Sphinx output and create GitHub annotations."""

from __future__ import annotations

import re
import subprocess  # noqa: S404
import sys


def main() -> int:
    """Run Sphinx build and create GitHub annotations for warnings/errors."""
    # Build sphinx command from command line args
    sphinx_args = sys.argv[1:] if len(sys.argv) > 1 else ["-b", "html", "docs", "docs/_build/html"]

    result = subprocess.run(
        ["sphinx-build", "-W", "--keep-going", *sphinx_args],
        capture_output=True,
        text=True,
        check=False,
    )

    # Print original output for logs
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    # Parse sphinx output for warnings and errors
    # Format: WARNING: /path/to/file.rst:123: message
    # Format: ERROR: /path/to/file.py:docstring of module.function:45: message
    output = result.stdout + result.stderr

    for line in output.splitlines():
        # Match WARNING or ERROR lines with file paths
        match = re.match(
            r"^(WARNING|ERROR):\s+(.+?):(\d+):\s*(.+)$",
            line,
        )
        if match:
            level, filepath, line_num, message = match.groups()
            annotation_type = "error" if level == "ERROR" else "warning"
            print(
                f"::{annotation_type} title=Sphinx {level},file={filepath},line={line_num}::{message}"
            )
            continue

        # Match warnings without line numbers
        match = re.match(
            r"^(WARNING|ERROR):\s+(.+?):\s*(.+)$",
            line,
        )
        if match:
            level, filepath, message = match.groups()
            # Skip if this looks like a generic message
            if "/" in filepath or "\\" in filepath:
                annotation_type = "error" if level == "ERROR" else "warning"
                print(f"::{annotation_type} title=Sphinx {level},file={filepath}::{message}")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
