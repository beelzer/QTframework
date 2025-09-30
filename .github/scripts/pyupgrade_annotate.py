#!/usr/bin/env python3
"""Parse pyupgrade output and create GitHub annotations."""

from __future__ import annotations

import re
import subprocess  # noqa: S404
import sys


def main() -> int:
    """Run pyupgrade and create GitHub annotations."""
    # Find all Python files
    result = subprocess.run(
        [
            "find",
            "src",
            "tests",
            "examples",
            "scripts",
            "-name",
            "*.py",
            "-type",
            "f",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    python_files = result.stdout.strip().split("\n")
    exit_code = 0

    for file_path in python_files:
        if not file_path:
            continue

        # Run pyupgrade on each file
        result = subprocess.run(
            ["pyupgrade", "--py313-plus", "--diff", file_path],
            capture_output=True,
            text=True,
            check=False,
        )

        # Print output for debugging
        if result.stdout:
            print(result.stdout)

        # Check if changes would be made (diff output present)
        if result.stdout.strip():
            exit_code = 1

            # Parse diff output to find line numbers
            # Format: @@ -line,count +line,count @@
            for line in result.stdout.splitlines():
                if line.startswith("@@"):
                    match = re.search(r"@@ -(\d+)", line)
                    if match:
                        line_num = match.group(1)
                        msg = "Code can be upgraded to Python 3.13+ syntax"
                        print(f"::warning title=Pyupgrade,file={file_path},line={line_num}::{msg}")
                        break  # Only show first occurrence per file

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
