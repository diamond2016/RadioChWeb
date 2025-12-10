from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from model.dto.stream_type import StreamTypeDTO
from model.dto.user import UserDTO

class RadioSourceDTO(BaseModel):
    """Data model for a radio source."""  

    id: int
    stream_url: str
    name: str
    is_secure: bool
    stream_type: StreamTypeDTO
    
    # User-editable fields
    website_url: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    
    # Timestamps
    created_at: Optional[datetime] = None  
    updated_at: Optional[datetime] = None

    # Related user (from proposal)
    user: Optional[UserDTO] = None
    model_config = ConfigDict(from_attributes=True) 