from typing import List
from pydantic import BaseModel, ConfigDict


class StreamTypeOut(BaseModel):
    """Schema for StreamType entity."""
    id: int
    display_name: str
    model_config = ConfigDict(from_attributes=True) 

class StreamTypeList(BaseModel):
    """Schema for StreamType list entity."""
    items: List[StreamTypeOut]
    total: int
    page: int
    page_size: int
    model_config = ConfigDict(from_attributes=True) 