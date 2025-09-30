#!/usr/bin/env python3
"""Parse detect-secrets output and create GitHub annotations."""

from __future__ import annotations

import re
import subprocess  # noqa: S404
import sys


def main() -> int:
    """Run detect-secrets and create GitHub annotations."""
    result = subprocess.run(
        ["detect-secrets", "scan", "--baseline", ".secrets.baseline"],
        capture_output=True,
        text=True,
        check=False,
    )

    # Print original output for logs
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    # Parse output for secrets found
    # Format: Location:    path/to/file.py:123
    lines = result.stderr.splitlines()

    for i, line in enumerate(lines):
        if line.startswith("Secret Type:"):
            secret_type = line.split(":", 1)[1].strip()

            # Look for location on next line
            if i + 1 < len(lines) and lines[i + 1].startswith("Location:"):
                location = lines[i + 1].split(":", 1)[1].strip()

                # Parse file:line
                match = re.match(r"^(.+?):(\d+)$", location)
                if match:
                    file_path, line_num = match.groups()
                    msg = f"Potential secret detected: {secret_type}"
                    print(f"::error title=Detect-Secrets,file={file_path},line={line_num}::{msg}")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
