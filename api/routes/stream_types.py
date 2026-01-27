from fastapi import APIRouter
from api.service.stream_type_api_service import StreamTypeAPIService
from api.schemas.stream_type import StreamTypeList


# Router has no prefix here; `main.py` includes this router with
# the desired prefix (`/api/v1/stream_types`). Avoid duplicating
# the prefix to prevent double-routing and 404s.
router = APIRouter(tags=["stream_types"])


@router.get("")
@router.get("/")
def get_stream_types() -> StreamTypeList:
    service = StreamTypeAPIService()
    return service.get_all_stream_types()