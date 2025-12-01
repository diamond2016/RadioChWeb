"""
Validation DTOs for proposal validation and security checks.
"""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from enum import Enum


class SecurityStatus(str, Enum):
    SAFE = "SAFE"
    WARNING = "WARNING"
    UNSAFE = "UNSAFE"


class ValidationResult(BaseModel):
    """Result of proposal validation."""
    is_valid: bool
    message: str = ""
    security_status: Optional[SecurityStatus] = None
    errors: List[str] = []
    warnings: List[str] = []

    model_config = ConfigDict(from_attributes=True)

    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)


class ProposalUpdateRequest(BaseModel):
    """Request DTO for updating proposal details."""
    name: Optional[str] = None
    website_url: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    def has_updates(self) -> bool:
        """Check if any updates are provided."""
        return any([
            self.name is not None,
            self.website_url is not None,
            self.country is not None,
            self.description is not None,
            self.image is not None
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