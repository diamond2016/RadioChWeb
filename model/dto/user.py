"""
User DTO for data transfer.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserDTO(BaseModel):
    """DTO for User entity."""
    id: int
    email: str
    role: str
    hash_password : Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[str] = None
    last_modified_at: Optional[str] = None
      
    model_config = ConfigDict(from_attributes=True)