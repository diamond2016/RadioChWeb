import sys
import types
from types import SimpleNamespace
import importlib

from api.schemas.stream_type import StreamTypeOut, StreamTypeList

# Minimal database stub so importing service modules doesn't pull in SQLAlchemy
_db_mod = types.ModuleType("database")
_db_mod.get_db_session = lambda: None
sys.modules.setdefault("database", _db_mod)

# Provide a module that exposes `StreamTypeService` so `from service.stream_type_service
# import StreamTypeService` succeeds during import. Tests will inject the actual
# runtime instance via monkeypatch on the API service class.
_svc_mod = types.ModuleType("service.stream_type_service")
class _FakeStreamTypeService:
    pass
_svc_mod.StreamTypeService = _FakeStreamTypeService
sys.modules.setdefault("service.stream_type_service", _svc_mod)

# Ensure repository module name exists so imports don't attempt to load real repository
_repo_mod = types.ModuleType("model.repository.stream_type_repository")
_repo_mod.StreamTypeRepository = type("StreamTypeRepository", (), {})
sys.modules.setdefault("model.repository.stream_type_repository", _repo_mod)

# Ensure the top-level `schemas.stream_type` name resolves to the real module so
# pydantic model generation inside `api.schemas.radio_source` works correctly.
schemas_mod = importlib.import_module("api.schemas.stream_type")
sys.modules.setdefault("schemas.stream_type", schemas_mod)

from api.service.stream_type_api_service import StreamTypeAPIService


def _make_service(monkeypatch, dtos: list[SimpleNamespace]):
    svc_stub = SimpleNamespace(
        get_predefined_types_map=lambda: {d.display_name: d.id for d in dtos},
        get_stream_type=lambda id: next((d for d in dtos if d.id == id), None),
        get_all_stream_types=lambda: list(dtos),
    )

    monkeypatch.setattr(StreamTypeAPIService, "get_stream_type_repo", lambda self: None)
    monkeypatch.setattr(StreamTypeAPIService, "get_stream_type_service", lambda self: svc_stub)
    return StreamTypeAPIService()


def test_get_stream_type_valid(monkeypatch):
    dtos = [SimpleNamespace(id=0, display_name="audio"), SimpleNamespace(id=1, display_name="video")]
    svc = _make_service(monkeypatch, dtos)

    res = svc.get_stream_type(1)
    assert isinstance(res, StreamTypeOut)
    assert res.id == 1
    assert res.display_name == "video"


def test_get_stream_type_out_of_range(monkeypatch):
    dtos = [SimpleNamespace(id=0, display_name="audio")]
    svc = _make_service(monkeypatch, dtos)

    assert svc.get_stream_type(-1) is None
    assert svc.get_stream_type(5) is None


def test_get_all_stream_types(monkeypatch):
    dtos = [SimpleNamespace(id=0, display_name="audio"), SimpleNamespace(id=1, display_name="video")]
    svc = _make_service(monkeypatch, dtos)

    res = svc.get_all_stream_types()
    assert isinstance(res, StreamTypeList)
    assert res.total == 2
    assert len(res.items) == 2
    assert res.items[0].id == 0
    assert res.items[0].display_name == "audio"
import sys
import types
from types import SimpleNamespace
import importlib

from api.schemas.stream_type import StreamTypeOut, StreamTypeList

# Minimal database stub so importing service modules doesn't pull in SQLAlchemy
_db_mod = types.ModuleType("database")
_db_mod.get_db_session = lambda: None
sys.modules.setdefault("database", _db_mod)

# Provide a module that exposes `StreamTypeService` so `from service.stream_type_service
# import StreamTypeService` succeeds during import. Tests will inject the actual
# runtime instance via monkeypatch on the API service class.
_svc_mod = types.ModuleType("service.stream_type_service")
class _FakeStreamTypeService:
    pass
_svc_mod.StreamTypeService = _FakeStreamTypeService
sys.modules.setdefault("service.stream_type_service", _svc_mod)

# Ensure repository module name exists so imports don't attempt to load real repository
_repo_mod = types.ModuleType("model.repository.stream_type_repository")
_repo_mod.StreamTypeRepository = type("StreamTypeRepository", (), {})
sys.modules.setdefault("model.repository.stream_type_repository", _repo_mod)

# Ensure the top-level `schemas.stream_type` name resolves to the real module so
# pydantic model generation inside `api.schemas.radio_source` works correctly.
schemas_mod = importlib.import_module("api.schemas.stream_type")
sys.modules.setdefault("schemas.stream_type", schemas_mod)

from api.service.stream_type_api_service import StreamTypeAPIService


def _make_service(monkeypatch, dtos: list[SimpleNamespace]):
    svc_stub = SimpleNamespace(
        get_predefined_types_map=lambda: {d.display_name: d.id for d in dtos},
        get_stream_type=lambda id: next((d for d in dtos if d.id == id), None),
        get_all_stream_types=lambda: list(dtos),
    )

    monkeypatch.setattr(StreamTypeAPIService, "get_stream_type_repo", lambda self: None)
    monkeypatch.setattr(StreamTypeAPIService, "get_stream_type_service", lambda self: svc_stub)
    return StreamTypeAPIService()


def test_get_stream_type_valid(monkeypatch):
    dtos = [SimpleNamespace(id=0, display_name="audio"), SimpleNamespace(id=1, display_name="video")]
    svc = _make_service(monkeypatch, dtos)

    res = svc.get_stream_type(1)
    assert isinstance(res, StreamTypeOut)
    assert res.id == 1
    assert res.display_name == "video"


def test_get_stream_type_out_of_range(monkeypatch):
    dtos = [SimpleNamespace(id=0, display_name="audio")]
    svc = _make_service(monkeypatch, dtos)

    assert svc.get_stream_type(-1) is None
    assert svc.get_stream_type(5) is None


def test_get_all_stream_types(monkeypatch):
    dtos = [SimpleNamespace(id=0, display_name="audio"), SimpleNamespace(id=1, display_name="video")]
    svc = _make_service(monkeypatch, dtos)

    res = svc.get_all_stream_types()
    assert isinstance(res, StreamTypeList)
    assert res.total == 2
    assert len(res.items) == 2
    assert res.items[0].id == 0
    assert res.items[0].display_name == "audio"
import sys
import types
from types import SimpleNamespace

from api.schemas.stream_type import StreamTypeOut, StreamTypeList
from types import SimpleNamespace

# Minimal database stub so importing service modules doesn't pull in SQLAlchemy
_db_mod = types.ModuleType("database")
_db_mod.get_db_session = lambda: None
sys.modules.setdefault("database", _db_mod)

# Provide a module that exposes `StreamTypeService` so `from service.stream_type_service
# import StreamTypeService` succeeds during import. Tests will inject the actual
# runtime instance via monkeypatch on the API service class.
_svc_mod = types.ModuleType("service.stream_type_service")
class _FakeStreamTypeService:
    pass
_svc_mod.StreamTypeService = _FakeStreamTypeService
sys.modules.setdefault("service.stream_type_service", _svc_mod)

# Ensure repository module name exists so imports don't attempt to load real repository
sys.modules.setdefault("model.repository.stream_type_repository", types.ModuleType("model.repository.stream_type_repository"))
_m = sys.modules["model.repository.stream_type_repository"]
if not hasattr(_m, "StreamTypeRepository"):
    _m.StreamTypeRepository = type("StreamTypeRepository", (), {})
import importlib
# Ensure the top-level `schemas.stream_type` name resolves to the real module
# so pydantic model generation inside `api.schemas.radio_source` works correctly
schemas_mod = importlib.import_module("api.schemas.stream_type")
sys.modules.setdefault("schemas.stream_type", schemas_mod)
# Ensure the actual DTO module is used (avoid any leftover test-defined module)
dto_mod = importlib.import_module("model.dto.stream_type")
sys.modules["model.dto.stream_type"] = dto_mod

from api.service.stream_type_api_service import StreamTypeAPIService


def _make_service(monkeypatch, dtos: list[StreamTypeDTO]):
    svc_stub = SimpleNamespace(
        get_predefined_types_map=lambda: {d.display_name: d.id for d in dtos},
        get_stream_type=lambda id: next((d for d in dtos if d.id == id), None),
        get_all_stream_types=lambda: list(dtos),
    )

    monkeypatch.setattr(StreamTypeAPIService, "get_stream_type_repo", lambda self: None)
    monkeypatch.setattr(StreamTypeAPIService, "get_stream_type_service", lambda self: svc_stub)
    return StreamTypeAPIService()


def test_get_stream_type_valid(monkeypatch):
    dtos = [
        SimpleNamespace(id=0, display_name="audio"),
        SimpleNamespace(id=1, display_name="video"),
    ]
    svc = _make_service(monkeypatch, dtos)

    res = svc.get_stream_type(1)
    assert isinstance(res, StreamTypeOut)
    assert res.id == 1
    assert res.display_name == "video"


def test_get_stream_type_out_of_range(monkeypatch):
    dtos = [SimpleNamespace(id=0, display_name="audio")]
    svc = _make_service(monkeypatch, dtos)

    assert svc.get_stream_type(-1) is None
    assert svc.get_stream_type(5) is None


def test_get_all_stream_types(monkeypatch):
    dtos = [
        SimpleNamespace(id=0, display_name="audio"),
        SimpleNamespace(id=1, display_name="video"),
    ]
    svc = _make_service(monkeypatch, dtos)

    res = svc.get_all_stream_types()
    assert isinstance(res, StreamTypeList)
    assert res.total == 2
    assert len(res.items) == 2
    assert res.items[0].id == 0
    assert res.items[0].display_name == "audio"
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
import sys
import types
from types import SimpleNamespace

from model.dto.stream_type import StreamTypeDTO
from api.schemas.stream_type import StreamTypeOut, StreamTypeList

# Prevent import-time heavy modules from failing when importing the API service.
# We only need to provide a minimal module object for the repository and the
# service package name so the import in the API module succeeds; tests will
# inject the runtime service instance via monkeypatch.
sys.modules.setdefault("model.repository.stream_type_repository", types.ModuleType("model.repository.stream_type_repository"))
sys.modules.setdefault("service.stream_type_service", types.ModuleType("service.stream_type_service"))
# Provide a minimal `database` module so `from database import get_db_session`
# in the service modules does not attempt to import SQLAlchemy during tests.
_db_mod = types.ModuleType("database")
_db_mod.get_db_session = lambda: None
sys.modules.setdefault("database", _db_mod)

from api.service.stream_type_api_service import StreamTypeAPIService


def _make_service(monkeypatch, dtos: list[StreamTypeDTO]):
    # stub service instance with the expected interface
    svc_stub = SimpleNamespace(
        get_predefined_types_map=lambda: {d.display_name: d.id for d in dtos},
        get_stream_type=lambda id: next((d for d in dtos if d.id == id), None),
        get_all_stream_types=lambda: list(dtos),
    )

    monkeypatch.setattr(StreamTypeAPIService, "get_stream_type_repo", lambda self: None)
    monkeypatch.setattr(StreamTypeAPIService, "get_stream_type_service", lambda self: svc_stub)
    return StreamTypeAPIService()


def test_get_stream_type_valid(monkeypatch):
    dtos = [
        StreamTypeDTO.model_validate({"id": 0, "protocol": "HTTP", "format": "MP3", "metadata_type": "None", "display_name": "audio"}),
        StreamTypeDTO.model_validate({"id": 1, "protocol": "HTTP", "format": "AAC", "metadata_type": "None", "display_name": "video"}),
    ]
    svc = _make_service(monkeypatch, dtos)

    res = svc.get_stream_type(1)
    assert isinstance(res, StreamTypeOut)
    assert res.id == 1
    assert res.display_name == "video"


def test_get_stream_type_out_of_range(monkeypatch):
    dtos = [StreamTypeDTO.model_validate({"id": 0, "protocol": "HTTP", "format": "MP3", "metadata_type": "None", "display_name": "audio"})]
    svc = _make_service(monkeypatch, dtos)

    assert svc.get_stream_type(-1) is None
    assert svc.get_stream_type(5) is None


def test_get_all_stream_types(monkeypatch):
    dtos = [
        StreamTypeDTO.model_validate({"id": 0, "protocol": "HTTP", "format": "MP3", "metadata_type": "None", "display_name": "audio"}),
        StreamTypeDTO.model_validate({"id": 1, "protocol": "HTTP", "format": "AAC", "metadata_type": "None", "display_name": "video"}),
    ]
    svc = _make_service(monkeypatch, dtos)

    res = svc.get_all_stream_types()
    assert isinstance(res, StreamTypeList)
    assert res.total == 2
    assert len(res.items) == 2
    assert res.items[0].id == 0
    assert res.items[0].display_name == "audio"
    dtos = [_DTO(0, "audio"), _DTO(1, "video")]
    svc = _make_service(monkeypatch, dtos)

    res = svc.get_all_stream_types()
    assert res.total == 2
    assert len(res.items) == 2
    assert res.items[0].id == 0
    assert res.items[0].display_name == "audio"
