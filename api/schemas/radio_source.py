from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

from schemas.stream_type import StreamTypeOut

class RadioSourceOut(BaseModel):
    """Schema for Radiosource detail entity."""
    id: int
    stream_url: str
    name: str
    is_secure: bool = False
    stream_type: StreamTypeOut

    website_url: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True) 

class RadioSourceList(BaseModel):
    """Schema for Radiosource list entity."""
    items: List[RadioSourceOut]
    total: int
    page: int
    page_size: int
    model_config = ConfigDict(from_attributes=True) 

class RadioSourceListenMetadata(BaseModel):
    """Schema for Radiosource listen metadata entity."""
    id: int
    stream_url: str
    stream_type: StreamTypeOut
    website_url: Optional[str] = None
    name: str
    model_config = ConfigDict(from_attributes=True)
