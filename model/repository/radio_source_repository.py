"""
RadioSourceRepository - Data access layer for RadioSource entities.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from model.entity.radio_source import RadioSource


class RadioSourceRepository:
    """Repository for RadioSource data access operations."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def find_by_id(self, source_id: int) -> Optional[RadioSource]:
        """Get RadioSource by ID."""
        return self.db.query(RadioSource).filter(RadioSource.id == source_id).first()

    def find_by_url(self, url: str) -> Optional[RadioSource]:
        """Get RadioSource by URL (for duplicate checking)."""
        return self.db.query(RadioSource).filter(RadioSource.stream_url == url).first()

    def find_all(self) -> List[RadioSource]:
        """Get all RadioSources."""
        return self.db.query(RadioSource).all()

    def find_by_stream_type(self, stream_type_id: int) -> List[RadioSource]:
        """Get RadioSources by stream type."""
        return (
            self.db.query(RadioSource)
            .filter(RadioSource.stream_type_id == stream_type_id)
            .all()
        )

    def search_by_name(self, name_query: str) -> List[RadioSource]:
        """Search RadioSources by name."""
        return (
            self.db.query(RadioSource)
            .filter(RadioSource.name.ilike(f"%{name_query}%"))
            .all()
        )

    def save(self, radio_source: RadioSource) -> RadioSource:
        """Save (create or update) a RadioSource."""
        if radio_source.id is None:
            self.db.add(radio_source)
        self.db.commit()
        self.db.refresh(radio_source)
        return radio_source

    def delete(self, source_id: int) -> bool:
        """Delete a RadioSource by ID."""
        radio_source = self.find_by_id(source_id)
        if radio_source:
            self.db.delete(radio_source)
            self.db.commit()
            return True
        return False

    def count(self) -> int:
        """Count total RadioSources."""
        return self.db.query(RadioSource).count()
