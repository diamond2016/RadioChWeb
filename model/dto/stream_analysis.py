"""
Stream analysis DTOs as defined in spec 003.
StreamAnalysisResult is the main return type from the analyze-and-classify process.
"""

from typing import Optional
from pydantic import BaseModel, HttpUrl, ConfigDict
from pydantic import field_validator
from enum import Enum


class DetectionMethod(str, Enum):
    HEADER = "HEADER"
    FFMPEG = "FFMPEG"
    BOTH = "BOTH"


class ErrorCode(str, Enum):
    TIMEOUT = "TIMEOUT"
    UNSUPPORTED_PROTOCOL = "UNSUPPORTED_PROTOCOL"
    UNREACHABLE = "UNREACHABLE"
    INVALID_FORMAT = "INVALID_FORMAT"
    NETWORK_ERROR = "NETWORK_ERROR"


class StreamAnalysisRequest(BaseModel):
    """Request DTO for stream analysis (spec 003)."""

    url: HttpUrl
    timeout_seconds: int = 30

    model_config = ConfigDict(json_encoders={HttpUrl: str})


class StreamAnalysisResult(BaseModel):
    """
    Data structure returned by analysis process (persisted for page proposal.html).
    This is the main return type from spec 003 analyze-and-classify process.
    """

    is_valid: bool
    is_secure: bool  # False for HTTP, true for HTTPS
    stream_url: Optional[str] = None  # if loaded is the url of proposal stream
    stream_type_id: Optional[int] = None  # Foreign key to StreamType, null if invalid
    stream_type_display_name: Optional[str] = (
        None  # Human-readable name of the stream type
    )
    error_code: Optional[ErrorCode] = None  # Null if valid
    detection_method: Optional[DetectionMethod] = None  # How the stream was detected
    raw_content_type: Optional[str] = None  # String from curl headers
    raw_ffmpeg_output: Optional[str] = None  # String from ffmpeg detection
    extracted_metadata: Optional[str] = (
        None  # Normalized metadata extracted from ffmpeg stderr
    )

    @field_validator("extracted_metadata")
    def _clean_extracted_metadata(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        # remove control chars except newline and tab, trim, and enforce max length
        cleaned = "".join(ch for ch in v if (ch >= " " or ch in "\n\t"))
        cleaned = cleaned.strip()
        if len(cleaned) > 4096:
            cleaned = cleaned[:4096]
        return cleaned

    def is_success(self) -> bool:
        """Returns True if analysis was successful and stream is valid."""
        return self.is_valid and self.error_code is None

    model_config = ConfigDict(from_attributes=True)
