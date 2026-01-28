PYTHONPATH=.. uvicorn main:app --reload --port 5001
# health
curl http://127.0.0.1:5001/api/v1/health

# list stream types (adjust path if needed)
curl http://127.0.0.1:5001/api/v1/stream_types

# listen single stream_type
curl http://127.0.0.1:5001/api/v1/stream_types/1

# list sources (adjust path if needed)
curl http://127.0.0.1:5001/api/v1/sources

# list single radio source (adjust path if needed)
curl http://127.0.0.1:5001/api/v1/sources/2

# run tests
cd ..
pytest -q

NOTE ON TESTS
Added test: test_stream_type_api_service.py — 3 pytest cases.
Updated: conftest.py — add repo root to sys.path.
Note: the test injects lightweight stubs for DB/models to avoid SQLAlchemy/DB setup; remove stubs once you want full integration.

In FastAPI tests SimplenameSpace is used to mock services.

In Python testing, types.SimpleNamespace is often used to create lightweight, "dummy" objects that mimic the structure of a database model or a complex class without the overhead of actual instantiation or database connectivity.

What is SimpleNamespace?
SimpleNamespace is a class that provides attribute access to its namespace, as well as a meaningful repr. It is essentially a dictionary that allows dot notation obj.attribute.

Why use it instead of unittest.mock.Mock?
While Mock is powerful for tracking calls and defining dynamic behavior, SimpleNamespace is preferred when you only need a data holder that behaves like a simple object.

Readability: It looks and acts like a real object or a Pydantic model.
No Side Effects: It doesn't track calls or have the "magical" qualities of Mock that can sometimes lead to false positives in tests (e.g., calling a non-existent method on a Mock usually returns another Mock rather than raising an AttributeError).
Static Data: It is perfect for faking database rows returned by a service.

Example in test_get_stream_type
In your project, the StreamTypeApiService likely expects objects with specific attributes (like id and name). Instead of creating a real SQLAlchemy model instance (which might require a database session), a SimpleNamespace is used.

Here is how it is typically applied in your testing context:
from types import SimpleNamespace
from unittest.mock import MagicMock

def test_get_stream_type():
```python
    # 1. Create a "fake" domain object using SimpleNamespace
    # This mimics a database record for a StreamType
    fake_stream_type = SimpleNamespace(id=1, name="Standard Stream")

    # 2. Mock the service or repository
    mock_service = MagicMock()
    
    # 3. Configure the mock to return our SimpleNamespace object
    mock_service.get_by_id.return_value = fake_stream_type

    # 4. Execution
    result = mock_service.get_by_id(1)

    # 5. Assertion
    # result behaves like an object with .id and .name
    assert result.id == 1
    assert result.name == "Standard Stream"
```