Quick smoke tests
# health
curl http://127.0.0.1:5001/api/v1/health

# list sources (adjust path if needed)
curl http://127.0.0.1:5001/api/v1/sources

# run tests
cd ..
pytest -q