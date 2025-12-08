from typing import Optional
from pydantic import BaseModel, ConfigDict

from model.dto.stream_type import StreamTypeDTO

class RadioSourceDTO(BaseModel):
    """Data model for a radio source."""  

    id: int
    stream_url: str
    name: str
    website_url: Optional[str] = None
    
    # Classification data
    stream_type_id: int
    is_secure: bool
    
    # User-editable fields
    country: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    
    # Timestamps
    created_at: Optional[str] = None  # ISO formatted datetime string

    # Relationships
    stream_type: Optional[StreamTypeDTO] = None

    model_config = ConfigDict(from_attributes=True) 