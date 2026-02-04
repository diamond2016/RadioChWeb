from typing import Optional
from pydantic import BaseModel, ConfigDict


class StreamMetadataOut(BaseModel):
    available: bool
    bitrate: Optional[int] = None
    genre: Optional[str] = None
    current_track: Optional[str] = None
    error_message: Optional[str] = None
    model_config = ConfigDict(from_attributes=True) 
