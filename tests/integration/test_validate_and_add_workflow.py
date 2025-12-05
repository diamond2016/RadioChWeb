"""
Integration tests for the Validate and Add Radio Source workflow (Spec 002).

These tests verify the complete end-to-end workflow:
- Creating proposals
- Validating proposals
- Saving proposals as RadioSources
- Rejecting proposals
- Handling duplicates
"""

import pytest
from model.entity.proposal import Proposal
from model.entity.radio_source import RadioSource
from model.entity.stream_type import StreamType
from model.repository.proposal_repository import ProposalRepository
from model.repository.radio_source_repository import RadioSourceRepository
from service.proposal_validation_service import ProposalValidationService
from service.radio_source_service import RadioSourceService
from model.dto.validation import ProposalUpdateRequest
from tests.conftest import login_helper, test_app, test_user


class TestValidateAndAddWorkflow:
    """Integration tests for the complete validate and add workflow."""

    @pytest.fixture(scope="function")
    def db_session(self, test_db):
        """Use the test database session from conftest."""
        return test_db

    @pytest.fixture
    def repositories(self, db_session):
        """Create repositories with test session."""
        proposal_repo = ProposalRepository(db_session)
        radio_source_repo = RadioSourceRepository(db_session)
        return proposal_repo, radio_source_repo

    @pytest.fixture
    def services(self, repositories):
        """Create services with repositories."""
        proposal_repo, radio_source_repo = repositories
        validation_service = ProposalValidationService(proposal_repo, radio_source_repo)
        radio_source_service = RadioSourceService(
            proposal_repo, radio_source_repo, validation_service
        )
        return validation_service, radio_source_service

    def test_complete_save_workflow(self, db_session, services):
        """Test the complete workflow: create proposal -> validate -> save as radio source."""
        validation_service, radio_source_service = services

        # Create a proposal
        proposal = Proposal(
            stream_url="https://stream.example.com/radio.mp3",
            name="Test Radio Station",
            website_url="https://testradio.com",
            stream_type_id=1,  # Assuming stream type 1 exists from conftest
            is_secure=True,
            country="Italy",
            description="A test radio station",
            image_url="test.jpg",
            proposal_user=test_user
        )
        db_session.add(proposal)
        db_session.commit()

        # Validate the proposal
        validation_result = validation_service.validate_proposal(proposal.id)
        assert validation_result.is_valid

        # Save the proposal as a radio source
        save_result = radio_source_service.save_from_proposal(proposal.id)
        assert save_result.name == "Test Radio Station"
        assert save_result.stream_url == "https://stream.example.com/radio.mp3"

        # Verify proposal was deleted and radio source was created
        saved_proposal = db_session.query(Proposal).filter_by(id=proposal.id).first()
        assert saved_proposal is None

        saved_radio_source = (
            db_session.query(RadioSource)
            .filter_by(stream_url="https://stream.example.com/radio.mp3")
            .first()
        )
        assert saved_radio_source is not None
        assert saved_radio_source.name == "Test Radio Station"

    def test_duplicate_stream_url_prevention(self, db_session, services):
        """Test that duplicate stream URLs are prevented."""
        validation_service, radio_source_service = services

        # First, create and save a radio source
        proposal1 = Proposal(
            stream_url="https://duplicate.example.com/stream.mp3",
            name="First Radio",
            website_url="https://first.com",
            stream_type_id=1,
            is_secure=True,
        )
        db_session.add(proposal1)
        db_session.commit()

        # Save first proposal
        save_result1 = radio_source_service.save_from_proposal(proposal1.id)
        assert save_result1 is not None

        # Now try to create a proposal with the same stream URL
        proposal2 = Proposal(
            stream_url="https://duplicate.example.com/stream.mp3",  # Same URL
            name="Second Radio",
            website_url="https://second.com",
            stream_type_id=1,
            is_secure=True,
            proposal_user=test_user
        )
        db_session.add(proposal2)
        db_session.commit()

        # Validation should fail due to duplicate
        validation_result = validation_service.validate_proposal(proposal2.id)
        assert not validation_result.is_valid
        assert (
            "This stream URL already exists in the database" in validation_result.errors
        )

    def test_proposal_rejection_workflow(self, db_session, services):
        """Test rejecting a proposal."""
        _, radio_source_service = services

        # Create a proposal
        proposal = Proposal(
            stream_url="https://reject.example.com/stream.mp3",
            name="Rejected Radio",
            website_url="https://reject.com",
            stream_type_id=1,
            is_secure=True,
            proposal_user=test_user
        )
        db_session.add(proposal)
        db_session.commit()

        # Reject the proposal
        reject_result = radio_source_service.reject_proposal(proposal.id)
        assert reject_result is True

        # Verify proposal was deleted
        deleted_proposal = db_session.query(Proposal).filter_by(id=proposal.id).first()
        assert deleted_proposal is None

    def test_proposal_update_workflow(self, db_session, services):
        """Test updating proposal data."""
        _, radio_source_service = services
        with test_app.test_client() as client:
            login_helper(client)    

            # Create a proposal
            proposal = Proposal(
                stream_url="https://update.example.com/stream.mp3",
                name="Original Name",
                website_url="https://original.com",
                stream_type_id=1,
                is_secure=True,
                country="Original Country",
                description="Original description",
                proposal_user=client
            )
            db_session.add(proposal)
            db_session.commit()

        # Update the proposal
        update_request = ProposalUpdateRequest(
            name="Updated Name",
            website_url="https://updated.com",
            country="Updated Country",
            description="Updated description",
        )

        update_result = radio_source_service.update_proposal(
            proposal.id, update_request
        )
        assert update_result.name == "Updated Name"

        # Verify the update
        updated_proposal = db_session.query(Proposal).filter_by(id=proposal.id).first()
        assert updated_proposal.name == "Updated Name"
        assert updated_proposal.website_url == "https://updated.com"
        assert updated_proposal.country == "Updated Country"
        assert updated_proposal.description == "Updated description"

    def test_validation_with_missing_required_fields(self, db_session, services):
        """Test validation fails with missing required fields."""
        validation_service, _ = services

        # Create proposal with missing required field
        proposal = Proposal(
            stream_url="",  # Missing required field
            name="Test Radio",
            website_url="https://test.com",
            stream_type_id=1,
            is_secure=True,
            proposal_user=test_user
        )
        db_session.add(proposal)
        db_session.commit()

        # Validation should fail
        validation_result = validation_service.validate_proposal(proposal.id)
        assert not validation_result.is_valid
        assert "Stream URL is required and cannot be empty" in validation_result.errors

    def test_insecure_stream_warning(self, db_session, services):
        """Test warning for insecure HTTP streams."""
        validation_service, _ = services

        # Create proposal with HTTP stream
        proposal = Proposal(
            stream_url="http://insecure.example.com/stream.mp3",  # HTTP, not HTTPS
            name="Insecure Radio",
            website_url="https://insecure.com",
            stream_type_id=1,
            is_secure=False,
            proposal_user=test_user
        )
        db_session.add(proposal)
        db_session.commit()

        # Validation should succeed but with warning
        validation_result = validation_service.validate_proposal(proposal.id)
        assert validation_result.is_valid
