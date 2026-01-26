from typing import List
from pydantic import BaseModel


class StreamTypeOut(BaseModel):
    """Schema for StreamType entity."""
    id: int
    display_name: str

class StreamTypeList(BaseModel):
    """Schema for StreamType list entity."""
    items: List[StreamTypeOut]
    total: int
    page: int
    page_size: int