---
name: avoid-modification-of-tests
description: Use when fixing bugs, writing tests, or modifying codebase to comply with testing and coding standards.
---
# Testing and Bug-fixing Guidelines

1. Tests and Code Modifications:
   - Do not modify existing test files in `tests/`. Add new regression tests in `tests/test_regressions.py`.
   - Add type hints to all new or modified functions.
   - Run tests using `pytest` via the shell to verify fixes.
   - If tests fail, inspect the failure trace and fix the implementation instead of re-running unchanged commands.

2. Common implementation pitfalls:
   - Rounding monetary values: use decimal `ROUND_HALF_UP`.
   - Parsing prices: support negative accounting format in parentheses e.g. `(12.00)` as negative.