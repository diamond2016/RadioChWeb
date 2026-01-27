from typing import Dict, Optional
from database import get_db_session

from model.repository.stream_type_repository import StreamTypeRepository
from service.stream_type_service import StreamTypeService


class StreamTypeAPIService:
    """API-facing service for stream types.

    Supports dependency injection and lazy imports to avoid importing
    application internals at module import time.
    """

    def __init__(self, stream_type_service: Optional[StreamTypeService] = None):
        self._stream_type_service = stream_type_service
        self._stream_type_repo = None
        self._predefined_types: Optional[Dict[str, int]] = None

    def get_stream_type_repo(self) -> StreamTypeRepository:
        from model.repository.stream_type_repository import StreamTypeRepository

        if self._stream_type_repo is None:
            self._stream_type_repo = StreamTypeRepository(get_db_session())
        return self._stream_type_repo

    def get_stream_type_service(self) -> StreamTypeService:
        if self._stream_type_service is not None:
            return self._stream_type_service
        from service.stream_type_service import StreamTypeService

        svc = StreamTypeService(stream_type_repo=self.get_stream_type_repo())
        self._stream_type_service: StreamTypeService = svc
        return svc

    def _get_predefined_types_map(self) -> Dict[str, int]:
        if self._predefined_types is None:
            self._predefined_types = self.get_stream_type_service().get_predefined_types_map()
        return self._predefined_types

    def get_stream_type(self, id: int) -> Optional[StreamTypeOut]:
        stream_type_dto = self.get_stream_type_service().get_stream_type(id)
        if stream_type_dto:
            return StreamTypeOut(id=stream_type_dto.id, display_name=stream_type_dto.display_name)
        return None

    def get_all_stream_types(self) -> StreamTypeList:
        items: List[StreamTypeOut] = [
            StreamTypeOut(id=dto.id, display_name=dto.display_name)
            for dto in self.get_stream_type_service().get_all_stream_types()
        ]
        return StreamTypeList(items=items, total=len(items), page=1, page_size=len(items))