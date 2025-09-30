#!/usr/bin/env python3
"""Parse bandit JSON output and create GitHub annotations."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main():
    """Parse bandit report and output GitHub annotations."""
    report_file = Path("bandit-report.json")

    if not report_file.exists():
        print("No bandit report found")
        return 0

    with report_file.open(encoding="utf-8") as f:
        data = json.load(f)

    high_severity_found = False

    for result in data.get("results", []):
        severity = result.get("issue_severity", "UNKNOWN")
        issue = result.get("issue_text", "")
        file = result.get("filename", "")
        line = result.get("line_number", 1)
        test_id = result.get("test_id", "")

        # Only fail on Medium/High severity issues
        if severity in {"MEDIUM", "HIGH"}:
            print(f"::error file={file},line={line}::[{test_id}] {severity} - {issue}")
            high_severity_found = True
        else:
            print(f"::warning file={file},line={line}::[{test_id}] {severity} - {issue}")

    return 1 if high_severity_found else 0


if __name__ == "__main__":
    sys.exit(main())
