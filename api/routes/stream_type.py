from fastapi import APIRouter,

router = APIRouter()

@router.get("/stream_types")
def get_stream_types():
    return {"stream_types": []} HTTPException, Query
from typing import Optional