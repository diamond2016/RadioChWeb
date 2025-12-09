"""
StreamAnalysisService - Core implementation of spec 003 analyze-and-classify-stream.

This service implements the dual validation strategy (curl + ffmpeg) and 
classification logic as defined in the specification.
"""

from datetime import date
import subprocess
import re
import shutil
from urllib.parse import urlparse
from typing import Optional, Dict, Any

from flask_login import current_user, login_required
from model.dto.user import UserDTO
from model.dto.stream_analysis import StreamAnalysisDTO, DetectionMethod, ErrorCode
from model.dto.validation import ValidationDTO, SecurityStatusDTO
from model.entity.proposal import Proposal
from model.entity.stream_analysis import StreamAnalysis
from model.repository import user_repository
from model.repository.stream_analysis_repository import StreamAnalysisRepository
from service.stream_type_service import StreamTypeService
from model.repository.proposal_repository import ProposalRepository


class StreamAnalysisService:
    """
    Core service implementing spec 003: analyze-and-classify-stream
    
    Performs dual validation:
    1. curl -I for headers/content-type analysis
    2. ffmpeg -i for deep format analysis
    3. FFmpeg is authoritative when results differ
    """
    
    def __init__(self, stream_type_service: StreamTypeService, proposal_repository: ProposalRepository, analysis_repository: StreamAnalysisRepository):
        self.stream_type_service: StreamTypeService = stream_type_service
        self.proposal_repository: ProposalRepository = proposal_repository
        self.analysis_repository: StreamAnalysisRepository = analysis_repository
        self.user_repository: user_repository.UserRepository = user_repository.UserRepository()
        self._check_prerequisites()

    def _check_prerequisites(self) -> None:
        """
        Check that required tools are available (NFR-001).
        Raises RuntimeError if prerequisites are not met.
        """
        if not shutil.which("ffmpeg"):
            raise RuntimeError("ffmpeg is not installed or not accessible in PATH. Required for stream analysis.")
        
        if not shutil.which("curl"):
            raise RuntimeError("curl is not installed or not accessible in PATH. Required for header analysis.")
    

    def _safe_current_user_id(self) -> Optional[int]:
        """Return current_user.id or None without raising outside-app-context errors."""
        try:
            return current_user.id if (current_user is not None and hasattr(current_user, 'id')) else None
        except RuntimeError:
            return None

    def _safe_current_user_dto(self) -> Optional[UserDTO]:
        """Return a UserDTO for the current user when available, else None.

        Uses repository.find_by_id to obtain the ORM user and then Pydantic's
        model_validate (from_attributes=True) to produce a DTO.
        """
        uid = self._safe_current_user_id()
        if not uid:
            return None
        try:
            orm_user = self.user_repository.find_by_id(uid)
            if orm_user:
                return UserDTO.model_validate(orm_user)
        except Exception:
            return None
        return None


    # Service method to analyze a stream and create a stream analysis
    def analyze_stream(self, url: str, timeout_seconds: int = 30) -> StreamAnalysisDTO:
        """
        Main entry point for stream analysis (spec 003).
        
        Args:
            url: The stream URL to analyze
            timeout_seconds: Maximum time to spend on analysis (default: 30s as per SC-001)
            
        Returns:
            StreamAnalysisDTO with validation and classification data
        """
        print("Starting analysis for URL: {}".format(url))
        # FR-004: Check for unsupported protocols first
        user: UserDTO | None = self._safe_current_user_dto()

        if not self._is_supported_protocol(url):
            result = StreamAnalysisDTO(
                stream_url=url,
                is_valid=False,
                is_secure=False,
                error_code=ErrorCode.UNSUPPORTED_PROTOCOL,
                user = user
            )
            return self._persist_analysis_and_return_dto(result)
        
        # Determine if URL is secure (HTTPS vs HTTP)
        is_secure = self._is_secure_url(url)
        
        try:
            # FR-002: Perform dual validation
            curl_result = self._analyze_with_curl(url, timeout_seconds)
            ffmpeg_result = self._analyze_with_ffmpeg(url, timeout_seconds)
            
            # FR-003: Compare results, ffmpeg is authoritative
            final_result: StreamAnalysisDTO = self._resolve_analysis_results(curl_result, ffmpeg_result, is_secure)
            # print("Analysis result for URL {}: {}".format(url, final_result))
            return self._persist_analysis_and_return_dto(final_result)
            
        except subprocess.TimeoutExpired:
            result = StreamAnalysisDTO(
                stream_url=url,
                is_valid=False,
                is_secure=is_secure,
                error_code=ErrorCode.TIMEOUT,
                user = user
            )
            return self._persist_analysis_and_return_dto(result)
            
            # FR-003: Compare results, ffmpeg is authoritative
            final_result: StreamAnalysisDTO = self._resolve_analysis_results(curl_result, ffmpeg_result, is_secure)
            # print("Analysis result for URL {}: {}".format(url, final_result))
            return final_result
        except Exception:
            result = StreamAnalysisDTO(
                stream_url=url,
                is_valid=False,
                is_secure=is_secure,
                error_code=ErrorCode.NETWORK_ERROR,
                user = user
            )
            return self._persist_analysis_and_return_dto(result)
    
    def _is_supported_protocol(self, url: str) -> bool:
        """Check if the URL uses a supported protocol (HTTP/HTTPS only)."""
        parsed = urlparse(url)
        return parsed.scheme.lower() in ['http', 'https']
    
    def _is_secure_url(self, url: str) -> bool:
        """Determine if URL is secure (HTTPS = true, HTTP = false)."""
        return urlparse(url).scheme.lower() == 'https'
    
    def _analyze_with_curl(self, url: str, timeout_seconds: int) -> Dict[str, Any]:
        """
        Analyze stream using curl -I to get headers and content-type.
        
        Returns:
            Dict with 'success', 'content_type', 'raw_output' keys
        """
        try:
            result = subprocess.run(
                ["curl", "-I", "--max-time", str(timeout_seconds), url],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False
            )
            
            if result.returncode != 0:
                return {"success": False, "content_type": None, "raw_output": result.stderr}
            
            # Extract content-type from headers
            content_type = self._extract_content_type(result.stdout)
            
            return {
                "success": True,
                "content_type": content_type,
                "raw_output": result.stdout
            }
            
        except subprocess.TimeoutExpired:
            raise
        except Exception as e:
            return {"success": False, "content_type": None, "raw_output": str(e)}
    

    def _analyze_with_ffmpeg(self, url: str, timeout_seconds: int) -> Dict[str, Any]:
        """
        Analyze stream using ffmpeg -i for deep format analysis.
        
        Returns:
            Dict with 'success', 'format', 'codec', 'raw_output' keys
        """
        try:
            result = subprocess.run(
                ["ffmpeg", "-i", url, "-t", "1", "-f", "null", "-"],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False
            )
            
            # ffmpeg writes info to stderr, not stdout
            output = result.stderr

            # Parse ffmpeg output for format and codec information
            format_info = self._parse_ffmpeg_output(output)

            # Extract metadata block from ffmpeg stderr (if present)
            extracted_metadata = self._extract_metadata_from_ffmpeg_output(output)

            return {
                "success": format_info is not None,
                "format": format_info.get("format") if format_info else None,
                "codec": format_info.get("codec") if format_info else None,
                "raw_output": output,
                "extracted_metadata": extracted_metadata
            }
            
        except subprocess.TimeoutExpired:
            raise
        except Exception as e:
            return {"success": False, "format": None, "codec": None, "raw_output": str(e)}
    

    def _extract_content_type(self, headers: str) -> Optional[str]:
        """Extract content-type from HTTP headers."""
        # Handle both actual newlines and literal \n in headers
        lines = headers.replace('\\n', '\n').split('\n')
        for line in lines:
            if line.lower().startswith('content-type:'):
                return line.split(':', 1)[1].strip()
        return None
    

    def _parse_ffmpeg_output(self, output: str) -> Optional[Dict[str, str]]:
        """
        Parse ffmpeg output to extract format and codec information.
        
        Example ffmpeg output:
        "Stream #0:0: Audio: mp3 (mp3float), 22050 Hz, mono, fltp, 24 kb/s"
        """
        # Look for audio stream information
        audio_match = re.search(r'Stream #\d+:\d+: Audio: (\w+)', output)
        if not audio_match:
            return None
        
        codec = audio_match.group(1).lower()
        
        # Map ffmpeg codec names to our format names
        format_mapping = {
            'mp3': 'MP3',
            'aac': 'AAC', 
            'ogg': 'OGG',
            'vorbis': 'OGG'
        }
        
        format_name = format_mapping.get(codec, codec.upper())
        
        return {
            "format": format_name,
            "codec": codec
        }


    def _extract_metadata_from_ffmpeg_output(self, output: str) -> Optional[str]:
        """
        Extract the 'Metadata:' block from ffmpeg stderr output and return a
        normalized plain-text snippet. Returns None when no metadata block found.

        Strategy:
        - Normalize newlines, find last occurrence of a line matching '^\\s*Metadata:\\s*$'.
        - Capture subsequent indented lines (leading whitespace) until an empty
          line or a non-indented section header is found.
        - Strip control characters (keep newline and tab), normalize colon spacing,
          trim and truncate to 4096 chars.
        """
        if not output or not isinstance(output, str):
            return None

        norm = output.replace('\r\n', '\n').replace('\r', '\n')

        # Find all 'Metadata:' markers; choose the last one
        meta_matches = [m.start() for m in re.finditer("^\\s*Metadata:\\s*$", norm, flags=re.MULTILINE)]
        if not meta_matches:
            return None

        # Start scanning from the last metadata marker
        last_pos = meta_matches[-1]
        tail = norm[last_pos:]
        lines = tail.split('\n')

        # Skip the 'Metadata:' line itself
        captured = []
        for line in lines[1:]:
            if line.strip() == "":
                break
            # Stop if we hit a new ffmpeg section header (Stream, Input, Output, Duration, etc.)
            if re.match(r"^\s*(Stream|Input|Output|Duration|At least)\b", line):
                break
            # Consider indented lines as metadata lines
            if re.match(r"^\s+", line):
                # normalize: remove leading whitespace, normalize spacing around ':'
                stripped = line.strip()
                # replace multiple spaces around colon
                if ':' in stripped:
                    parts = stripped.split(':', 1)
                    key = parts[0].strip()
                    val = parts[1].strip()
                    captured.append(f"{key}: {val}")
                else:
                    captured.append(stripped)
            else:
                break

        if not captured:
            return None

        joined = "\n".join(captured)

        # Remove control chars except newline and tab
        cleaned = ''.join(ch for ch in joined if (ch >= ' ' or ch in '\n\t'))
        cleaned = cleaned.strip()
        if len(cleaned) > 4096:
            cleaned = cleaned[:4096]
        return cleaned
    

    def _resolve_analysis_results(self, curl_result: dict, ffmpeg_result: dict, is_secure: bool) -> StreamAnalysisDTO:
        """
        Resolve analysis results from curl and ffmpeg.
        FR-003: FFmpeg is authoritative when results differ.
        """
        user: UserDTO | None = self._safe_current_user_dto()

        # If ffmpeg failed, try to use curl results
        if not ffmpeg_result["success"]:
            if curl_result["success"]:
                return self._classify_from_curl(curl_result, is_secure)
            else:
                return StreamAnalysisDTO(
                    stream_url=curl_result["stream_url"] if "stream_url" in curl_result else None,
                    is_valid=False,
                    is_secure=is_secure,
                    error_code=ErrorCode.UNREACHABLE,
                    raw_content_type=curl_result.get("raw_output"),
                    raw_ffmpeg_output=ffmpeg_result.get("raw_output"),
                    extracted_metadata=ffmpeg_result.get("extracted_metadata"),
                    user = user
                )
        
        # FFmpeg succeeded - use it as authoritative source
        format_name = ffmpeg_result["format"]
        user: UserDTO | None = self._safe_current_user_dto()

        if not format_name:
            return StreamAnalysisDTO(
                is_valid=False,
                stream_url=ffmpeg_result["stream_url"] if "stream_url" in ffmpeg_result else None,   
                is_secure=is_secure,
                error_code=ErrorCode.INVALID_FORMAT,
                raw_content_type=curl_result.get("raw_output"),
                raw_ffmpeg_output=ffmpeg_result.get("raw_output"),
                extracted_metadata=ffmpeg_result.get("extracted_metadata"),
                user = user
            )
        
        # Determine protocol (HTTP/HTTPS based on URL, or HLS if m3u8 detected)
        protocol = "HTTPS" if is_secure else "HTTP"
        if ".m3u8" in ffmpeg_result.get("raw_output", "").lower():
            protocol = "HLS"
        
        # Detect metadata support (basic heuristic - could be enhanced)
        metadata = self._detect_metadata_support(curl_result.get("raw_output", ""))
        
        # Find matching StreamType
        stream_type_id = self.stream_type_service.find_stream_type_id(protocol, format_name, metadata)
        
        detection_method = DetectionMethod.BOTH if curl_result["success"] else DetectionMethod.FFMPEG
        
        return StreamAnalysisDTO(
            is_valid=stream_type_id is not None,
            stream_type_id=stream_type_id,
            stream_type_display_name=self.stream_type_service.get_display_name(stream_type_id) if stream_type_id else None,
            stream_url=ffmpeg_result["stream_url"] if "stream_url" in ffmpeg_result else None,
            is_secure=is_secure,
            error_code=None,
            detection_method=detection_method,
            raw_content_type=curl_result.get("raw_output"),
            raw_ffmpeg_output=ffmpeg_result.get("raw_output"),
            extracted_metadata=ffmpeg_result.get("extracted_metadata"),
            user = user
        )
    
    def _classify_from_curl(self, curl_result: dict, is_secure: bool) -> StreamAnalysisDTO:
        """Classify stream based only on curl content-type headers."""
        content_type = curl_result["content_type"]
        user: UserDTO | None = self._safe_current_user_dto()

        if not content_type:
            return StreamAnalysisDTO(
                is_valid=False,
                is_secure=is_secure,
                error_code=ErrorCode.INVALID_FORMAT,
                raw_content_type=curl_result.get("raw_output"),
                user = user
            )
        
        # Map content-type to format
        format_name = None
        if "audio/mpeg" in content_type.lower() or "audio/mp3" in content_type.lower():
            format_name = "MP3"
        elif "audio/aac" in content_type.lower():
            format_name = "AAC"
        elif "audio/ogg" in content_type.lower():
            format_name = "OGG"
        elif "application/vnd.apple.mpegurl" in content_type.lower():
            # HLS playlist
            protocol = "HLS"
            format_name = "AAC"  # Most common for HLS
            stream_type_id = self.stream_type_service.find_stream_type_id(protocol, format_name, "None")
            return StreamAnalysisDTO(
                is_valid=stream_type_id is not None,
                stream_type_id=stream_type_id,
                stream_type_display_name=self.stream_type_service.get_display_name(stream_type_id) if stream_type_id else None,
                stream_url=curl_result.get("stream_url", None),
                is_secure=is_secure,
                detection_method=DetectionMethod.HEADER,
                raw_content_type=curl_result.get("raw_output"),
                user = user
            )

        if not format_name:
            return StreamAnalysisDTO(
                is_valid=False,
                is_secure=is_secure,
                error_code=ErrorCode.INVALID_FORMAT,
                raw_content_type=curl_result.get("raw_output"),
                user = user
            )
        
        protocol = "HTTPS" if is_secure else "HTTP"
        metadata = self._detect_metadata_support(curl_result.get("raw_output", ""))
        stream_type_id = self.stream_type_service.find_stream_type_id(protocol, format_name, metadata)
        
        return StreamAnalysisDTO(
            is_valid=stream_type_id is not None,
            stream_type_id=stream_type_id,
            stream_type_display_name=self.stream_type_service.get_display_name(stream_type_id) if stream_type_id else None,
            stream_url=curl_result.get("stream_url", None),
            is_secure=is_secure,
            detection_method=DetectionMethod.HEADER,
            raw_content_type=curl_result.get("raw_output"),
            user = user
        )
    
    def _persist_analysis_and_return_dto(self, analysis_dto: StreamAnalysisDTO) -> StreamAnalysisDTO:
        """Persist a StreamAnalysis ORM record from the DTO-like object and return a fresh DTO with transient validation attached."""
        # Build a minimal ValidationDTO based on analysis outcome
        validation = ValidationDTO(is_valid=getattr(analysis_dto, 'is_valid', True), message="")
        if getattr(analysis_dto, 'is_secure', None) is not None:
            validation.security_status = SecurityStatusDTO(is_secure=analysis_dto.is_secure)

        # Map enums to plain values when persisting
        detection = None
        if getattr(analysis_dto, 'detection_method', None) is not None:
            dm = analysis_dto.detection_method
            detection = dm.value if hasattr(dm, 'value') else str(dm)

        error_code_val = None
        if getattr(analysis_dto, 'error_code', None) is not None:
            ec = analysis_dto.error_code
            error_code_val = ec.value if hasattr(ec, 'value') else str(ec)

        analysis = StreamAnalysis(
            stream_url=getattr(analysis_dto, 'stream_url', None),
            stream_type_id=getattr(analysis_dto, 'stream_type_id', None),
            is_valid=getattr(analysis_dto, 'is_valid', False),
            is_secure=getattr(analysis_dto, 'is_secure', False),
            error_code=error_code_val,
            detection_method=detection,
            raw_content_type=getattr(analysis_dto, 'raw_content_type', None),
            raw_ffmpeg_output=getattr(analysis_dto, 'raw_ffmpeg_output', None),
            extracted_metadata=getattr(analysis_dto, 'extracted_metadata', None),
            created_by=self._safe_current_user_id()
        )

        saved = self.analysis_repository.save(analysis)

        dto = StreamAnalysisDTO.model_validate(saved)
        dto.validation = validation
        return dto
    
    def _detect_metadata_support(self, headers: str) -> str:
        """
        Detect metadata support (Icecast/Shoutcast) from headers.
        Basic heuristic - could be enhanced with more sophisticated detection.
        """
        if not headers:
            return "None"
        
        # Handle both actual newlines and literal \n in headers
        headers_normalized = headers.replace('\\n', '\n')
        headers_lower = headers_normalized.lower()
        
        # Check for Shoutcast first (more specific)
        if "shoutcast" in headers_lower:
            return "Shoutcast"
        elif "icecast" in headers_lower or "icy-" in headers_lower:
            return "Icecast"
        else:
            return "None"
    
    # Service method: transform an analysis into a proposal
    def save_analysis_as_proposal(self, stream_id: int) -> bool:
        """
        Approve an analysis and create a proposal for radio source.

        Accepts integer id of StreamAnalysis.
        Returns True on successful creation, False otherwise.
        """
        # Resolve input to an analysis entity/object
        stream_entity = None
        stream_entity: StreamAnalysis | None = self.analysis_repository.find_by_id(stream_id)

        if not stream_entity:
            print("Cannot create proposal: analysis not found or invalid input.")
            return False

        # Determine required fields
        stream_url = getattr(stream_entity, 'stream_url', None)
        stream_type_id = getattr(stream_entity, 'stream_type_id', None)
        is_secure = getattr(stream_entity, 'is_secure', False)
        is_valid = getattr(stream_entity, 'is_valid', True)

        if not is_valid or not stream_url or not stream_type_id:
            print("Cannot create proposal for invalid analysis or missing data.")
            return False

        current_uid = self._safe_current_user_id()
        if (not current_uid or current_uid != getattr(stream_entity.user, 'id', None)):
            print("Cannot create proposal: no authenticated user or no matching user.")
            return False

        # Prefer the already-loaded user relationship from the analysis entity
        proposal_user = getattr(stream_entity, 'user', None)

        if proposal_user is None:
            # Try to fetch from repository but fail gracefully if no app context
            try:
                proposal_user = self.user_repository.find_by_id(current_uid)
            except RuntimeError:
                proposal_user = None

        proposal = Proposal(
            stream_url=stream_url,
            name="",
            website_url=None,
            country=None,
            description=None,
            image_url=None,
            stream_type_id=stream_type_id,
            is_secure=is_secure,
            created_at=date.today(),
            created_by=current_uid
        )

        # Save proposal to repository
        try:
            self.proposal_repository.save(proposal)
            print("Proposal created for stream URL: {}".format(stream_url))
            # After successfully creating a proposal, try to remove the originating analysis
            self.delete_analysis(stream_id)
            return True
        
        except Exception as e:  
            print(f"Failed to save proposal: {e}")
            return False


    # Service method: delete a StreamAnalysis by id
    def delete_analysis(self, stream_id: int) -> bool:
        """
        Delete a StreamAnalysis by id or by object.

        Returns True if deletion was successful, False otherwise.
        """
        stream_entity: StreamAnalysis | None = self.analysis_repository.find_by_id(stream_id)  
        current_uid = self._safe_current_user_id()
        if (not current_uid or current_uid != getattr(stream_entity, 'created_by', None)):
            print("Cannot delete analysis: no authenticated user or no matching user.")
            return False
        
        # If an object provided, try to get id

        return self.analysis_repository.delete(stream_id)