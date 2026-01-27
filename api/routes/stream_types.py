from fastapi import APIRouter
from api.service.stream_type_api_service import StreamTypeAPIService
from api.schemas.stream_type import StreamTypeList


router = APIRouter(prefix="/api/v1/stream_types", tags=["stream_types"])

@router.get("/")
def get_stream_types() -> StreamTypeList:
    service = StreamTypeAPIService()
    return service.get_all_stream_types()