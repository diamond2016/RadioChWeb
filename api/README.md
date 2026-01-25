# RadioChWeb — API (FastAPI) README

This folder contains a minimal FastAPI-based API skeleton for RadioChWeb. It is intended to run isolated from the main Flask app (separate virtualenv/container).

Quick start (local, isolated):

1. Create and activate a venv inside the `api/` directory:

```bash
python3 -m venv api/.venv
source api/.venv/bin/activate
```

2. Install dependencies:

```bash
pip install --upgrade pip setuptools wheel
pip install -r api/requirements.txt
```

3. Run the app (development):

```bash
uvicorn api.main:app --reload --port 5001
```

4. Smoke-check the health endpoint:

```bash
curl http://127.0.0.1:5001/health
# expected: {"status":"ok"}
```

Notes
- The API is scaffolded and exposes placeholder `sources` routes and a `/health` endpoint.
- Keep the API dependencies isolated from the Flask app to avoid conflicting packages (use `api/.venv` or a container).
- For production, containerize the API and the Flask app separately and run behind a proper ASGI/WSGI server.

Contributing
- Add API routes under `api/routes/`, Pydantic schemas under `api/schemas/`, and tests under `tests/api/`.
