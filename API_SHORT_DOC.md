API Short Doc — RadioChWeb (API layer)
=====================================

Summary
-------
- This repository includes a FastAPI-based API under the `api/` folder providing read-only endpoints for radio sources and stream types.
- Current prefix for API routes: `/api/v1` (see `api/main.py`).

Key endpoints
-------------
- GET `/api/v1/sources/` — list radio sources (supports basic query params; pagination).
- GET `/api/v1/sources/{id}` — get details for a single radio source.
- GET `/api/v1/sources/{id}/listen` — minimal metadata for opening the stream.
- GET `/api/v1/stream_types/` — list available stream types.

Run locally
-----------
1. Create and activate virtualenv (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

2. Run the API (development):

```bash
cd api
export PYTHONPATH=..  # ensure project root is importable
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Testing
-------
- API tests live under `api/tests/`. Run the API tests only with:

```bash
# from repo root
.venv/bin/python -m pytest -q api/tests/test_routes_radio_sources.py
```

Notes
-----
- The API layer uses lightweight adapter services in `api/services`. These adapt the main application's services and repositories so tests can stub them cleanly.
- If you plan to push the local merge to the remote, ensure you have a clean remote `main` state or rebase/coordinate with collaborators.

Contact
-------
For more details about the application architecture, see `ARCHITECTURE.md` and `web-interface.md`.
