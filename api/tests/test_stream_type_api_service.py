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

# Inject lightweight stubs for model and service modules to avoid importing SQLAlchemy
_m_repo = types.ModuleType("model.repository.stream_type_repository")
class _StubRepo:
    pass
_m_repo.StreamTypeRepository = _StubRepo
sys.modules["model.repository.stream_type_repository"] = _m_repo

_m_dto = types.ModuleType("model.dto.stream_type")
class StreamTypeDTO:
    def __init__(self, id: int, display_name: str):
        self.id = id
        self.display_name = display_name
_m_dto.StreamTypeDTO = StreamTypeDTO
sys.modules["model.dto.stream_type"] = _m_dto

_m_schema = types.ModuleType("api.schemas.stream_type")
class StreamTypeOut:
    def __init__(self, id: int, display_name: str):
        self.id = id
        self.display_name = display_name

class StreamTypeList:
    def __init__(self, items, total, page, page_size):
        self.items = items
        self.total = total
        self.page = page
        self.page_size = page_size

_m_schema.StreamTypeOut = StreamTypeOut
_m_schema.StreamTypeList = StreamTypeList
sys.modules["api.schemas.stream_type"] = _m_schema

_m_service = types.ModuleType("service.stream_type_service")
class StreamTypeService:
    def __init__(self, repo):
        self.repo = repo
    def get_predefined_types_map(self):
        return {}
    def get_stream_type(self, id: int):
        return None
    def get_all_stream_types(self):
        return []
_m_service.StreamTypeService = StreamTypeService
sys.modules["service.stream_type_service"] = _m_service

from api.service.stream_type_api_service import StreamTypeAPIService

class _DTO:
    def __init__(self, id: int, display_name: str):
        self.id = id
        self.display_name = display_name


class _StubService:
    def __init__(self, dtos):
        self._dtos = dtos

    def get_predefined_types_map(self):
        return {dto.display_name: dto.id for dto in self._dtos}

    def get_stream_type(self, id: int):
        for d in self._dtos:
            if d.id == id:
                return d
        return None

    def get_all_stream_types(self):
        return list(self._dtos)


def _make_service(monkeypatch, dtos):
    stub = _StubService(dtos)
    # avoid touching real DB/repo during construction
    monkeypatch.setattr(StreamTypeAPIService, "get_stream_type_repo", lambda self: None)
    monkeypatch.setattr(StreamTypeAPIService, "get_stream_type_service", lambda self: stub)
    return StreamTypeAPIService()


def test_get_stream_type_valid(monkeypatch):
    dtos = [_DTO(0, "audio"), _DTO(1, "video")]
    svc = _make_service(monkeypatch, dtos)

    res = svc.get_stream_type(1)
    assert res is not None
    assert res.id == 1
    assert res.display_name == "video"


def test_get_stream_type_out_of_range(monkeypatch):
    dtos = [_DTO(0, "audio")]
    svc = _make_service(monkeypatch, dtos)

    assert svc.get_stream_type(-1) is None
    assert svc.get_stream_type(5) is None


def test_get_all_stream_types(monkeypatch):
    dtos = [_DTO(0, "audio"), _DTO(1, "video")]
    svc = _make_service(monkeypatch, dtos)

    res = svc.get_all_stream_types()
    assert res.total == 2
    assert len(res.items) == 2
    assert res.items[0].id == 0
    assert res.items[0].display_name == "audio"
