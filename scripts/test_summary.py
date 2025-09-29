#!/usr/bin/env python3
"""Generate test summary from test results."""

from __future__ import annotations

import json
from pathlib import Path


def generate_test_summary(input_file: str = "test-results.json") -> None:
    """Generate test summary for GitHub Actions."""
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Test results file {input_file} not found")
        return

    with input_path.open(encoding="utf-8") as f:
        data = json.load(f)

    failed_tests = [
        f"❌ {test.get('name', 'Unknown test')}"
        for test in data.get("tests", [])
        if test.get("outcome") == "failed"
    ]

    if failed_tests:
        print("### Failed Tests")
        for test in failed_tests:
            print(test)
    else:
        print("✅ All tests passed!")


if __name__ == "__main__":
    generate_test_summary()
