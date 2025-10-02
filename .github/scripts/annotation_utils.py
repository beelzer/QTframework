"""Shared utilities for GitHub annotation scripts."""

from __future__ import annotations

import json
import subprocess  # noqa: S404
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class Annotation:
    """Represents a GitHub annotation.

    Attributes:
        file: File path
        line: Line number
        message: Annotation message
        title: Annotation title
        severity: Annotation severity (error, warning, notice)
        col: Column number (optional)
        end_line: End line number (optional)
        end_col: End column number (optional)
    """

    file: str
    line: int
    message: str
    title: str
    severity: str = "error"
    col: int | None = None
    end_line: int | None = None
    end_col: int | None = None

    def emit(self) -> None:
        """Print GitHub annotation to stdout."""
        parts = [
            f"file={self.file}",
            f"line={self.line}",
        ]
        if self.col is not None:
            parts.append(f"col={self.col}")
        if self.end_line is not None:
            parts.append(f"endLine={self.end_line}")
        if self.end_col is not None:
            parts.append(f"endColumn={self.end_col}")

        location = ",".join(parts)
        print(f"::{self.severity} title={self.title},{location}::{self.message}")


def run_tool(
    command: list[str],
    output_parser: Callable[[subprocess.CompletedProcess], list[Annotation]],
    print_output: bool = False,
) -> int:
    """Run a tool and create GitHub annotations.

    Args:
        command: Command to run with arguments
        output_parser: Function to parse tool output into annotations
        print_output: Whether to print the tool's stdout/stderr

    Returns:
        Return code from the tool
    """
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if print_output:
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

    try:
        annotations = output_parser(result)
        for annotation in annotations:
            annotation.emit()
    except Exception as e:
        print(f"Error parsing tool output: {e}", file=sys.stderr)
        # Print raw output for debugging
        print("STDOUT:", result.stdout[:500], file=sys.stderr)
        print("STDERR:", result.stderr[:500], file=sys.stderr)

    return result.returncode


def parse_json_output(result: subprocess.CompletedProcess, *, prefer_stderr: bool = False) -> Any:
    """Parse JSON output from a subprocess with error handling.

    Args:
        result: Completed subprocess result
        prefer_stderr: Check stderr first for JSON output

    Returns:
        Parsed JSON object or None if parsing fails
    """
    if prefer_stderr:
        output = result.stderr if result.stderr.strip() else result.stdout
    else:
        output = result.stdout if result.stdout.strip() else result.stderr

    if not output.strip():
        return None

    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return None
