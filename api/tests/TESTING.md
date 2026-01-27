PYTHONPATH=.. uvicorn main:app --reload --port 5001
# health
curl http://127.0.0.1:5001/api/v1/health

# list stream types (adjust path if needed)
curl http://127.0.0.1:5001/api/v1/stream_types

# list sources (adjust path if needed)
curl http://127.0.0.1:5001/api/v1/sources

# run tests
cd ..
pytest -q

NOTE ON TESTS
Added test: test_stream_type_api_service.py — 3 pytest cases.
Updated: conftest.py — add repo root to sys.path.
Note: the test injects lightweight stubs for DB/models to avoid SQLAlchemy/DB setup; remove stubs once you want full integration.
