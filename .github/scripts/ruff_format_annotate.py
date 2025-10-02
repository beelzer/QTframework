#!/usr/bin/env python3
"""Parse ruff format output and create GitHub annotations."""

from __future__ import annotations

import subprocess  # noqa: S404
import sys


def main() -> int:
    """Run ruff format and create annotations for files that need formatting."""
    result = subprocess.run(
        ["ruff", "format", "--check", "src", "tests", "examples", "scripts"],
        capture_output=True,
        text=True,
        check=False,
    )

    # Parse output looking for "Would reformat: filename"
    needs_formatting = []
    for line in result.stdout.splitlines():
        if line.strip().startswith("Would reformat:"):
            filename = line.split(":", 1)[1].strip()
            needs_formatting.append(filename)

    # Create GitHub annotations
    for filename in needs_formatting:
        print(
            f"::error title=Ruff Format,file={filename},line=1::File needs formatting. Run `ruff format {filename}` to fix."
        )

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
