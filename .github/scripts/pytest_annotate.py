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

    # Look for short test summary section for detailed error messages
    in_summary = False
    summary_errors = {}
    for line in lines:
        if line.startswith("=========================== short test summary info"):
            in_summary = True
            continue
        if in_summary and line.startswith("==="):
            break
        if in_summary and line.startswith("FAILED "):
            # Extract test path and error message
            # Format: FAILED test_file.py::test_name - assert message
            summary_match = re.match(r"FAILED (.+?) - (.+)", line)
            if summary_match:
                test_path, msg = summary_match.groups()
                summary_errors[test_path] = msg

    for i, line in enumerate(lines):
        # Look for FAILED test lines
        if " FAILED" in line or " ERROR" in line:
            # Extract test file and name
            match = re.match(r"^(.+?)::([\w\[\]_-]+)\s+(FAILED|ERROR)", line)
            if match:
                test_file, test_name, status = match.groups()
                test_path = f"{test_file}::{test_name}"

                # Look ahead for the actual error location in traceback
                error_file = test_file
                error_line = 1
                error_msg = f"Test {status.lower()}: {test_name}"

                # Check if we have a summary error message
                if test_path in summary_errors:
                    error_msg = summary_errors[test_path]

                # Scan next lines for traceback info
                error_details = []
                for j in range(i + 1, min(i + 100, len(lines))):
                    # Look for file:line: pattern in traceback
                    traceback_match = re.match(r"^(.+?):(\d+):\s*in (.+)", lines[j])
                    if traceback_match:
                        error_file, error_line, _ = traceback_match.groups()
                        continue

                    # Collect "E       " lines (pytest error details)
                    if lines[j].startswith("E       "):
                        detail = lines[j].replace("E       ", "").strip()
                        if detail:
                            error_details.append(detail)

                    # Stop at next test result or section
                    if lines[j].startswith(("====", "----", "PASSED", "FAILED", "ERROR")):
                        break

                # Build error message from collected details
                if error_details:
                    error_msg = " ".join(error_details[:3])  # First 3 lines of error

                print(f"::error title=Pytest,file={error_file},line={error_line}::{error_msg}")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
