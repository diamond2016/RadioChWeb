#!/usr/bin/env bash
set -euo pipefail

echo "Running root tests (top-level tests/) using ./.venv..."
# Run only the project's top-level `tests/` to avoid collecting `api/tests` here.
if [ -x "./.venv/bin/pytest" ]; then
  ./.venv/bin/pytest -q tests
else
  python3 -m pytest -q tests
fi

echo "Running api tests using api/.venv..."
if [ -x "api/.venv/bin/pytest" ]; then
  (cd api && ./.venv/bin/pytest -q)
else
  (cd api && python3 -m pytest -q)
fi

echo "All test suites completed successfully."
