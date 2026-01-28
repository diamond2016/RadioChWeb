from fastapi import APIRouter, HTTPException
from api.services.stream_type_api_service import StreamTypeAPIService
from api.schemas.stream_type import StreamTypeList, StreamTypeOut


# Router has no prefix here; `main.py` includes this router with
# the desired prefix (`/api/v1/stream_types`). Avoid duplicating
# the prefix to prevent double-routing and 404s.
router = APIRouter(tags=["stream_types"])
service = StreamTypeAPIService()

@router.get("")
@router.get("/")
def get_stream_types() -> StreamTypeList:
    return service.get_all_stream_types()

@router.get("/{stream_type_id}", response_model=StreamTypeOut)
def get_stream_type(stream_type_id: int) -> StreamTypeOut:
    stream_type: StreamTypeOut | None = service.get_stream_type(stream_type_id)
    if not stream_type:
        raise HTTPException(status_code=404, detail="Stream type not found")
    return stream_type