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

