"""
ProposalService - business logic for updating Proposal entities.

Provides an isolated service for proposal-specific operations such as
updating user-editable fields. This keeps proposal domain logic
separate from the RadioSource service.
"""

from typing import List, Optional
from model.entity import proposal
from model.entity.proposal import Proposal
from model.repository.proposal_repository import ProposalRepository
from model.dto.proposal import ProposalDTO


class ProposalService:
    def __init__(self, proposal_repo: ProposalRepository):
        self.proposal_repo: ProposalRepository = proposal_repo

    # a user can propose from analyze stream an can update proposals if is their own
    def update_proposal(self, proposal_id: int, updates: ProposalDTO) -> ProposalDTO | None:
        """Update editable fields of a proposal and persist changes.

        Non Editable fields: id, stream_url, stream_type_id, is_secure 
        """
        proposal = self.proposal_repo.find_by_id(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal with ID {proposal_id} not found")

        if not updates:
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

        result: Proposal | None = self.proposal_repo.update(proposal)
        if result is None:
            return None
        return ProposalDTO.model_validate(result)
    

    def get_proposal(self, proposal_id: int) -> Optional[ProposalDTO]:
        """
        Get a proposal by ID.
        
        Args:
            proposal_id: ID of the proposal
            
        Returns:
            Proposal if found, None otherwise
        """
        result: Proposal | None = self.proposal_repo.find_by_id(proposal_id)
        if result is None:
            return None
        
        return ProposalDTO.model_validate(result)
    

    def get_all_proposals(self) -> list[ProposalDTO]:
        """
        Get all proposals.
        
        Returns:
            List of all proposals
        """

        proposals: List[Proposal] = self.proposal_repo.get_all_proposals()
        proposal_dtos: List[ProposalDTO] = []
        for proposal in proposals:
            new_proposal: ProposalDTO = ProposalDTO.model_validate(proposal)
            proposal_dtos.append(new_proposal)
        return proposal_dtos   

    def reject_proposal(self, proposal_id: int) -> bool:
        """
        Reject (delete) a proposal by its ID.

        Returns True when the proposal existed and was deleted, False otherwise.
        """
        if proposal_id is None:
            raise ValueError("proposal_id must be provided")

        deleted: bool = self.proposal_repo.delete(proposal_id)
        return deleted


