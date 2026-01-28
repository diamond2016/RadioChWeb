import sys
import types
from unittest.mock import MagicMock

# Stub the API service module to isolate the routes from the business logic and database.
# This prevents the test from requiring a Flask application context or a real database.
service_mod = types.ModuleType("api.services.radio_source_api_service")

class MockRadioSourceList:
    def __init__(self):
        self.items = []
        self.total = 0
        self.page = 1
        self.page_size = 0
    def dict(self): return self.__dict__
    def model_dump(self, **kwargs): return self.__dict__

class RadioSourceAPIService:
    def __init__(self, *args, **kwargs):
        pass
    def get_all_radio_sources(self):
        return MockRadioSourceList()
    def get_radio_source(self, _id):
        return None
    def get_listen_metadata(self, _id):
        return None


service_mod.RadioSourceAPIService = RadioSourceAPIService
sys.modules["api.services.radio_source_api_service"] = service_mod
# Also stub as 'services.radio_source_api_service' to handle different import styles
sys.modules["services.radio_source_api_service"] = service_mod

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_list_sources_smoke():
    resp = client.get("/api/v1/sources/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert set(["items", "total", "page", "page_size"]).issubset(data.keys())
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)
    assert isinstance(data["page"], int)
    assert isinstance(data["page_size"], int)


def test_get_radio_source_not_found_smoke():
    resp = client.get("/api/v1/sources/999")
    assert resp.status_code == 404
    data = resp.json()
    assert isinstance(data, dict)

def test_get_radio_source_found_smoke():
    resp = client.get("/api/v1/sources/1")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)

