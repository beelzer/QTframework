#!/usr/bin/env python3
"""Generate benchmark summary from pytest-benchmark results."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def generate_summary(
    input_file: str = "benchmark-results.json", output_file: str = "benchmark-summary.md"
) -> None:
    """Generate markdown summary from benchmark results."""
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Benchmark results file {input_file} not found")
        sys.exit(1)

    with input_path.open(encoding="utf-8") as f:
        data = json.load(f)

    summary = [
        {
            "name": bench["name"],
            "min": bench["stats"]["min"],
            "mean": bench["stats"]["mean"],
            "max": bench["stats"]["max"],
        }
        for bench in data.get("benchmarks", [])
    ]

    # Write summary
    with Path(output_file).open("w", encoding="utf-8") as f:
        f.write("## ⚡ Performance Benchmarks\n\n")
        f.write("| Test | Min (s) | Mean (s) | Max (s) |\n")
        f.write("|------|---------|----------|---------|\\n")
        f.writelines(
            f"| {s['name']} | {s['min']:.4f} | {s['mean']:.4f} | {s['max']:.4f} |\n"
            for s in summary
        )

    print(f"Benchmark summary written to {output_file}")


if __name__ == "__main__":
    generate_summary()
