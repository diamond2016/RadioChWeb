from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class StreamType(BaseModel):
    id: int
    display_name: str


class RadioSourceOut(BaseModel):
    id: int
    name: str
    stream_url: str
    website_url: Optional[str] = None
    stream_type: Optional[StreamType] = None
    is_secure: bool = False
    country: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None


class RadioSourceList(BaseModel):
    items: List[RadioSourceOut]
    total: int
    page: int
    page_size: int
