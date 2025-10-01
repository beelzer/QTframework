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

    print(f"Running: sphinx-build {' '.join(sphinx_args)}")

    result = subprocess.run(
        ["sphinx-build", "-W", "--keep-going", *sphinx_args],
        capture_output=True,
        text=True,
        check=False,
    )

    # Print original output for logs
    print("\n=== Sphinx Output ===")
    print(result.stdout)
    if result.stderr:
        print("\n=== Sphinx Errors ===", file=sys.stderr)
        print(result.stderr, file=sys.stderr)

    print(f"\n=== Exit Code: {result.returncode} ===")

    # Parse sphinx output for warnings and errors
    output = result.stdout + "\n" + result.stderr
    found_issues = False

    for line in output.splitlines():
        # Match various Sphinx error/warning formats
        # Format 1: WARNING: /path/to/file.rst:123: message
        match = re.match(r"^(WARNING|ERROR):\s+(.+?):(\d+):\s*(.+)$", line)
        if match:
            found_issues = True
            level, filepath, line_num, message = match.groups()
            annotation_type = "error" if level == "ERROR" else "warning"
            print(
                f"::{annotation_type} title=Sphinx {level},file={filepath},line={line_num}::{message}"
            )
            continue

        # Format 2: WARNING: message (no file)
        match = re.match(r"^(WARNING|ERROR):\s+(.+)$", line)
        if match:
            found_issues = True
            level, message = match.groups()
            annotation_type = "error" if level == "ERROR" else "warning"
            print(f"::{annotation_type} title=Sphinx {level}::{message}")
            continue

        # Format 3: Catch traceback errors
        if "Traceback (most recent call last):" in line:
            found_issues = True
            print("::error title=Sphinx Build Error::Build failed with exception - see logs")

        # Format 4: Extension errors
        if "Extension error:" in line:
            found_issues = True
            print(f"::error title=Sphinx Extension Error::{line}")

    # If build failed but no specific errors were found, create generic annotation
    if result.returncode != 0 and not found_issues:
        print(
            f"::error title=Sphinx Build Failed::Build failed with exit code {result.returncode}. Check logs for details."
        )

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
