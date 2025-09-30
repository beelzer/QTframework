"""Test file to trigger CI annotations."""

import os
import subprocess  # Should trigger bandit B404

def bad_function():
    """This has multiple issues."""
    # Ruff: unused variable
    unused_var = 42

    # Bandit: hardcoded password (B105)
    password = "hardcoded_password_123"

    # Bandit: eval usage (B307)
    result = eval("1+1")

    # Bandit: shell=True (B602)
    subprocess.run("ls -la", shell=True)

    # Ruff: undefined name
    print(undefined_variable)

    # Ruff: bare except
    try:
        risky_operation()
    except:
        pass