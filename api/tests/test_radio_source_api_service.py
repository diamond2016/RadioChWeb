import sys
import types


# Provide a fake 'db' module so importing `api.deps` doesn't fail during tests
_db_mod = types.ModuleType("db")
class _DummySession:
    def close(self):
        pass
def _dummy_session_local():
    return _DummySession()
_db_mod.SessionLocal = _dummy_session_local
sys.modules["db"] = _db_mod


# Stub repository modules used by the service import-time references
_m_repo_rs = types.ModuleType("model.repository.radio_source_repository")
class _StubRSRepo:
    pass
_m_repo_rs.RadioSourceRepository = _StubRSRepo
sys.modules["model.repository.radio_source_repository"] = _m_repo_rs

_m_repo_prop = types.ModuleType("model.repository.proposal_repository")
class _StubPropRepo:
    pass
_m_repo_prop.ProposalRepository = _StubPropRepo
sys.modules["model.repository.proposal_repository"] = _m_repo_prop

_m_repo_st = types.ModuleType("model.repository.stream_type_repository")
class _StubSTRepo:
    pass
_m_repo_st.StreamTypeRepository = _StubSTRepo
sys.modules["model.repository.stream_type_repository"] = _m_repo_st


# Minimal DTO and entity stubs so imports succeed
_m_dto = types.ModuleType("model.dto.radio_source")
class RadioSourceDTO:
    def __init__(self, id: int, name: str, stream_type_id: int, country: str, stream_url: str):
        self.id = id
        self.name = name
        self.stream_type = types.SimpleNamespace(id=stream_type_id)
        self.country = country
        self.stream_url = stream_url
_m_dto.RadioSourceDTO = RadioSourceDTO
sys.modules["model.dto.radio_source"] = _m_dto

# Stub the model entity module to avoid importing SQLAlchemy constructs during tests
_m_entity_rs = types.ModuleType("model.entity.radio_source")
class RadioSource:
    pass
_m_entity_rs.RadioSource = RadioSource
sys.modules["model.entity.radio_source"] = _m_entity_rs


# Stub minimal schema classes with `model_validate` used by the API service
_m_schema = types.ModuleType("api.schemas.radio_source")
class RadioSourceOut:
    def __init__(self, dto):
        # accept either DTO or mapping
        if hasattr(dto, "id"):
            self.id = dto.id
            self.name = dto.name
            self.stream_type = dto.stream_type
            self.country = getattr(dto, "country", None)
            self.stream_url = getattr(dto, "stream_url", None)
        else:
            self.id = dto.get("id")
            self.name = dto.get("name")
            self.stream_type = dto.get("stream_type")
            self.country = dto.get("country")
            self.stream_url = dto.get("stream_url")

    @classmethod
    def model_validate(cls, data):
        return cls(data)


class RadioSourceListenMetadata:
    def __init__(self, mapping):
        self.stream_url = mapping.get("stream_url")
        self.stream_type = mapping.get("stream_type")
        self.name = mapping.get("name")

    @classmethod
    def model_validate(cls, mapping):
        return cls(mapping)


_m_schema.RadioSourceOut = RadioSourceOut
_m_schema.RadioSourceListenMetadata = RadioSourceListenMetadata
sys.modules["api.schemas.radio_source"] = _m_schema


# Also stub top-level schemas import that some modules may use
_m_schema_top = types.ModuleType("schemas.stream_type")
class StreamTypeOut:
    def __init__(self, id: int, display_name: str = ""):
        self.id = id
        self.display_name = display_name
_m_schema_top.StreamTypeOut = StreamTypeOut
sys.modules["schemas.stream_type"] = _m_schema_top


# Stub the `service` package and the specific submodules the API service imports
# to avoid pulling in Flask and other heavy runtime deps during test collection.
_service_pkg = types.ModuleType("service")
sys.modules["service"] = _service_pkg

_auth_mod = types.ModuleType("service.auth_service")
class AuthService:
    def __init__(self, *args, **kwargs):
        pass
_auth_mod.AuthService = AuthService
sys.modules["service.auth_service"] = _auth_mod

_proposal_mod = types.ModuleType("service.proposal_service")
class ProposalService:
    def __init__(self, *args, **kwargs):
        pass
_proposal_mod.ProposalService = ProposalService
sys.modules["service.proposal_service"] = _proposal_mod

_radio_mod = types.ModuleType("service.radio_source_service")
class RadioSourceService:
    def __init__(self, *args, **kwargs):
        pass
_radio_mod.RadioSourceService = RadioSourceService
sys.modules["service.radio_source_service"] = _radio_mod

_stream_mod = types.ModuleType("service.stream_type_service")
class StreamTypeService:
    def __init__(self, *args, **kwargs):
        pass
_stream_mod.StreamTypeService = StreamTypeService
sys.modules["service.stream_type_service"] = _stream_mod

from api.service.radio_source_api_service import RadioSourceAPIService


class _DTO:
    def __init__(self, id: int, name: str, stream_type_id: int, country: str, stream_url: str):
        self.id = id
        self.name = name
        self.stream_type = types.SimpleNamespace(id=stream_type_id)
        self.country = country
        self.stream_url = stream_url


class _StubService:
    def __init__(self, dtos):
        self._dtos = list(dtos)

    def get_all_radio_sources(self):
        return list(self._dtos)

    def get_radio_source(self, id: int):
        for d in self._dtos:
            if d.id == id:
                return d
        return None


class _StubStreamTypeAPI:
    def __init__(self):
        pass

    def get_stream_type(self, dt):
        # Return a simple object representing stream type
        return types.SimpleNamespace(id=getattr(dt, "id", None), display_name=f"type-{getattr(dt, 'id', None)}")


def _make_service(monkeypatch, dtos):
    stub = _StubService(dtos)
    # avoid touching real DB/repo during construction
    monkeypatch.setattr(RadioSourceAPIService, "get_radio_source_repo", lambda self: None)
    monkeypatch.setattr(RadioSourceAPIService, "get_proposal_repo", lambda self: None)
    monkeypatch.setattr(RadioSourceAPIService, "get_stream_type_repo", lambda self: None)
    monkeypatch.setattr(RadioSourceAPIService, "get_radio_source_service", lambda self: stub)
    monkeypatch.setattr(RadioSourceAPIService, "get_stream_type_api_service", lambda self: _StubStreamTypeAPI())
    return RadioSourceAPIService()


def test_list_sources_empty(monkeypatch):
    svc = _make_service(monkeypatch, [])
    assert svc.list_sources() is None


def test_list_sources_filters_and_pagination(monkeypatch):
    dtos = [
        _DTO(1, "One Radio", 1, "IT", "http://one"),
        _DTO(2, "Two Station", 2, "US", "http://two"),
        _DTO(3, "Another One", 1, "IT", "http://three"),
    ]
    svc = _make_service(monkeypatch, dtos)

    # filter by q
    items, total = svc.list_sources(q="one")
    assert total == 2
    assert len(items) == 2

    # filter by stream_type
    items, total = svc.list_sources(stream_type=2)
    assert total == 1
    assert items[0].id == 2

    # filter by country
    items, total = svc.list_sources(country="IT")
    assert total == 2

    # pagination: page_size 1
    items, total = svc.list_sources(page=2, page_size=1)
    assert total == 3
    assert len(items) == 1
    assert items[0].id == 2


def test_get_source_and_listen_metadata(monkeypatch):
    dtos = [_DTO(5, "ListenMe", 7, "GB", "http://listen")]
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

    # missing source returns None
    assert svc.get_source(999) is None
    assert svc.get_listen_metadata(999) is None
