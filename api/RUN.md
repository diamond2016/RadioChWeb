# Running the API from the `api/` folder

If you run `uvicorn` from inside the `api/` directory, you need to ensure the repository root is on `PYTHONPATH` so `import api...` works.

Options:

- From `api/` directly:

```bash
PYTHONPATH=.. uvicorn main:app --reload --port 5001
```

- Or use the included helper script (from `api/`):

```bash
./run_uvicorn.sh
```

Notes:
- The helper script sets `PYTHONPATH` to the repo root and then execs `uvicorn`.
- Alternatively, run from the repository root with `uvicorn api.main:app`.
