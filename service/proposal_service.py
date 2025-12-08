"""
ProposalService - business logic for updating Proposal entities.

Provides an isolated service for proposal-specific operations such as
updating user-editable fields. This keeps proposal domain logic
separate from the RadioSource service.
"""

from typing import List, Optional
from flask_login import login_required
from model.entity import proposal
from service.auth_service import admin_required
from model.entity.proposal import Proposal
from model.repository.proposal_repository import ProposalRepository
from model.dto.proposal import ProposalDTO, ProposalUpdateRequest


class ProposalService:
    def __init__(self, proposal_repo: ProposalRepository):
        self.proposal_repo: ProposalRepository = proposal_repo

    # a user can propose from analyze stream an can update proposals if is their own
    @login_required
    def update_proposal(self, proposal_id: int, updates: ProposalUpdateRequest) -> ProposalDTO:
        """Update editable fields of a proposal and persist changes.

        Editable fields: name, website_url, country, description, image (mapped to image_url)
        """
        proposal = self.proposal_repo.find_by_id(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal with ID {proposal_id} not found")

        if not updates.has_updates():
            raise ValueError("No updates provided")

        if updates.name is not None:
            proposal.name = updates.name

        if updates.website_url is not None:
            proposal.website_url = updates.website_url

        if updates.country is not None:
            proposal.country = updates.country

        if updates.description is not None:
            proposal.description = updates.description

        if updates.image_url is not None:
            proposal.image_url = updates.image_url

        result: proposal = self.proposal_repo.update(proposal)
        if result is None:
            return None
        return self.proposal_repo.to_dto(result.id)
    

    def get_proposal(self, proposal_id: int) -> Optional[ProposalDTO]:
        """
        Get a proposal by ID.
        
        Args:
            proposal_id: ID of the proposal
            
        Returns:
            Proposal if found, None otherwise
        """
        result: proposal = self.proposal_repo.find_by_id(proposal_id)
        if result is None:
            return None
        return self.proposal_repo.to_dto(result.id)
    

    def get_all_proposals(self) -> list[ProposalDTO]:
        """
        Get all proposals.
        
        Returns:
            List of all proposals
        """

        proposals: List[Proposal] = self.proposal_repo.get_all_proposals()
        proposal_dtos: List[ProposalDTO] = []
        for proposal in proposals:
            new_proposal: ProposalDTO = self.proposal_repo.to_dto(proposal.id)
            proposal_dtos.append(new_proposal)
        return proposal_dtos   


    # only admin can disapprove a proposal as can approve. If rejected is deleted
    @admin_required
    def reject_proposal(self, proposal_id: int) -> bool:
        """
        Reject (delete) a proposal by id.

        Returns True if deletion succeeded, False otherwise.
        This method is defensive about repository method names to preserve backward compatibility.
        """
        try:
            proposal: Proposal = self.proposal_repo.find_by_id(proposal_id)
            if proposal is None:
                return False
            self.proposal_repo.delete(proposal_id)
            return True
        
        except AttributeError:  
            return False
