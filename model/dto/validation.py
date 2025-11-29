"""
Validation DTOs for proposal validation and security checks.
"""

from typing import Optional
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

    model_config = ConfigDict(use_enum_values=True)


class ProposalUpdateRequest(BaseModel):
    """Request DTO for updating proposal details."""
    name: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    user_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)