"""
RadioSourceService - Business logic for managing radio sources and proposals.

This service handles the workflow of converting validated proposals into
RadioSourceNodes, including validation, duplicate checking, and proper
transaction handling.
"""

from datetime import datetime
from typing import List

from flask_login import login_required
from model.dto.radio_source import RadioSourceDTO
from model.dto.validation import ValidationResult
from model.entity.proposal import Proposal
from model.repository.proposal_repository import ProposalRepository
from model.repository.radio_source_repository import RadioSourceRepository
from service.auth_service import admin_required
from service.proposal_validation_service import ProposalValidationService
from model.entity.radio_source import RadioSource


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
    
    # admin can transfor a proposal in radio source
    @admin_required
    def save_from_proposal(self, proposal_id: int) -> RadioSourceDTO:
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
            as a RadioSourceDTO
        Raises:
            ValueError: If validation fails or proposal not found
            RuntimeError: If database operation fails
        """
        # Validate proposal
        validation_result: ValidationResult = self.validation_service.validate_proposal(proposal_id)
        if not validation_result.is_valid:
            error_msg = "; ".join(validation_result.errors)
            raise ValueError(f"Proposal validation failed: {error_msg}")
        
        # Get proposal
        proposal: Proposal | None = self.proposal_repo.find_by_id(proposal_id)
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
            image_url=proposal.image_url,
            created_at=datetime.now()
        )
     
        try:
            # Save RadioSourceNode (this will commit the transaction)
            saved_source: RadioSource = self.radio_source_repo.save(radio_source)
            
            # Delete proposal after successful save
            self.proposal_repo.delete(proposal_id)
            
            return RadioSourceDTO.model_validate(saved_source)
            
        except Exception as e:
            raise RuntimeError(f"Failed to save radio source: {str(e)}")


    def get_all_radio_sources(self) -> list[RadioSourceDTO]:
        """
        Get all radio sources.
        Returns:
            List of all radio sources
        """
        radio_sources: List[RadioSource] = self.radio_source_repo.find_all()
        radio_source_dtos: List[RadioSourceDTO] = []
        for radio_source in radio_sources:
            new_radio_source: RadioSourceDTO = RadioSourceDTO.model_validate(radio_source)
            radio_source_dtos.append(new_radio_source)
        return radio_source_dtos   


    def get_radio_source_by_id(self, id) -> RadioSourceDTO | None:
        """ get a radio source by id"""
        radio_source: RadioSource | None = self.radio_source_repo.find_by_id(id)
        if radio_source:
            return RadioSourceDTO.model_validate(radio_source)
        return None
    
    # only admin can edit a radio source
    @admin_required
    def update_radio_source(self, radio_source_dto: RadioSourceDTO) -> RadioSourceDTO:
        """ update a radio source"""
        radio_source: RadioSource | None = self.radio_source_repo.find_by_id(radio_source_dto.id)
        if not radio_source:
            raise ValueError(f"Radio source with ID {radio_source_dto.id} not found")
        
        # Update fields
        radio_source.name = radio_source_dto.name
        radio_source.stream_url = radio_source_dto.stream_url
        radio_source.description = radio_source_dto.description
        radio_source.stream_type_id = radio_source_dto.stream_type_id
        
        # Save updated radio source
        updated_radio_source: RadioSource = self.radio_source_repo.save(radio_source)
        return RadioSourceDTO.model_validate(updated_radio_source)
    
    # only admin can delete a radio source
    @admin_required
    def delete_radio_source(self, id) -> bool:
        """ delete a radio source"""
        if id:
            return self.radio_source_repo.delete(id)
        return False
    

