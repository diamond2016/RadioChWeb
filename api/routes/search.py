from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db
from api.services.radio_source_service import list_sources
from schemas.radio_source import RadioSourceList

router = APIRouter()


@router.get("/search", response_model=RadioSourceList)
def search(q: str, db: Session = Depends(get_db)):
    items, total = list_sources(db, q=q, page=1, page_size=20)
    return {
        "items": items,
        "total": total,
        "page": 1,
        "page_size": 20,
    }
@router.get("/latest", response_model=RadioSourceList)
def latest(db: Session = Depends(get_db)):
    items = list_sources(db, page=1, page_size=10)[0]
    total = len(items)
    return {
        "items": items,
        "total": total,
        "page": 1,
        "page_size": 10,
    }   