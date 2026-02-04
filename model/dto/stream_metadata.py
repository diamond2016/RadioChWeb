"""
Stream metadata DTO for on-the-fly listening information.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict


class StreamMetadataDTO(BaseModel):
    available: bool
    bitrate: Optional[int] = None
    genre: Optional[str] = None
    current_track: Optional[str] = None
    error_message: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
