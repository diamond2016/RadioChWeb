from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from ..schemas.radio_source import RadioSourceOut, RadioSourceList

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/", response_model=RadioSourceList)
def list_sources(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    # Placeholder: return empty page
    return {"items": [], "total": 0, "page": page, "page_size": page_size}


@router.get("/{source_id}", response_model=RadioSourceOut)
def get_source(source_id: int):
    # Placeholder: not found
    raise HTTPException(status_code=404, detail="Source not found")
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from schemas.radio_source import RadioSourceOut, RadioSourceList

router = APIRouter()


@router.get("/", response_model=RadioSourceList)
def list_sources(q: Optional[str] = Query(None), stream_type: Optional[int] = Query(None), country: Optional[str] = Query(None), page: int = 1, page_size: int = 20):
    """List radio sources (placeholder implementation)."""
    # Phase 1: implement service layer to read from DB
    return {"items": [], "total": 0, "page": page, "page_size": page_size}


@router.get("/{source_id}", response_model=RadioSourceOut)
def get_source(source_id: int):
    # Placeholder: raise 404 if not found
    raise HTTPException(status_code=404, detail="Not implemented")


@router.get("/{source_id}/listen")
def listen_source(source_id: int):
    # Return minimal metadata for the client to open stream
    return {"stream_url": "", "stream_type": None, "name": None}
