"""
StreamAnalysysRepository - Data access layer for StreamAnalysys entity.
"""

from typing import Optional, List, Dict
from sqlalchemy.orm import Session, selectinload
from model.entity.stream_analysis import StreamAnalysis


class StreamAnalysisRepository:
    """Repository for StreamAnalysis data access operations."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def find_by_id(self, id: int) -> Optional[StreamAnalysis]:
        """Get StreamAnalysis by ID."""
        return self.db.query(StreamAnalysis).options(selectinload(StreamAnalysis.stream_type), selectinload(StreamAnalysis.user)).filter(StreamAnalysis.id == id).first()
    
    def find_all(self) -> List[StreamAnalysis]:
        """Get all StreamAnalysises."""
        return self.db.query(StreamAnalysis).options(selectinload(StreamAnalysis.stream_type), selectinload(StreamAnalysis.user)).all()
    
    def count(self) -> int:
        """Count total StreamAnalysises."""
        return self.db.query(StreamAnalysis).count()
    
    def find_by_url(self, stream_url: str) -> Optional[StreamAnalysis]:
        """
        Find StreamAnalysis ID by stream url
        
        Returns:
            StreamAnalysis if found, None otherwise
        """
        stream_analysis = self.db.query(StreamAnalysis).options(selectinload(StreamAnalysis.stream_type), selectinload(StreamAnalysis.user)).filter(
            StreamAnalysis.stream_url == stream_url
        ).first()
        
        return stream_analysis if stream_analysis else None
    

    def save(self, new_analysis: StreamAnalysis) -> StreamAnalysis:
        """
        Create a StreamAnalysis if it doesn't already exist.
        Used for initializing predefined types.
        """
        existing = self.db.query(StreamAnalysis).filter(
            StreamAnalysis.stream_url == new_analysis.stream_url
        ).first()
        
        if existing:
            return existing
        
        self.db.add(new_analysis)
        self.db.commit()
        self.db.refresh(new_analysis)
        
        return new_analysis
    
    def delete(self, id: int) -> bool:
        """Delete a StreamAnalysis by ID."""
        existing = self.find_by_id(id)
        if existing:
            self.db.delete(existing)
            self.db.commit()
            return True
        return False
    
    def get_analyses_by_user(self, user_id: int) -> List[StreamAnalysis]:
        """Retrieve all stream analyses submitted by a specific user."""
        return self.db.query(StreamAnalysis).options(selectinload(StreamAnalysis.stream_type), selectinload(StreamAnalysis.user)).filter(StreamAnalysis.created_by == user_id).all()