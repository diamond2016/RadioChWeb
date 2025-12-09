"""
User DTO for data transfer.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserDTO(BaseModel):
    """DTO for User entity."""
    id: int
    email: str
    role: str
    hash_password: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)