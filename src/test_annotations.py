"""Test file to trigger CI annotations."""

from __future__ import annotations


# import os
# import subprocess  # Should trigger bandit B404


# def bad_function():
#     """This has multiple issues."""
#     # Ruff: unused variable
#     unused_var = 42

#     # Bandit: hardcoded password (B105)
#     password = "hardcoded_password_123"  # pragma: allowlist secret

#     # Bandit: eval usage (B307)
#     result = eval("1+1")

#     # Bandit: shell=True (B602)
#     subprocess.run("ls -la", check=False, shell=True)

#     # Ruff: undefined name
#     print(undefined_variable)

#     # Ruff: bare except
#     try:
#         risky_operation()
#     except:
#         pass


def type_errors() -> int:
    """Function with type checking errors."""
    # Type error: returning string instead of int
    return "not an integer"


def wrong_args() -> str:
    """Type error: wrong argument types."""
    # Type error: passing int to function expecting str
    result: str = len("hello")  # len returns int, not str
    print(result)  # Use it to avoid RET504
    return result


def incompatible_types() -> list[int]:
    """Type error: incompatible type assignments."""
    numbers: list[int] = [1, 2, 3]
    # Type error: assigning string to list[int]
    numbers = "not a list"
    print(numbers)  # Use it to avoid RET504
    return numbers


def missing_return_type():
    """Type error: inconsistent return types."""
    if True:
        return 42
    return "string"  # Type error: inconsistent return types


class BadClass:
    """Class with type errors."""

    def __init__(self, value: int):
        self.value = value

    def method(self) -> str:
        # Type error: returning int instead of str
        return self.value


def use_bad_class():
    """Type errors with class usage."""
    # Type error: passing string instead of int
    obj = BadClass("not an int")

    # Type error: accessing non-existent attribute
    result = obj.nonexistent_attribute
    print(result)  # Use it to avoid RET504

    return result
