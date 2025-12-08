"""
User DTO for data transfer.
"""

from pydantic import BaseModel, ConfigDict


class UserDTO(BaseModel):
    """DTO for User entity."""
    id: int
    email: str
    role: str
       
    model_config = ConfigDict(from_attributes=True)