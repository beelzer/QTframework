#!/usr/bin/env python3
"""Parse prettier output and create GitHub annotations."""

from __future__ import annotations

import subprocess  # noqa: S404
import sys

from annotation_utils import Annotation, run_tool


def install_prettier() -> None:
    """Install prettier and plugins."""
    subprocess.run(
        ["npm", "install", "-g", "prettier@3.4.2", "prettier-plugin-toml"],
        check=False,
    )


def parse_prettier_output(result) -> list[Annotation]:
    """Parse prettier text output into annotations."""
    annotations = []
    # Prettier outputs to stderr, not stdout!
    output = result.stderr or result.stdout
    for line in output.splitlines():
        if line.startswith("[warn]"):
            file_path = line.replace("[warn]", "").strip()
            if file_path and not file_path.startswith("Code style issues"):
                msg = f"File needs formatting. Run `prettier --write {file_path}` to fix."
                annotations.append(
                    Annotation(
                        file=file_path,
                        line=1,
                        message=msg,
                        title="Prettier",
                    )
                )

    return annotations


def main() -> int:
    """Run prettier and create GitHub annotations."""
    # Install prettier
    install_prettier()

    # Run prettier check
    return run_tool(
        [
            "prettier",
            "--check",
            "**/*.{json,yaml,yml,md}",
            "--ignore-path",
            ".gitignore",
        ],
        parse_prettier_output,
        print_output=True,
    )


if __name__ == "__main__":
    sys.exit(main())
