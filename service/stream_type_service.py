"""
StreamTypeService - Service for managing StreamType lookup table.
Provides methods to find and manage the predefined stream types from spec 003.
"""

from typing import Optional, List, Dict
from model.repository.stream_type_repository import StreamTypeRepository
from model.dto.stream_type import StreamTypeDTO


class StreamTypeService:
    """Service for managing StreamType entities and lookup operations."""
    
    def __init__(self, stream_type_repository: StreamTypeRepository):
        self.repository = stream_type_repository
    
    def find_stream_type_id(self, protocol: str, format: str, metadata: str) -> Optional[int]:
        """
        Find StreamType ID for given protocol, format, and metadata combination.
        
        Args:
            protocol: HTTP, HTTPS, or HLS
            format: MP3, AAC, OGG
            metadata: Icecast, Shoutcast, or None
            
        Returns:
            StreamType ID if found, None otherwise
        """
        return self.repository.find_by_combination(protocol, format, metadata)
    
    def get_stream_type(self, stream_type_id: int) -> Optional[StreamTypeDTO]:
        """Get StreamType by ID."""
        stream_type = self.repository.get_by_id(stream_type_id)
        if stream_type:
            # Map from model to DTO, renaming metadata_type to metadata
            return StreamTypeDTO(
                id=stream_type.id,
                protocol=stream_type.protocol,
                format=stream_type.format,
                metadata=stream_type.metadata_type,
                display_name=stream_type.display_name
            )
        return None
    
    def get_all_stream_types(self) -> List[StreamTypeDTO]:
        """Get all available StreamTypes."""
        stream_types = self.repository.get_all()
        return [StreamTypeDTO(
            id=st.id,
            protocol=st.protocol,
            format=st.format,
            metadata=st.metadata_type,
            display_name=st.display_name
        ) for st in stream_types]
    
    def get_predefined_types_map(self) -> Dict[str, int]:
        """
        Get a map of type keys (PROTOCOL-FORMAT-METADATA) to IDs.
        Useful for quick lookups during analysis.
        """
        return self.repository.get_type_key_to_id_map()
    
    def initialize_predefined_types(self) -> None:
        """
        Initialize the database with the 14 predefined StreamTypes from spec 003.
        This should be called during application setup.
        """
        predefined_types = [
            ("HTTP", "MP3", "Icecast", "HTTP MP3 with Icecast metadata"),
            ("HTTP", "MP3", "Shoutcast", "HTTP MP3 with Shoutcast metadata"),
            ("HTTP", "MP3", "None", "HTTP MP3 direct stream"),
            ("HTTP", "AAC", "Icecast", "HTTP AAC with Icecast metadata"),
            ("HTTP", "AAC", "Shoutcast", "HTTP AAC with Shoutcast metadata"),
            ("HTTP", "AAC", "None", "HTTP AAC direct stream"),
            ("HTTPS", "MP3", "Icecast", "HTTPS MP3 with Icecast metadata"),
            ("HTTPS", "MP3", "Shoutcast", "HTTPS MP3 with Shoutcast metadata"),
            ("HTTPS", "MP3", "None", "HTTPS MP3 direct stream"),
            ("HTTPS", "AAC", "Icecast", "HTTPS AAC with Icecast metadata"),
            ("HTTPS", "AAC", "Shoutcast", "HTTPS AAC with Shoutcast metadata"),
            ("HTTPS", "AAC", "None", "HTTPS AAC direct stream"),
            ("HLS", "AAC", "None", "HTTP Live Streaming (HLS) with AAC"),
            ("PLAYLIST", "PLAYLIST", "None", "Playlist file (.m3u, .pls, .m3u8) - parsing not implemented")
        ]
        
        for protocol, format_type, metadata, display_name in predefined_types:
            self.repository.create_if_not_exists(protocol, format_type, metadata, display_name)

    def get_display_name(self, stream_type_id: int) -> Optional[str]:
        """Get the display name of a StreamType by its ID."""
        stream_type = self.repository.find_by_id(stream_type_id)
        if stream_type:
            return stream_type.display_name
        return None