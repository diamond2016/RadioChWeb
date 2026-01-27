"""
Unit tests for StreamTypeService.

Moved from `tests/unit` into `tests/service` during test reorganization.
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path
from typing import List
# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
print(sys.path)
from model.entity.stream_type import StreamType
from model.repository.stream_type_repository import StreamTypeRepository
from model.entity.stream_analysis import StreamAnalysis
from service.stream_type_service import StreamTypeService
from model.dto.stream_type import StreamTypeDTO

@pytest.fixture
def mock_repository() -> StreamTypeRepository:
    """Mock StreamTypeRepository for testing."""
    return Mock()

@pytest.fixture
def stream_type_service(mock_repository: StreamTypeRepository) -> StreamTypeService:
    """Create StreamTypeService with mocked repository."""
    return StreamTypeService(mock_repository)


class TestStreamTypeService:
    """Test cases for StreamTypeService."""

    def test_find_stream_type_id(self, stream_type_service: StreamTypeService, mock_repository: StreamTypeRepository):
        """Test finding stream type ID by combination."""
        mock_repository.find_by_combination.return_value = 5

        result = stream_type_service.find_stream_type_id("HTTPS", "MP3", "Icecast")

        assert result == 5
        mock_repository.find_by_combination.assert_called_once_with("HTTPS", "MP3", "Icecast")

    def test_find_stream_type_id_not_found(self, stream_type_service: StreamTypeService, mock_repository: StreamTypeRepository):
        """Test finding stream type ID when not found."""
        mock_repository.find_by_combination.return_value = None

        result = stream_type_service.find_stream_type_id("UNKNOWN", "FORMAT", "META")

        assert result is None

    def test_get_stream_type(self, stream_type_service: StreamTypeService, mock_repository: StreamTypeRepository):
        """Test getting stream type by ID."""
        # Mock the entity returned by repository
        mock_entity = Mock()
        mock_entity.id = 1
        mock_entity.protocol = "HTTPS"
        mock_entity.format = "MP3"
        mock_entity.metadata_type = "Icecast"
        mock_entity.display_name = "HTTPS MP3 Icecast"
        mock_repository.find_by_id.return_value = mock_entity

        result: StreamTypeDTO | None = stream_type_service.get_stream_type(1)

        assert isinstance(result, StreamTypeDTO)
        assert result.id == 1
        assert result.protocol == "HTTPS"
        assert result.format == "MP3"
        assert result.metadata_type == "Icecast"
        assert result.display_name == "HTTPS MP3 Icecast"

    def test_get_stream_type_not_found(self, stream_type_service: StreamTypeService, mock_repository: StreamTypeRepository):
        """Test getting stream type when not found."""
        mock_repository.find_by_id.return_value = None

        result: StreamTypeDTO | None = stream_type_service.get_stream_type(999)

        assert result is None

    def test_get_all_stream_types(self, stream_type_service: StreamTypeService, mock_repository: StreamTypeRepository):
        """Test getting all stream types."""
        # Mock entities
        mock_entities: list[StreamType] = [
            StreamType(id=1, protocol="HTTP", format="MP3", metadata_type="Icecast", display_name="HTTP MP3 Icecast"),
            StreamType(id=2, protocol="HTTPS", format="AAC", metadata_type="Shoutcast", display_name="HTTPS AAC Shoutcast")
        ]
        mock_repository.find_all.return_value = mock_entities

        result: List[StreamTypeDTO] = stream_type_service.get_all_stream_types()

        assert len(result) == 2
        assert all(isinstance(dto, StreamTypeDTO) for dto in result)
        assert result[0].protocol == "HTTP"
        assert result[1].protocol == "HTTPS"

    def test_get_predefined_types_map(self, stream_type_service: StreamTypeService, mock_repository: StreamTypeRepository):
        """Test getting predefined types map."""
        mock_repository.get_type_key_to_id_map.return_value = {
            "HTTP-MP3-Icecast": 1,
            "HTTPS-AAC-Shoutcast": 2
        }

        result = stream_type_service.get_predefined_types_map()

        assert result == {"HTTP-MP3-Icecast": 1, "HTTPS-AAC-Shoutcast": 2}
        mock_repository.get_type_key_to_id_map.assert_called_once()

    def test_initialize_predefined_types(self, stream_type_service: StreamTypeService, mock_repository: StreamTypeRepository):
        """Test initializing predefined types."""
        stream_type_service.initialize_predefined_types()

        # Should call create_if_not_exists for each predefined type
        assert mock_repository.create_if_not_exists.call_count == 14

        # Check one of the calls
        calls = mock_repository.create_if_not_exists.call_args_list
        assert any(call[0] == ("HTTP", "MP3", "Icecast", "HTTP MP3 with Icecast metadata") for call in calls)
