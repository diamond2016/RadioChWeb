"""
RadioSourceService - Business logic for managing radio sources and proposals.

This service handles the workflow of converting validated proposals into
RadioSourceNodes, including validation, duplicate checking, and proper
transaction handling.
"""

from datetime import datetime
from typing import Optional
from model.repository.proposal_repository import ProposalRepository
from model.repository.radio_source_repository import RadioSourceRepository
from service.proposal_validation_service import ProposalValidationService
from model.entity.radio_source import RadioSource
from model.entity.proposal import Proposal
from model.dto.validation import ProposalUpdateRequest, ValidationResult


class RadioSourceService:
    """
    Service for managing RadioSourceNodes and their lifecycle.
    
    Handles:
    - Saving proposals as RadioSourceNodes
    - Rejecting proposals
    - Updating proposal data
    """
    
    def __init__(
        self,
        proposal_repo: ProposalRepository,
        radio_source_repo: RadioSourceRepository,
        validation_service: ProposalValidationService
    ):
        self.proposal_repo = proposal_repo
        self.radio_source_repo = radio_source_repo
        self.validation_service = validation_service
    
    def save_from_proposal(self, proposal_id: int) -> RadioSource:
        """
        Save a proposal as a RadioSourceNode in the database.
        
        This method:
        1. Validates the proposal
        2. Creates a RadioSourceNode from proposal data
        3. Saves to database
        4. Deletes the proposal (single transaction)
        
        Args:
            proposal_id: ID of the proposal to save
            
        Returns:
            The saved RadioSourceNode
            
        Raises:
            ValueError: If validation fails or proposal not found
            RuntimeError: If database operation fails
        """
        # Validate proposal
        validation_result = self.validation_service.validate_proposal(proposal_id)
        if not validation_result.is_valid:
            error_msg = "; ".join(validation_result.errors)
            raise ValueError(f"Proposal validation failed: {error_msg}")
        
        # Get proposal
        proposal = self.proposal_repo.find_by_id(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal with ID {proposal_id} not found")
        
        # Create RadioSourceNode from proposal
        radio_source = RadioSource(
            stream_url=proposal.stream_url,
            name=proposal.name,
            website_url=proposal.website_url,
            stream_type_id=proposal.stream_type_id,
            is_secure=proposal.is_secure,
            country=proposal.country,
            description=proposal.description,
            image_url=proposal.image_url
        )
        
        try:
            # Save RadioSourceNode (this will commit the transaction)
            saved_source = self.radio_source_repo.save(radio_source)
            
            # Delete proposal after successful save
            self.proposal_repo.delete(proposal_id)
            
            return saved_source
            
        except Exception as e:
            raise RuntimeError(f"Failed to save radio source: {str(e)}")
    
    def reject_proposal(self, proposal_id: int) -> bool:
        """
        Reject and delete a proposal.
        
        Args:
            proposal_id: ID of the proposal to reject
            
        Returns:
            True if successfully deleted, False if proposal not found
        """
        return self.proposal_repo.delete(proposal_id)
    
    def update_proposal(self, proposal_id: int, updates: ProposalUpdateRequest) -> Proposal:
        """
        Update user-editable fields of a proposal.
        
        Only allows updating: name, website_url, country, description, image
        Read-only fields (stream_type_id, is_secure) cannot be modified.
        
        Args:
            proposal_id: ID of the proposal to update
            updates: ProposalUpdateRequest with fields to update
            
        Returns:
            Updated Proposal
            
        Raises:
            ValueError: If proposal not found or no updates provided
        """
        # Get proposal
        proposal = self.proposal_repo.find_by_id(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal with ID {proposal_id} not found")
        
        # Check if any updates provided
        if not updates.has_updates():
            raise ValueError("No updates provided")
        
        # Update only user-editable fields
        if updates.name is not None:
            proposal.name = updates.name
        
        if updates.website_url is not None:
            proposal.website_url = updates.website_url
        
        if updates.country is not None:
            proposal.country = updates.country
        
        if updates.description is not None:
            proposal.description = updates.description
        
        if updates.image is not None:
            proposal.image = updates.image
        
        # Save and return updated proposal
        return self.proposal_repo.save(proposal)
    
    def get_proposal(self, proposal_id: int) -> Optional[Proposal]:
        """
        Get a proposal by ID.
        
        Args:
            proposal_id: ID of the proposal
            
        Returns:
            Proposal if found, None otherwise
        """
        return self.proposal_repo.find_by_id(proposal_id)
    
    def get_all_proposals(self) -> list[Proposal]:
        """
        Get all proposals.
        
        Returns:
            List of all proposals
        """
        return self.proposal_repo.get_all()
    
    def get_all_radio_sources(self) -> list[RadioSource]:
        """
        Get all radio sources.
        
        Returns:
            List of all radio sources
        """
        return self.radio_source_repo.get_all()
