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

    result = subprocess.run(
        ["pytest", *pytest_args],
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
            # Extract test file and name (including class::method format)
            match = re.match(r"^(.+?\.py)(::[\w\[\]_:-]+)+\s+(FAILED|ERROR)", line)
            if match:
                test_file = match.group(1)
                test_path = match.group(0).split(" ")[0]  # Full path including ::
                status = match.group(3)
                test_name = test_path.split("::")[-1]

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
                    # Look for file:line: pattern in traceback (multiple formats)
                    # Format 1: tests/path/test_file.py:43: in test_name
                    traceback_match = re.match(r"^(.+?):(\d+):\s*in\s+(.+)", lines[j])
                    if traceback_match:
                        file_path, line_num, _ = traceback_match.groups()
                        # Only update if it's the actual test file
                        if file_path == test_file:
                            error_file = file_path
                            error_line = line_num
                        continue

                    # Format 2: Look for assertion line references
                    # Example: "    assert timer.elapsed_ms < 1000  # Less than 1 second"
                    # Preceded by line like "tests/file.py:43: in test_method"
                    if lines[j].strip().startswith("assert ") and error_line == 1:
                        # Check previous lines for file:line
                        for k in range(max(0, j - 3), j):
                            prev_match = re.match(r"^(.+?):(\d+):", lines[k])
                            if prev_match and prev_match.group(1) == test_file:
                                error_line = prev_match.group(2)
                                break

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
