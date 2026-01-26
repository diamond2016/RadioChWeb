from typing import Dict, List, Optional
from api.deps import get_db

from model.repository.stream_type_repository import StreamTypeRepository
from model.dto.stream_type import StreamTypeDTO
from api.schemas.stream_type import StreamTypeList, StreamTypeOut
from service.stream_type_service import StreamTypeService


class StreamTypeAPIService:
    # Repository and service initialization functions
    def get_stream_type_repo(self) -> StreamTypeRepository:
        return StreamTypeRepository(get_db())
    
    def get_stream_type_service(self) -> StreamTypeService:
        stream_type_repo: StreamTypeRepository = self.get_stream_type_repo()
        return StreamTypeService(stream_type_repo)  
    
    def __init__(self):
        self.stream_type_repository: StreamTypeRepository = self.get_stream_type_repo()
        self.stream_type_service: StreamTypeService = self.get_stream_type_service()
        self.stream_types: Dict[str, int] = self.stream_type_service.get_predefined_types_map()

    def get_stream_type(self, id: int) -> Optional[StreamTypeOut]:
        if id < 0 or id >= len(self.stream_types):
            return None
        stream_type_dto: Optional[StreamTypeDTO] = self.stream_type_service.get_stream_type(id)
        if stream_type_dto:
            return StreamTypeOut(
                id=stream_type_dto.id,
                display_name=stream_type_dto.display_name
            )
        return None    
    
    def get_all_stream_types(self) -> StreamTypeList:
        items_types: List[StreamTypeOut] = []
        items_types = [
            StreamTypeOut(
                id=stream_type_dto.id,
                display_name=stream_type_dto.display_name
            )
            for stream_type_dto in self.stream_type_service.get_all_stream_types()
        ]
        return StreamTypeList(items=items_types, total=len(items_types), page=1, page_size=len(items_types))