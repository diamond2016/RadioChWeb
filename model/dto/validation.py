"""
Validation DTOs for proposal validation and security checks.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

# Backwards import alias: some code/tests expect ProposalUpdateRequest in this module
try:
    from model.dto.proposal import ProposalUpdateRequest  # type: ignore
except Exception:
    ProposalUpdateRequest = None  # type: ignore


class SecurityStatusDTO(BaseModel):
    is_secure: bool
    warning_message: Optional[str] = None


class ValidationDTO(BaseModel):
    """Result of proposal validation and security checks."""
    is_valid: bool = True
    message: str = ""
    security_status: Optional[SecurityStatusDTO] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

    def add_error(self, error: str):
        """Add an error message and mark invalid."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)

# Backwards compatibility alias
ValidationResult = ValidationDTO

# Backwards compatibility alias for older name
SecurityStatus = SecurityStatusDTO

