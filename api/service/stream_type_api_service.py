from typing import Dict, Optional
from model.dto.stream_type import StreamTypeDTO
from service.stream_type_service import StreamTypeService
from model.repository.stream_type_repository import StreamTypeRepository
from schemas.stream_type import StreamTypeList, StreamTypeOut
from deps import get_db_session


class StreamTypeAPIService:
    """API-facing service for stream types.

    Supports dependency injection and lazy imports to avoid importing
    application internals at module import time.
    """

    def __init__(self):
        self._stream_type_service = None
        self._stream_type_repo = None
        self._predefined_types: Optional[Dict[str, int]] = None

    def get_stream_type_repo(self) -> StreamTypeRepository:
        from model.repository.stream_type_repository import StreamTypeRepository

        if self._stream_type_repo is None:
            self._stream_type_repo = StreamTypeRepository(get_db_session())
        return self._stream_type_repo

    def get_stream_type_service(self) -> StreamTypeService:
        from service.stream_type_service import StreamTypeService
        if self._stream_type_service is None:
            self._stream_type_service: StreamTypeService = StreamTypeService(stream_type_repository=self.get_stream_type_repo())
        return self._stream_type_service

    def _get_predefined_types_map(self) -> Dict[str, int]:
        if self._predefined_types is None:
            self._predefined_types = self.get_stream_type_service().get_predefined_types_map()
        return self._predefined_types

    def get_stream_type(self, id: int) -> Optional[StreamTypeOut]:
        stream_type_dto: StreamTypeDTO | None = self.get_stream_type_service().get_stream_type(id)
        if stream_type_dto:
            # Accept DTOs that may be simple namespaces or objects by
            # converting to a mapping first (tests provide SimpleNamespace).
            data = vars(stream_type_dto) if hasattr(stream_type_dto, "__dict__") else stream_type_dto
            return StreamTypeOut.model_validate(data)
        return None

    def get_all_stream_types(self) -> StreamTypeList:
        raw_items = self.get_stream_type_service().get_all_stream_types()
        items: list[StreamTypeOut] = []
        for item in raw_items:
            data = vars(item) if hasattr(item, "__dict__") else item
            items.append(StreamTypeOut.model_validate(data))
        return StreamTypeList(items=items, total=len(items), page=1, page_size=len(items))