#!/usr/bin/env python3
"""Run pytest with annotation support for future Python compatibility issues."""

from __future__ import annotations

import subprocess  # noqa: S404
import sys


def main() -> int:
    """Run pytest and create GitHub annotations for failures."""
    # Build pytest command from command line args
    pytest_args = sys.argv[1:] if len(sys.argv) > 1 else ["tests/", "-v"]

    # Try to import pytest first to catch import errors from incompatible deps
    try:
        import pytest  # noqa: F401
    except ImportError as e:
        # Create annotation for dependency compatibility issue
        print(
            f"::warning title=Future Python Compatibility::Unable to import pytest on Python {sys.version_info.major}.{sys.version_info.minor}: {e}"
        )
        print(
            f"Dependency not compatible with Python {sys.version_info.major}.{sys.version_info.minor}: {e}"
        )
        return 0  # Don't fail the job since this is experimental

    result = subprocess.run(
        ["python", ".github/scripts/pytest_annotate.py", *pytest_args],
        check=False,
    )

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
