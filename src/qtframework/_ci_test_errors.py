"""Test file to trigger CI check errors - DELETE AFTER TESTING."""

# Ruff errors
from __future__ import annotations

import os  # Unused import - triggers F401
import sys  # Unused import


x = 1 + 2  # Missing spaces around operators - triggers E225


def bad_function():  # Extra spaces in function def - triggers E201/E202
    pass


# Type checking errors (mypy)
def untyped_function(x):  # Missing type annotations
    return x + "string"  # Type error if x is not string


# Pyupgrade errors (outdated syntax)
x = dict()  # Should use {} - triggers UP018
y = list()  # Should use [] - triggers UP018

# Detect-secrets test (fake secret patterns)
api_key = "FAKE_API_KEY_12345678901234567890"  # Fake API key pattern
password = "hardcoded_password_here"  # Hardcoded password pattern

print(x)
