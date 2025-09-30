#!/usr/bin/env python3
"""Parse prettier output and create GitHub annotations."""

from __future__ import annotations

import subprocess  # noqa: S404
import sys


def main() -> int:
    """Run prettier and create GitHub annotations."""
    # Install prettier
    subprocess.run(
        ["npm", "install", "-g", "prettier@3.4.2", "prettier-plugin-toml"],
        check=False,
    )

    # Run prettier check
    result = subprocess.run(
        [
            "prettier",
            "--check",
            "**/*.{json,yaml,yml,md}",
            "--ignore-path",
            ".gitignore",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    # Print output
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    # Parse output for files that need formatting
    # Format: [warn] path/to/file.json
    print(f"DEBUG: About to parse {len(result.stdout.splitlines())} lines")
    for line in result.stdout.splitlines():
        print(f"DEBUG: Checking line: '{line}'")
        if line.startswith("[warn]"):
            file_path = line.replace("[warn]", "").strip()
            print(f"DEBUG: Found [warn] line, file_path='{file_path}'")
            if file_path and not file_path.startswith("Code style issues"):
                msg = f"File needs formatting. Run `prettier --write {file_path}` to fix."
                print(f"::error title=Prettier,file={file_path},line=1::{msg}")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
