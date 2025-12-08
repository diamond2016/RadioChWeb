"""
Validation DTOs for proposal validation and security checks.
"""

from dataclasses import dataclass
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from enum import Enum

@dataclass
class SecurityStatus:
    is_secure: bool
    warning_message: Optional[str]


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

