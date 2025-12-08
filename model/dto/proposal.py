"""
Proposal DTOs for proposal data transfer.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict

from model.dto import user
from model.dto.stream_type import StreamTypeDTO
from model.dto.user import UserDTO

class ProposalUpdateRequest(BaseModel):
    """Request DTO for updating proposal details."""
    name: Optional[str] = None
    website_url: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    def has_updates(self) -> bool:
        """Check if any updates are provided."""
        return any([
            self.name is not None,
            self.website_url is not None,
            self.country is not None,
            self.description is not None,
            self.image_url is not None
        ])


class ProposalRequest(BaseModel):
    """Data model for a proposal."""    
    id: int
    stream_url: str
    name: str
    website_url: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    stream_type_id: int
    is_secure: bool
    
    model_config = ConfigDict(from_attributes=True)
    def __repr__(self):
        return f"<Proposal(id={self.id}, name='{self.name}', stream_url='{self.stream_url}', is_secure={self.is_secure})>"
    

class ProposalDTO(BaseModel):
    """Data model for a proposal."""    
    id: int
    stream_url: str
    name: Optional[str] = None
    website_url: Optional[str] = None
    stream_type_id: int
    is_secure: bool
    country: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    created_at: Optional[str] = None  # ISO formatted datetime string
    stream_type: Optional[StreamTypeDTO] = None
    user: Optional[user.UserDTO] = None

    model_config = ConfigDict(from_attributes=True)
    