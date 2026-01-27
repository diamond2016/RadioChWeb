#!/usr/bin/env bash
set -euo pipefail

# Convenient helper to run the API from the `api/` folder while
# ensuring the repository root is on PYTHONPATH so `import api...` works.

export PYTHONPATH="$(pwd)/.."
echo "PYTHONPATH=$PYTHONPATH"

# Run uvicorn with the app defined in main.py
exec uvicorn main:app --reload --port 5001
