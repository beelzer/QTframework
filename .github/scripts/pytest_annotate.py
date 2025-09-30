#!/usr/bin/env python3
"""Parse pytest output and create GitHub annotations."""

from __future__ import annotations

import re
import subprocess  # noqa: S404
import sys


def main() -> int:
    """Run pytest and create GitHub annotations for failures."""
    # Build pytest command from command line args
    pytest_args = sys.argv[1:] if len(sys.argv) > 1 else ["tests/", "-v"]

    result = subprocess.run(  # noqa: S603
        ["pytest", *pytest_args],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )

    # Print original output for logs
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    # Parse pytest output for failures
    # Format: tests/path/test_file.py::test_name FAILED
    # Followed by file:line: in the traceback
    lines = result.stdout.splitlines()

    for i, line in enumerate(lines):
        # Look for FAILED test lines
        if " FAILED" in line or " ERROR" in line:
            # Extract test file and name
            match = re.match(r"^(.+?)::([\w\[\]_-]+)\s+(FAILED|ERROR)", line)
            if match:
                test_file, test_name, status = match.groups()

                # Look ahead for the actual error location in traceback
                error_file = test_file
                error_line = 1
                error_msg = f"Test {status.lower()}: {test_name}"

                # Scan next lines for traceback info
                for j in range(i + 1, min(i + 50, len(lines))):
                    # Look for file:line: pattern in traceback
                    traceback_match = re.match(r"^(.+?):(\d+):\s*(.+)", lines[j])
                    if traceback_match:
                        error_file, error_line, _ = traceback_match.groups()
                        break

                    # Look for assertion errors or exceptions
                    if "AssertionError" in lines[j] or "Error:" in lines[j]:
                        error_msg = lines[j].strip()
                        break

                    # Look for "E       " lines (pytest error details)
                    if lines[j].startswith("E       "):
                        error_msg = lines[j].replace("E       ", "").strip()
                        break

                print(f"::error title=Pytest,file={error_file},line={error_line}::{error_msg}")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
