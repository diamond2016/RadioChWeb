"""
StreamTypeRepository - Data access layer for StreamType entities.
"""

from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from model.dto.stream_type import StreamTypeDTO
from model.entity.stream_type import StreamType


class StreamTypeRepository:
    """Repository for StreamType data access operations."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def find_by_id(self, stream_type_id: int) -> Optional[StreamType]:
        """Get StreamType by ID."""
        return self.db.query(StreamType).filter(StreamType.id == stream_type_id).first()
    
    def find_all(self) -> List[StreamType]:
        """Get all StreamTypes."""
        return self.db.query(StreamType).all()
    
    def count(self) -> int:
        """Count total StreamTypes."""
        return self.db.query(StreamType).count()
    
    def find_by_combination(self, protocol: str, format_type: str, metadata: str) -> Optional[int]:
        """
        Find StreamType ID by protocol, format, and metadata combination.
        
        Returns:
            StreamType ID if found, None otherwise
        """
        stream_type = self.db.query(StreamType).filter(
            StreamType.protocol == protocol,
            StreamType.format == format_type,
            StreamType.metadata_type == metadata
        ).first()
        
        return stream_type.id if stream_type else None
    
    def create_if_not_exists(self, protocol: str, format_type: str, metadata: str, display_name: str) -> StreamType:
        """
        Create a StreamType if it doesn't already exist.
        Used for initializing predefined types.
        """
        existing = self.db.query(StreamType).filter(
            StreamType.protocol == protocol,
            StreamType.format == format_type,
            StreamType.metadata_type == metadata
        ).first()
        
        if existing:
            return existing
        
        new_type = StreamType(
            protocol=protocol,
            format=format_type,
            metadata_type=metadata,
            display_name=display_name
        )
        
        self.db.add(new_type)
        self.db.commit()
        self.db.refresh(new_type)
        
        return new_type
    
    def get_type_key_to_id_map(self) -> Dict[str, int]:
        """
        Get a dictionary mapping type keys (PROTOCOL-FORMAT-METADATA) to IDs.
        Useful for quick lookups during stream analysis.
        """
        stream_types: List[StreamType] = self.find_all()
        return {st.type_key: st.id for st in stream_types}
    

    def to_dto(self, stream_type_id: int) -> Optional[StreamTypeDTO]:
        """Convert StreamType entity to StreamTypeDTO."""
        stream_type: StreamType | None = self.find_by_id(stream_type_id)
        if stream_type is None:
            return None
        return StreamTypeDTO(
            id=stream_type.id,
            protocol=stream_type.protocol,
            format=stream_type.format,
            metadata_type=stream_type.metadata_type,
            display_name=stream_type.display_name
        )