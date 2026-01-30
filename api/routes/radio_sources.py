from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from api.schemas.radio_source import RadioSourceListenMetadata, RadioSourceOut, RadioSourceList
from api.services.radio_source_api_service import RadioSourceAPIService

service = RadioSourceAPIService()
# Router has no prefix here; `main.py` includes this router with prefix (`/api/v1/sources`).
router = APIRouter(tags=["sources"])

@router.get("/", response_model=RadioSourceList)
def list_sources(q: Optional[str] = Query(None), stream_type: Optional[int] = Query(None), 
                 country: Optional[str] = Query(None), page: int = 1, page_size: int = 20) -> RadioSourceList:
    """List radio sources with optional filters"""

    # Phase 1: read all sources wihothout filtering/pagination
    all_sources: RadioSourceList = service.get_all_radio_sources()
    print(f"Total sources before filtering: {len(all_sources.items)}")
    return all_sources

@router.get("/{source_id}", response_model=RadioSourceOut)
def get_radio_source(source_id: int):
    """List single radio source"""
    # raise 404 if not found
    radio_source: RadioSourceOut = service.get_radio_source(source_id)
    if not radio_source:
        raise HTTPException(status_code=404, detail="radio source not found")
    return radio_source


@router.get("/{source_id}/listen")
def listen_source(source_id: int):
    """Return minimal metadata for the client to open stream"""
    listen_metadata: RadioSourceListenMetadata | None = service.get_listen_metadata(source_id)
    if not listen_metadata:
        raise HTTPException(status_code=404, detail="radio source not found")
    return listen_metadata  
