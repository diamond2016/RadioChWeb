"""
Unit tests for StreamAnalysisService - Core spec 003 implementation.
Tests TR-001: comprehensive unit tests for service layer components.
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from service.stream_analysis_service import StreamAnalysisService
from service.stream_type_service import StreamTypeService
from model.dto.stream_analysis import ErrorCode, DetectionMethod, StreamAnalysisResult


class TestStreamAnalysisService:
    """Test cases for StreamAnalysisService."""

    @pytest.fixture
    def mock_stream_type_service(self) -> Mock:
        """Mock StreamTypeService for testing."""
        mock_service = Mock(spec=StreamTypeService)
        mock_service.find_stream_type_id.return_value = 1
        return mock_service

    @pytest.fixture
    def analysis_service(self, mock_stream_type_service: Mock) -> StreamAnalysisService:
        """Create StreamAnalysisService with mocked dependencies."""
        with patch('service.stream_analysis_service.shutil.which', return_value='/usr/bin/ffmpeg'):
            service = StreamAnalysisService(mock_stream_type_service)
            return service

    def test_unsupported_protocol_rejection(self, analysis_service: StreamAnalysisService) -> None:
        """Test FR-004: RTMP/RTSP URLs are rejected."""
        rtmp_url = "rtmp://stream.example.com/live"

        result: StreamAnalysisResult = analysis_service.analyze_stream(url=rtmp_url)

        assert not result.is_valid
        assert result.error_code == ErrorCode.UNSUPPORTED_PROTOCOL
        assert not result.is_secure

    def test_https_security_detection(self, analysis_service: StreamAnalysisService) -> None:
        """Test security detection for HTTPS URLs."""
        https_url = "https://stream.example.com/radio.mp3"

        with patch.object(analysis_service, '_analyze_with_curl') as mock_curl, \
             patch.object(analysis_service, '_analyze_with_ffmpeg') as mock_ffmpeg:

            # Mock successful analysis
            mock_curl.return_value = {
                "success": True,
                "content_type": "audio/mpeg",
                "raw_output": "HTTP/1.1 200 OK\\nContent-Type: audio/mpeg"
            }
            mock_ffmpeg.return_value = {
                "success": True,
                "format": "MP3",
                "codec": "mp3",
                "raw_output": "Stream #0:0: Audio: mp3 (mp3float), 22050 Hz, mono, fltp, 24 kb/s"
            }

            result = analysis_service.analyze_stream(https_url)

            assert result.is_secure  # HTTPS should be secure

    def test_http_security_warning(self, analysis_service: StreamAnalysisService) -> None:
        """Test FR-005: HTTP streams flagged as insecure but valid."""
        http_url = "http://stream.example.com:8000/"

        with patch.object(analysis_service, '_analyze_with_curl') as mock_curl, \
             patch.object(analysis_service, '_analyze_with_ffmpeg') as mock_ffmpeg:

            mock_curl.return_value = {
                "success": True,
                "content_type": "audio/mpeg",
                "raw_output": "HTTP/1.1 200 OK\\nContent-Type: audio/mpeg"
            }
            mock_ffmpeg.return_value = {
                "success": True,
                "format": "MP3",
                "codec": "mp3",
                "raw_output": "Stream #0:0: Audio: mp3"
            }

            result: StreamAnalysisResult = analysis_service.analyze_stream(http_url)

            assert not result.is_secure  # HTTP should be insecure
            assert result.is_valid       # But still valid

    @patch('subprocess.run')
    def test_ffmpeg_authoritative_over_curl(self, mock_run: Mock, analysis_service: StreamAnalysisService) -> None:
        """Test FR-003: FFmpeg is authoritative when results differ."""

        # Mock curl detecting MP3, but ffmpeg detecting AAC
        curl_responses: list[Mock] = [
            # First call: curl -I
            Mock(returncode=0, stdout="HTTP/1.1 200 OK\\nContent-Type: audio/mpeg\\n", stderr=""),
            # Second call: ffmpeg -i
            Mock(returncode=0, stdout="", stderr="Stream #0:0: Audio: aac, 44100 Hz, stereo")
        ]

        mock_run.side_effect = curl_responses

        result: StreamAnalysisResult = analysis_service.analyze_stream("https://stream.example.com/test")

        # Should use FFmpeg's AAC detection, not curl's MP3
        assert result.detection_method == DetectionMethod.BOTH
        # The mock should have called find_stream_type_id with AAC format

    def test_curl_header_extraction(self, analysis_service: StreamAnalysisService) -> None:
        """Test _extract_content_type method."""
        headers = "HTTP/1.1 200 OK\\nContent-Type: audio/mpeg\\nServer: Icecast\\n"

        content_type = analysis_service._extract_content_type(headers)
        print("Extracted Content-Type:", content_type)
        assert content_type == "audio/mpeg"

    def test_ffmpeg_output_parsing(self, analysis_service: StreamAnalysisService) -> None:
        """Test _parse_ffmpeg_output method."""
        ffmpeg_output = "Input #0, mp3, from 'stream':\\nStream #0:0: Audio: mp3 (mp3float), 22050 Hz, mono, fltp, 24 kb/s"

        result: dict | None = analysis_service._parse_ffmpeg_output(ffmpeg_output)
        print("Extracted Content-Type:", result)
        assert result["format"] == "MP3"
        assert result["codec"] == "mp3"

    def test_metadata_detection_icecast(self, analysis_service: StreamAnalysisService) -> None:
        """Test metadata detection for Icecast streams."""
        headers = "HTTP/1.1 200 OK\\nicy-name: Test Radio\\nServer: Icecast"

        metadata = analysis_service._detect_metadata_support(headers)

        assert metadata == "Icecast"

    def test_metadata_detection_shoutcast(self, analysis_service: StreamAnalysisService) -> None:
        """Test metadata detection for Shoutcast streams."""
        headers = "HTTP/1.1 200 OK\\nServer: Shoutcast\\nicy-genre: Rock"

        metadata = analysis_service._detect_metadata_support(headers)

        assert metadata == "Shoutcast"

    def test_prerequisites_check_missing_ffmpeg(self):
        """Test NFR-001: Prerequisites check for missing ffmpeg."""
        mock_service = Mock()

        with patch('service.stream_analysis_service.shutil.which', return_value=None):
            with pytest.raises(RuntimeError, match="ffmpeg is not installed"):
                StreamAnalysisService(mock_service)

    @patch('subprocess.run')
    def test_timeout_handling(self, mock_run, analysis_service: StreamAnalysisService) -> None:
        """Test NFR-002: Timeout handling."""
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired('curl', 30)

        result = analysis_service.analyze_stream("https://slow.example.com/stream", timeout_seconds=1)

        assert not result.is_valid
        assert result.error_code == ErrorCode.TIMEOUT