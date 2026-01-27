import sys
from types import SimpleNamespace
import importlib

# Ensure the top-level import `schemas.stream_type` resolves to the module
# we have under `api.schemas.stream_type` (api.schemas.radio_source imports it).
schemas_mod = importlib.import_module("api.schemas.stream_type")
sys.modules.setdefault("schemas.stream_type", schemas_mod)

# Minimal `database` stub so importing `api.service.*` modules doesn't pull
# in the real `database.py` (which imports SQLAlchemy and can fail in test
# environments with incompatible SQLAlchemy versions).
import types
_db_mod = types.ModuleType("database")
_db_mod.get_db_session = lambda: None
sys.modules.setdefault("database", _db_mod)

from api.service.radio_source_api_service import RadioSourceAPIService
from api.schemas.stream_type import StreamTypeOut as StreamTypeSchema


def _make_service(monkeypatch, dto_mappings):
    # radio_source_service stub using DTOs
    def _get_all():
        items = []
        for m in dto_mappings:
            st = m.get("stream_type")
            st_obj = SimpleNamespace(**st) if isinstance(st, dict) else SimpleNamespace(id=getattr(st, "id", st))
            item = SimpleNamespace(
                id=m.get("id"),
                stream_url=m.get("stream_url"),
                name=m.get("name"),
                is_secure=m.get("is_secure", False),
                stream_type=st_obj,
                country=m.get("country"),
            )
            items.append(item)
        return items

    def _get_one(id_):
        for m in dto_mappings:
            if m["id"] == id_:
                st = m.get("stream_type")
                st_obj = SimpleNamespace(**st) if isinstance(st, dict) else SimpleNamespace(id=getattr(st, "id", st))
                return SimpleNamespace(
                    id=m.get("id"),
                    stream_url=m.get("stream_url"),
                    name=m.get("name"),
                    is_secure=m.get("is_secure", False),
                    stream_type=st_obj,
                    country=m.get("country"),
                )
        return None

    radio_stub = SimpleNamespace(get_all_radio_sources=_get_all, get_radio_source=_get_one)

    # stream type API stub returns StreamType schema instances
    def _get_stream_type(st):
        # `st` may be a mapping or an id
        if isinstance(st, dict):
            sid = st.get("id")
        else:
            sid = getattr(st, "id", st)
        return StreamTypeSchema.model_validate({"id": sid, "display_name": f"type-{sid}"})

    stream_type_api = SimpleNamespace(get_stream_type=_get_stream_type)

    svc = RadioSourceAPIService(radio_source_service=radio_stub, stream_type_api_service=stream_type_api)
    return svc


def test_list_sources_empty(monkeypatch):
    svc = _make_service(monkeypatch, [])
    assert svc.list_sources() is None


def test_list_sources_filters_and_pagination(monkeypatch):
    dtos = [
        {"id": 1, "stream_url": "http://one", "name": "One Radio", "is_secure": False, "stream_type": {"id": 1, "protocol": "HTTP", "format": "MP3", "metadata_type": "None", "display_name": "t1"}, "country": "IT"},
        {"id": 2, "stream_url": "http://two", "name": "Two Station", "is_secure": False, "stream_type": {"id": 2, "protocol": "HTTP", "format": "AAC", "metadata_type": "None", "display_name": "t2"}, "country": "US"},
        {"id": 3, "stream_url": "http://three", "name": "Another One", "is_secure": False, "stream_type": {"id": 1, "protocol": "HTTP", "format": "MP3", "metadata_type": "None", "display_name": "t1"}, "country": "IT"},
    ]
    svc = _make_service(monkeypatch, dtos)

    items, total = svc.list_sources(q="one")
    assert total == 2
    assert len(items) == 2

    items, total = svc.list_sources(stream_type=2)
    assert total == 1
    assert items[0].id == 2

    items, total = svc.list_sources(country="IT")
    assert total == 2

    items, total = svc.list_sources(page=2, page_size=1)
    assert total == 3
    assert len(items) == 1
    assert items[0].id == 2


def test_get_source_and_listen_metadata(monkeypatch):
    dtos = [
        {"id": 5, "stream_url": "http://listen", "name": "ListenMe", "is_secure": False, "stream_type": {"id": 7, "protocol": "HTTP", "format": "MP3", "metadata_type": "None", "display_name": "t7"}, "country": "GB"}
    ]
    svc = _make_service(monkeypatch, dtos)

    src = svc.get_source(5)
    assert src is not None
    assert src.id == 5
    assert src.name == "ListenMe"

    meta = svc.get_listen_metadata(5)
    assert meta is not None
    assert meta.stream_url == "http://listen"
    assert hasattr(meta.stream_type, "id")
    assert meta.name == "ListenMe"

    assert svc.get_source(999) is None
    assert svc.get_listen_metadata(999) is None
