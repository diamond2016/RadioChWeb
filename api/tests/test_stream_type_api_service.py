# python
from types import SimpleNamespace

from api.schemas.stream_type import StreamTypeList, StreamTypeOut
from api.service.stream_type_api_service import StreamTypeAPIService


def test_get_all_stream_types_returns_items_and_counts():
    svc = StreamTypeAPIService()
    dto1 = SimpleNamespace(id=1, display_name="Music")
    dto2 = SimpleNamespace(id=2, display_name="News")
    fake_service = SimpleNamespace(get_all_stream_types=lambda: [dto1, dto2])
    svc._stream_type_service = fake_service

    result: StreamTypeList = svc.get_all_stream_types()

    assert result is not None
    assert hasattr(result, "items")
    assert hasattr(result, "total")
    assert hasattr(result, "page")
    assert hasattr(result, "page_size")

    assert result.total == 2
    assert result.page == 1
    assert result.page_size == 2
    assert len(result.items) == 2
    assert result.items[0].id == 1
    assert result.items[0].display_name == "Music"
    assert result.items[1].id == 2
    assert result.items[1].display_name == "News"


def test_get_all_stream_types_empty_list():
    svc = StreamTypeAPIService()
    fake_service = SimpleNamespace(get_all_stream_types=lambda: [])
    svc._stream_type_service = fake_service

    result = svc.get_all_stream_types()

    assert result is not None
    assert result.total == 0
    assert result.page == 1
    assert result.page_size == 0
    assert result.items == []

def test_get_stream_type():
    svc = StreamTypeAPIService()
    dto = SimpleNamespace(id=1, display_name="Music")
    fake_service = SimpleNamespace(get_stream_type=lambda id: dto if id == 1 else None)
    svc._stream_type_service = fake_service

    result: StreamTypeOut | None = svc.get_stream_type(1)

    assert result is not None
    assert result.id == 1
    assert result.display_name == "Music"

    result_none: StreamTypeOut | None = svc.get_stream_type(999)
    assert result_none is None