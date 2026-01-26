from sqlalchemy.orm import Session
from models.radio_source import RadioSource


def list_sources(
    db: Session,
    q: str | None = None,
    stream_type: int | None = None,
    country: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    query = db.query(RadioSource)

    if q:
        query = query.filter(RadioSource.name.ilike(f"%{q}%"))

    if stream_type:
        query = query.filter(RadioSource.stream_type == stream_type)

    if country:
        query = query.filter(RadioSource.country == country)

    total = query.count()

    items = (
        query.order_by(RadioSource.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return items, total


def get_source(db: Session, source_id: int):
    return db.query(RadioSource).get(source_id)


def get_listen_metadata(db: Session, source_id: int):
    source = db.query(RadioSource).get(source_id)
    if not source:
        return None

    return {
        "stream_url": source.stream_url,
        "stream_type": source.stream_type,
        "name": source.name,
    }


def latest_sources(db: Session, limit: int = 10):
    return (
        db.query(RadioSource)
        .order_by(RadioSource.created_at.desc())
        .limit(limit)
        .all()
    )

