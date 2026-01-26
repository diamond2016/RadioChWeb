from fastapi import APIRouter,
from api.service.stream_type_api_service import StreamTypeAPIService
router = APIRouter()

@router.get("/stream_types")
def get_stream_types():
    service = StreamTypeAPIService()
    return service.get_all_stream_types()