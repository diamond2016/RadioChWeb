"""
Unit tests for RadioSourceService.

Tests radio source management including:
- Saving proposals as RadioSources
- Rejecting proposals
- Updating proposal data
- Transaction handling
"""

import pytest
from unittest.mock import Mock
from model.repository.proposal_repository import ProposalRepository
from model.repository.radio_source_repository import RadioSourceRepository
from service.radio_source_service import RadioSourceService
from service.proposal_validation_service import ProposalValidationService
from model.entity.proposal import Proposal
from model.entity.radio_source import RadioSource


from model.dto.validation import ProposalUpdateRequest
from model.dto.validation import ValidationResult
from datetime import datetime


@pytest.fixture
def mock_proposal_repo() -> ProposalRepository:
    """Create mock ProposalRepository."""
    return Mock(spec=ProposalRepository)


@pytest.fixture
def mock_radio_source_repo() -> RadioSourceRepository:
    """Create mock RadioSourceRepository."""
    return Mock(spec=RadioSourceRepository)


@pytest.fixture
def mock_validation_service() -> ProposalValidationService:
    """Create mock ProposalValidationService."""
    return Mock(spec=ProposalValidationService)


@pytest.fixture
def radio_source_service(
    mock_proposal_repo: ProposalRepository,
    mock_radio_source_repo: RadioSourceRepository,
    mock_validation_service: ProposalValidationService,
) -> RadioSourceService:
    """Create RadioSourceService with mocked dependencies."""
    return RadioSourceService(
        mock_proposal_repo, mock_radio_source_repo, mock_validation_service
    )


class TestRadioSourceService:
    """Test suite for RadioSourceService."""

    def test_save_from_proposal_success(
        self,
        radio_source_service,
        mock_proposal_repo,
        mock_radio_source_repo,
        mock_validation_service,
    ):
        """Test successfully saving a valid proposal as RadioSource."""

        # Arrange
        proposal = Proposal(
            id=1,
            stream_url="https://stream.example.com/radio.mp3",
            name="Test Radio",
            website_url="https://example.com",
            stream_type_id=1,
            is_secure=True,
            country="Italy",
            description="Test description",
            image_url="test.jpg",
        )

        validation_result = ValidationResult(is_valid=True)
        mock_validation_service.validate_proposal.return_value = validation_result
        mock_proposal_repo.find_by_id.return_value = proposal

        mock_radio_source_repo.save.return_value = RadioSource(
            id=1,
            stream_url="https://stream.example.com/radio.mp3",
            name="Test Radio",
            website_url="https://example.com",
            stream_type_id=1,
            is_secure=True,
            country="Italy",
            description="Test description",
            image_url="test.jpg",
            created_at=datetime.now(),
        )

        # Act
        result = radio_source_service.save_from_proposal(1)

        # Assert
        assert result.name == "Test Radio"
        assert result.stream_url == "https://stream.example.com/radio.mp3"
        assert result.website_url == "https://example.com"
        mock_validation_service.validate_proposal.assert_called_once_with(1)
        mock_radio_source_repo.save.assert_called_once()
        mock_proposal_repo.delete.assert_called_once_with(1)


    def test_save_from_proposal_validation_failure(
        self, radio_source_service, mock_validation_service
    ):
        """Test saving fails when validation fails."""
        # Arrange
        validation_result = ValidationResult(
            is_valid=False, errors=["Stream URL is required"]
        )
        mock_validation_service.validate_proposal.return_value = validation_result

        # Act & Assert
        with pytest.raises(
            ValueError, match="Proposal validation failed: Stream URL is required"
        ):
            radio_source_service.save_from_proposal(1)


    def test_save_from_proposal_not_found(
        self, radio_source_service, mock_proposal_repo, mock_validation_service
    ):
        """Test saving fails when proposal not found."""
        # Arrange
        validation_result = ValidationResult(is_valid=True)
        mock_validation_service.validate_proposal.return_value = validation_result
        mock_proposal_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Proposal with ID 1 not found"):
            radio_source_service.save_from_proposal(1)


    def test_reject_proposal_success(self, radio_source_service, mock_proposal_repo):
        """Test successfully rejecting a proposal."""
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

        # Act
        result = radio_source_service.reject_proposal(1)

        # Assert
        assert result
        mock_proposal_repo.delete.assert_called_once_with(1)


    def test_reject_proposal_not_found(self, radio_source_service, mock_proposal_repo):
        """Test rejecting fails when proposal not found."""
        # Arrange
        mock_proposal_repo.find_by_id.return_value = None

        # Act
        result = radio_source_service.reject_proposal(1)

        # Assert
        assert not result


    def test_update_proposal_success(self, radio_source_service, mock_proposal_repo):
        """Test successfully updating proposal data."""
        # Arrange
        update_request = ProposalUpdateRequest(
            name="Updated Radio Name",
            website_url="https://updated.example.com",
            country="Updated Country",
            description="Updated description",
        )

        proposal = Proposal(
            id=1,
            stream_url="https://stream.example.com/radio.mp3",
            name="Original Name",
            website_url="https://original.example.com",
            stream_type_id=1,
            is_secure=True,
            country="Original Country",
            description="Original description",
        )
        mock_proposal_repo.find_by_id.return_value = proposal

        updated_proposal = Proposal(
            id=1,
            stream_url="https://stream.example.com/radio.mp3",
            name="Updated Radio Name",
            website_url="https://updated.example.com",
            stream_type_id=1,
            is_secure=True,
            country="Updated Country",
            description="Updated description",
        )
        mock_proposal_repo.save.return_value = updated_proposal

        # Act
        result = radio_source_service.update_proposal(1, update_request)

        # Assert
        assert result.name == "Updated Radio Name"
        assert result.website_url == "https://updated.example.com"
        assert result.country == "Updated Country"
        assert result.description == "Updated description"

    def test_update_proposal_not_found(self, radio_source_service, mock_proposal_repo):
        """Test updating fails when proposal not found."""
        # Arrange
        update_request = ProposalUpdateRequest(name="New Name")
        mock_proposal_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Proposal with ID 1 not found"):
            radio_source_service.update_proposal(1, update_request)

    def test_get_proposal(self, radio_source_service, mock_proposal_repo):
        """Test getting a proposal by ID."""
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

        # Act
        result = radio_source_service.get_proposal(1)

        # Assert
        assert result == proposal

    def test_get_all_proposals(self, radio_source_service, mock_proposal_repo):
        """Test getting all proposals."""
        # Arrange
        proposals = [
            Proposal(
                id=1,
                stream_url="url1",
                name="Radio 1",
                website_url="web1",
                stream_type_id=1,
                is_secure=True,
            ),
            Proposal(
                id=2,
                stream_url="url2",
                name="Radio 2",
                website_url="web2",
                stream_type_id=2,
                is_secure=False,
            ),
        ]
        mock_proposal_repo.get_all_proposals.return_value = proposals

        # Act
        result = radio_source_service.get_all_proposals()

        # Assert
        assert result == proposals


    def test_reject_proposal_not_found(self, radio_source_service, mock_proposal_repo):
        """Test rejecting a proposal that doesn't exist."""
        # Arrange
        mock_proposal_repo.delete.return_value = False

        # Act
        result = radio_source_service.reject_proposal(1)

        # Assert
        assert result is False
        mock_proposal_repo.delete.assert_called_once_with(1)

    def test_get_all_radio_sources(self, radio_source_service, mock_radio_source_repo):
        """Test getting all radio sources."""
        # Arrange
        radio_sources = [
            RadioSource(
                id=1,
                stream_url="url1",
                name="Radio 1",
                website_url="web1",
                stream_type_id=1,
                is_secure=True,
                created_at=datetime.now(),
            ),
            RadioSource(
                id=2,
                stream_url="url2",
                name="Radio 2",
                website_url="web2",
                stream_type_id=2,
                is_secure=False,
                created_at=datetime.now(),
            ),
        ]
        mock_radio_source_repo.find_all.return_value = radio_sources

        # Act
        result = radio_source_service.get_all_radio_sources()

        # Assert
        assert result == radio_sources
