"""
Stream metadata DTO for on-the-fly listening information.
"""

from typing import Optional
from pydantic import BaseModel


class StreamMetadataDTO(BaseModel):
    available: bool
    bitrate: Optional[int] = None
    genre: Optional[str] = None
    current_track: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        validate_assignment = True
        orm_mode = True
