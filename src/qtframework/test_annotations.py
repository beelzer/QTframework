"""Minimal test file to trigger CI annotations - DELETE AFTER TESTING."""

import os  # Unused import - triggers Ruff F401

x=1+2  # Missing spaces - triggers Ruff E225

# Pyupgrade: outdated syntax
data = dict()  # Should be {} - triggers Ruff C408

# Detect-secrets: fake credentials
api_key = "my_secret_api_key_12345"  # Triggers detect-secrets
password = "hardcoded_pass"  # Triggers detect-secrets

# Mypy: missing type annotations
def add(a, b):  # Missing type hints
    return a + b
