"""
Unit tests for RadioSourceService.

Moved from `tests/unit` into `tests/service` during test reorganization.
"""
import pytest
from unittest.mock import Mock
from datetime import datetime

from model.dto.radio_source import RadioSourceDTO
from model.dto.stream_type import StreamTypeDTO
from model.dto.user import UserDTO
from service.auth_service import AuthService
from service.stream_type_service import StreamTypeService

from model.repository.proposal_repository import ProposalRepository
from model.repository.radio_source_repository import RadioSourceRepository

from service.radio_source_service import RadioSourceService
from service.proposal_validation_service import ProposalValidationService

from model.entity.proposal import Proposal
from model.entity.radio_source import RadioSource
from model.entity.user import User

from model.dto.validation import ValidationResult



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
def mock_stream_type_service() -> StreamTypeService:
    """Create mock StreamTypeService."""
    return Mock(spec=StreamTypeService)

@pytest.fixture
def mock_stream_type_result() -> StreamTypeDTO:
    """Create mock StreamTypeService."""
    # return an actual StreamTypeDTO so nested fields are concrete values for Pydantic
    return StreamTypeDTO(id=1, name="MP3", description="MP3 Stream", protocol="HTTP", 
                         format="MP3", metadata_type="Icecast", display_name="HTTP MP3 Icecast")

@pytest.fixture
def mock_auth_service() -> AuthService:
    """Create mock AuthService."""
    return Mock(spec=AuthService)

@pytest.fixture
def radio_source_service(mock_proposal_repo: ProposalRepository,
                            mock_radio_source_repo: RadioSourceRepository, mock_validation_service: ProposalValidationService,
                            mock_auth_service: AuthService, mock_stream_type_service: StreamTypeService) -> RadioSourceService:
    """Create RadioSourceService with mocked dependencies."""
    return RadioSourceService(
        mock_proposal_repo,
        mock_radio_source_repo,
        mock_validation_service,
        mock_auth_service,
        mock_stream_type_service
    )


class TestRadioSourceService:
    """Test suite for RadioSourceService."""

    def test_save_from_proposal_success(
        self,
        radio_source_service: RadioSourceService,
        mock_proposal_repo: ProposalRepository,
        mock_radio_source_repo: RadioSourceRepository,
        mock_stream_type_service: StreamTypeService,
        mock_stream_type_result: StreamTypeDTO,
        mock_auth_service: AuthService,
        test_user: User
    ) -> None:
        """Test successfully saving a valid proposal as RadioSource."""

        # Arrange
        #stream_type_result = StreamTypeDTO(id=1, name="MP3", description="MP3 Stream", protocol="HTTP", 
        #                            format="MP3", metadata_type="Icecast", display_name="HTTP MP3 Icecast")
        proposal = Proposal(
            id=1,
            stream_url="https://stream.example.com/radio.mp3",
            name="Test Radio",
            website_url="https://example.com",
            stream_type_id=mock_stream_type_result.id,
            is_secure=True,
            country="Italy",
            description="Test description",
            image_url="test.jpg",
            created_by= test_user.id
        )

        mock_stream_type_service.get_stream_type.return_value = mock_stream_type_result
        user_result = UserDTO.model_validate(test_user)
        mock_auth_service.get_user_by_id.return_value = user_result
        mock_proposal_repo.find_by_id.return_value = proposal

        mock_radio_source_repo.save.return_value = RadioSource(
            id=1,
            stream_url="https://stream.example.com/radio.mp3",
            name="Test Radio",
            website_url="https://example.com",
            stream_type_id=mock_stream_type_result.id,
            is_secure=True,
            country="Italy",
            description="Test description",
            image_url="test.jpg",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=proposal.created_by
        )

        # Act
        result: RadioSourceDTO = radio_source_service.save_from_proposal(1)

        # Assert
        assert result.name == "Test Radio"
        assert result.stream_url == "https://stream.example.com/radio.mp3"
        assert result.website_url == "https://example.com"

        mock_radio_source_repo.save.assert_called_once()
        mock_proposal_repo.delete.assert_called_once_with(1)


    def test_save_from_proposal_not_found(
        self,
        radio_source_service,
        mock_proposal_repo,
    ) -> None:
        """Test saving fails when proposal not found."""
        # Arrange
        mock_proposal_repo.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Proposal with ID 1 not found"):
            radio_source_service.save_from_proposal(1)


    def test_reject_proposal_success(
        self,
        radio_source_service,
        mock_proposal_repo
    ) -> None:
        """Test successfully rejecting a proposal."""
        # Arrange
        proposal = Proposal(
            id=1,
            stream_url="https://stream.example.com/radio.mp3",
            name="Test Radio",
            website_url="https://example.com",
            stream_type_id=1,
            is_secure=True
        )
        mock_proposal_repo.find_by_id.return_value = proposal

        # Act
        result = radio_source_service.reject_proposal(1)

        # Assert
        assert result
        mock_proposal_repo.delete.assert_called_once_with(1)


    def test_reject_proposal_not_found(
        self,
        radio_source_service,
        mock_proposal_repo
    ) -> None:
        """Test rejecting fails when proposal not found."""
        # Arrange
        mock_proposal_repo.find_by_id.return_value = None

        # Act
        result = radio_source_service.reject_proposal(1)

        # Assert
        assert not result


    def test_get_all_radio_sources(
        self,
        radio_source_service: RadioSourceService,
        mock_radio_source_repo: RadioSourceRepository,
        mock_stream_type_service: StreamTypeService,
        test_user: User,
        mock_stream_type_result: StreamTypeDTO,
        mock_auth_service: AuthService
    ) -> None:
        """Test getting all radio sources."""
        # Arrange

        mock_stream_type_service.get_stream_type.return_value = mock_stream_type_result
        user_result = UserDTO.model_validate(test_user)
        mock_auth_service.get_user_by_id.return_value = user_result
        radio_sources: list[RadioSource] = [
            RadioSource(id=1, stream_url="url1", name="Radio 1", website_url="web1", stream_type_id=mock_stream_type_result.id, is_secure=True, created_by=test_user.id, created_at=datetime.now()),
            RadioSource(id=2, stream_url="url2", name="Radio 2", website_url="web2", stream_type_id=mock_stream_type_result.id, is_secure=False, created_by=test_user.id, created_at=datetime.now())
        ]
        mock_radio_source_repo.find_all.return_value = radio_sources

        # Act
        result: list[RadioSourceDTO] = radio_source_service.get_all_radio_sources()

        # Assert
        assert result is not None
        assert len(result) == 2
        assert all(isinstance(dto, RadioSourceDTO) for dto in result)
        assert result[0].name == "Radio 1"
        assert result[1].name == "Radio 2"
