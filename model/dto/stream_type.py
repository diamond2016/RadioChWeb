"""
StreamType DTO for API responses and data transfer.
"""

from pydantic import BaseModel, ConfigDict


class StreamTypeDTO(BaseModel):
    """DTO for StreamType entity."""

    id: int
    protocol: str  # HTTP, HTTPS, HLS
    format: str  # MP3, AAC, OGG
    metadata: str  # Icecast, Shoutcast, None (mapped from metadata_type)
    display_name: str

    @property
    def type_key(self) -> str:
        """Returns the type key in format: PROTOCOL-FORMAT-METADATA"""
        return f"{self.protocol}-{self.format}-{self.metadata}"

    model_config = ConfigDict(from_attributes=True)
