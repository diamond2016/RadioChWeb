"""
StreamAnalysisService - Core implementation of spec 003 analyze-and-classify-stream.

This service implements the dual validation strategy (curl + ffmpeg) and 
classification logic as defined in the specification.
"""

import subprocess
import re
import shutil
from urllib.parse import urlparse
from typing import Optional, Dict, Any
from model.dto.stream_analysis import StreamAnalysisResult, DetectionMethod, ErrorCode
from service.stream_type_service import StreamTypeService


class StreamAnalysisService:
    """
    Core service implementing spec 003: analyze-and-classify-stream
    
    Performs dual validation:
    1. curl -I for headers/content-type analysis
    2. ffmpeg -i for deep format analysis
    3. FFmpeg is authoritative when results differ
    """
    
    def __init__(self, stream_type_service: StreamTypeService):
        self.stream_type_service = stream_type_service
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
    
    def analyze_stream(self, url: str, timeout_seconds: int = 30) -> StreamAnalysisResult:
        """
        Main entry point for stream analysis (spec 003).
        
        Args:
            url: The stream URL to analyze
            timeout_seconds: Maximum time to spend on analysis (default: 30s as per SC-001)
            
        Returns:
            StreamAnalysisResult with validation and classification data
        """
        print("Starting analysis for URL: {}".format(url))
        # FR-004: Check for unsupported protocols first
        if not self._is_supported_protocol(url):
            return StreamAnalysisResult(
                stream_url=url,
                is_valid=False,
                is_secure=False,
                error_code=ErrorCode.UNSUPPORTED_PROTOCOL
            )
        
        # Determine if URL is secure (HTTPS vs HTTP)
        is_secure = self._is_secure_url(url)
        
        try:
            # FR-002: Perform dual validation
            curl_result = self._analyze_with_curl(url, timeout_seconds)
            ffmpeg_result = self._analyze_with_ffmpeg(url, timeout_seconds)
            
            # FR-003: Compare results, ffmpeg is authoritative
            final_result: StreamAnalysisResult = self._resolve_analysis_results(curl_result, ffmpeg_result, is_secure)
            
            return final_result
            
        except subprocess.TimeoutExpired:
            return StreamAnalysisResult(
                stream_url=url,
                is_valid=False,
                is_secure=is_secure,
                error_code=ErrorCode.TIMEOUT
            )
        except Exception:
            return StreamAnalysisResult(

                is_valid=False,
                is_secure=is_secure,
                error_code=ErrorCode.NETWORK_ERROR
            )
    
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
            
            return {
                "success": format_info is not None,
                "format": format_info.get("format") if format_info else None,
                "codec": format_info.get("codec") if format_info else None,
                "raw_output": output
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
    
    def _resolve_analysis_results(self, curl_result: dict, ffmpeg_result: dict, is_secure: bool) -> StreamAnalysisResult:
        """
        Resolve analysis results from curl and ffmpeg.
        FR-003: FFmpeg is authoritative when results differ.
        """
        # If ffmpeg failed, try to use curl results
        if not ffmpeg_result["success"]:
            if curl_result["success"]:
                return self._classify_from_curl(curl_result, is_secure)
            else:
                return StreamAnalysisResult(
                    stream_url=curl_result["stream_url"] if "stream_url" in curl_result else None,
                    is_valid=False,
                    is_secure=is_secure,
                    error_code=ErrorCode.UNREACHABLE,
                    raw_content_type=curl_result.get("raw_output"),
                    raw_ffmpeg_output=ffmpeg_result.get("raw_output")
                )
        
        # FFmpeg succeeded - use it as authoritative source
        format_name = ffmpeg_result["format"]
        if not format_name:
            return StreamAnalysisResult(
                is_valid=False,
                stream_url=ffmpeg_result["stream_url"] if "stream_url" in ffmpeg_result else None,   
                is_secure=is_secure,
                error_code=ErrorCode.INVALID_FORMAT,
                raw_content_type=curl_result.get("raw_output"),
                raw_ffmpeg_output=ffmpeg_result.get("raw_output")
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
        
        return StreamAnalysisResult(
            is_valid=stream_type_id is not None,
            stream_type_id=stream_type_id,
            stream_type_display_name=self.stream_type_service.get_display_name(stream_type_id) if stream_type_id else None,
            stream_url=ffmpeg_result["stream_url"] if "stream_url" in ffmpeg_result else None,
            is_secure=is_secure,
            error_code=None,
            detection_method=detection_method,
            raw_content_type=curl_result.get("raw_output"),
            raw_ffmpeg_output=ffmpeg_result.get("raw_output")
        )
    
    def _classify_from_curl(self, curl_result: dict, is_secure: bool) -> StreamAnalysisResult:
        """Classify stream based only on curl content-type headers."""
        content_type = curl_result["content_type"]
        if not content_type:
            return StreamAnalysisResult(
                is_valid=False,
                is_secure=is_secure,
                error_code=ErrorCode.INVALID_FORMAT,
                raw_content_type=curl_result.get("raw_output")
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
            return StreamAnalysisResult(
                is_valid=stream_type_id is not None,
                stream_type_id=stream_type_id,
                stream_type_display_name=self.stream_type_service.get_display_name(stream_type_id) if stream_type_id else None,
                stream_url=curl_result.get("stream_url", None),
                is_secure=is_secure,
                detection_method=DetectionMethod.HEADER,
                raw_content_type=curl_result.get("raw_output")
            )
        
        if not format_name:
            return StreamAnalysisResult(
                is_valid=False,
                is_secure=is_secure,
                error_code=ErrorCode.INVALID_FORMAT,
                raw_content_type=curl_result.get("raw_output")
            )
        
        protocol = "HTTPS" if is_secure else "HTTP"
        metadata = self._detect_metadata_support(curl_result.get("raw_output", ""))
        stream_type_id = self.stream_type_service.find_stream_type_id(protocol, format_name, metadata)
        
        return StreamAnalysisResult(
            is_valid=stream_type_id is not None,
            stream_type_id=stream_type_id,
            stream_type_display_name=self.stream_type_service.get_display_name(stream_type_id) if stream_type_id else None,
            stream_url=curl_result.get("stream_url", None),
            is_secure=is_secure,
            detection_method=DetectionMethod.HEADER,
            raw_content_type=curl_result.get("raw_output")
        )
    
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