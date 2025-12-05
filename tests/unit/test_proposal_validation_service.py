"""
Unit tests for ProposalValidationService.

Tests validation logic for proposals including:
- Required field validation
- URL format validation
- Duplicate detection
- Security status checks
"""

import pytest
from unittest.mock import Mock

from model.dto.stream_analysis import StreamAnalysisResult
from model.dto.validation import ValidationResult
from model.repository.proposal_repository import ProposalRepository
from model.repository.radio_source_repository import RadioSourceRepository
from service.proposal_validation_service import ProposalValidationService
from model.entity.proposal import Proposal
from model.entity.radio_source import RadioSource
from model.entity.stream_analysis import StreamAnalysis
from service.stream_analysis_service import StreamAnalysisService


@pytest.fixture
def mock_proposal_repo() -> ProposalRepository:
    """Create mock ProposalRepository."""
    return Mock(spec=ProposalRepository)


@pytest.fixture
def mock_radio_source_repo() -> RadioSourceRepository:
    """Create mock RadioSourceRepository."""
    return Mock(spec=RadioSourceRepository)


@pytest.fixture
def mock_stream_analysis_service() -> StreamAnalysisService:
    """Create mock StreamAnalysisService."""
    return Mock(spec=StreamAnalysisService)


@pytest.fixture
def validation_service(
    mock_proposal_repo: ProposalRepository,
    mock_radio_source_repo: RadioSourceRepository,
) -> ProposalValidationService:
    """Create ProposalValidationService with mocked repositories."""
    return ProposalValidationService(mock_proposal_repo, mock_radio_source_repo)


class TestProposalValidationService:
    """Test suite for ProposalValidationService."""

    def test_validate_proposal_success(
        self,
        validation_service: ProposalValidationService,
        mock_proposal_repo: ProposalRepository,
        mock_stream_analysis_service: StreamAnalysisService,
        mock_radio_source_repo: RadioSourceRepository,
    ) -> None:
        """Test validation succeeds for valid proposal."""

        url = "https://stream.example.com/radio.mp3"
        mock_analysis_result: StreamAnalysisResult = (
            mock_stream_analysis_service.analyze_stream(url).return_value
        )
        mock_analysis_result.success = True
        mock_analysis_result.content_type = "audio/mpeg"
        mock_analysis_result.raw_output = "HTTP/1.1 200 OK\nContent-Type: audio/mpeg"
        mock_analysis_result.security_status = "UNSAFE"
        mock_analysis_result.is_valid = True
        mock_analysis_result.is_secure = True
        mock_analysis_result.stream_url = url
        mock_analysis_result.stream_type_id = 1

        # Arrange
        proposal = Proposal(
            id=1,
            stream_url=mock_analysis_result.stream_url,
            name="Test Radio",
            website_url="http://example.com",
            stream_type_id=mock_analysis_result.stream_type_id,
            is_secure=True,
        )

        mock_proposal_repo.find_by_id.return_value = proposal
        mock_radio_source_repo.find_by_url.return_value = None  # No duplicate
        mock_stream_analysis_service.analyze_stream.return_value = mock_analysis_result

        # Act
        result: ValidationResult = validation_service.validate_proposal(1)

        # Assert
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_validate_proposal_missing_required_fields(
        self,
        validation_service: ProposalValidationService,
        mock_proposal_repo: ProposalRepository,
    ):
        """Test validation fails for missing required fields."""
        # Arrange
        proposal = Proposal(
            id=1,
            stream_url="",  # Empty required field
            name="Test Radio",
            website_url="https://example.com",
            stream_type_id=1,
            is_secure=True,
        )
        mock_proposal_repo.find_by_id.return_value = proposal

        # Act
        result = validation_service.validate_proposal(1)

        # Assert
        assert not result.is_valid
        assert "Stream URL is required and cannot be empty" in result.errors

    def test_validate_proposal_invalid_url_format(
        self,
        validation_service: ProposalValidationService,
        mock_proposal_repo: ProposalRepository,
    ):
        """Test validation fails for invalid URL format."""
        # Arrange
        proposal = Proposal(
            id=1,
            stream_url="not-a-valid-url",
            name="Test Radio",
            website_url="https://example.com",
            stream_type_id=1,
            is_secure=True,
        )
        mock_proposal_repo.find_by_id.return_value = proposal

        # Act
        result = validation_service.validate_proposal(1)

        # Assert
        assert not result.is_valid
        assert "Invalid stream URL format: not-a-valid-url" in result.errors

    def test_validate_proposal_duplicate_stream_url(
        self,
        validation_service: ProposalValidationService,
        mock_proposal_repo: ProposalRepository,
        mock_radio_source_repo: RadioSourceRepository,
    ):
        """Test validation fails for duplicate stream URL."""
        # Arrange
        proposal = Proposal(
            id=1,
            stream_url="https://stream.example.com/radio.mp3",
            name="Test Radio",
            website_url="https://example.com",
            stream_type_id=1,
            is_secure=True,
        )
        mock_proposal_repo.find_by_id.return_value = proposal
        mock_radio_source_repo.find_by_url.return_value = RadioSource(
            id=1,
            stream_url="https://stream.example.com/radio.mp3",
            name="Existing Radio",
            website_url="https://existing.com",
            stream_type_id=1,
            is_secure=True,
        )

        # Act
        result = validation_service.validate_proposal(1)

        # Assert
        assert not result.is_valid
        assert "This stream URL already exists in the database" in result.errors

    def test_validate_proposal_insecure_stream_warning(
        self,
        validation_service: ProposalValidationService,
        mock_proposal_repo: ProposalRepository,
        mock_radio_source_repo: RadioSourceRepository,
    ):
        """Test validation warns for insecure HTTP streams."""
        # Arrange
        proposal = Proposal(
            id=1,
            stream_url="http://stream.example.com/radio.mp3",  # HTTP, not HTTPS
            name="Insecure Radio",
            website_url="https://insecure.com",
            stream_type_id=1,
            is_secure=False,
        )
        mock_proposal_repo.find_by_id.return_value = proposal
        mock_radio_source_repo.find_by_url.return_value = None

        # Act
        result = validation_service.validate_proposal(1)

        # Assert
        assert result.is_valid  # Still valid, just a warning
        assert "This stream uses HTTP (not secure)" in result.warnings

    def test_validate_proposal_nonexistent_proposal(
        self,
        validation_service: ProposalValidationService,
        mock_proposal_repo: ProposalRepository,
    ):
        """Test validation fails for nonexistent proposal."""
        # Arrange
        mock_proposal_repo.find_by_id.return_value = None

        # Act
        result = validation_service.validate_proposal(999)

        # Assert
        assert not result.is_valid
        assert "Proposal with ID 999 not found" in result.errors

    def test_validate_url_format_valid_urls(
        self, validation_service: ProposalValidationService
    ):
        """Test URL format validation for valid URLs."""
        valid_urls = [
            "https://stream.example.com/radio.mp3",
            "http://stream.example.com:8000/stream.aac",
            "https://example.com/playlist.m3u8",
        ]

        for url in valid_urls:
            assert validation_service._is_valid_url(url), f"URL should be valid: {url}"

    def test_validate_url_format_invalid_urls(
        self, validation_service: ProposalValidationService
    ):
        """Test URL format validation for invalid URLs."""
        invalid_urls = ["not-a-url", "rtmp://stream.example.com/live", ""]

        for url in invalid_urls:
            assert not validation_service._is_valid_url(
                url
            ), f"URL should be invalid: {url}"

    def test_check_duplicate_stream_url_no_duplicate(
        self,
        validation_service: ProposalValidationService,
        mock_radio_source_repo: RadioSourceRepository,
    ):
        """Test duplicate check when no duplicate exists."""
        # Arrange
        mock_radio_source_repo.find_by_url.return_value = None

        # Act
        is_duplicate = validation_service.check_duplicate_stream_url(
            "https://stream.example.com/radio.mp3"
        )

        # Assert
        assert not is_duplicate

    def test_check_duplicate_stream_url_duplicate_exists(
        self,
        validation_service: ProposalValidationService,
        mock_radio_source_repo: RadioSourceRepository,
    ):
        """Test duplicate check when duplicate exists."""
        # Arrange
        mock_radio_source_repo.find_by_url.return_value = RadioSource(
            id=1,
            stream_url="https://stream.example.com/radio.mp3",
            name="Existing Radio",
            website_url="https://existing.com",
            stream_type_id=1,
            is_secure=True,
        )

        # Act
        is_duplicate = validation_service.check_duplicate_stream_url(
            "https://stream.example.com/radio.mp3"
        )

        # Assert
        assert is_duplicate
