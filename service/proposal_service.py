"""
ProposalService - business logic for updating Proposal entities.

Provides an isolated service for proposal-specific operations such as
updating user-editable fields. This keeps proposal domain logic
separate from the RadioSource service.
"""

from typing import Optional
from flask_login import login_required
from model.entity.proposal import Proposal
from model.repository.proposal_repository import ProposalRepository
from model.dto.proposal import ProposalDTO, ProposalUpdateRequest


class ProposalService:
    def __init__(self, proposal_repo: ProposalRepository):
        self.proposal_repo = proposal_repo

    # a user can propose from analyze stream an can update proposals if is their own
    @login_required
    def update_proposal(self, proposal_id: int, updates: ProposalUpdateRequest) -> Proposal:
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

        return self.proposal_repo.save(proposal)
    

    def get_proposal(self, proposal_id: int) -> Optional[ProposalDTO]:
        """
        Get a proposal by ID.
        
        Args:
            proposal_id: ID of the proposal
            
        Returns:
            Proposal if found, None otherwise
        """
        return self.proposal_repo.find_by_id(proposal_id)
    

    def get_all_proposals(self) -> list[ProposalDTO]:
        """
        Get all proposals.
        
        Returns:
            List of all proposals
        """

        proposals = self.proposal_repo.get_all_proposals()
        for proposal in proposals:
            
            proposal.stream_type  # ensure stream_type is loaded
            proposal.created_by   # ensure created_by is loaded 
        return proposals
    


    # only admin can disapprove a proposal as can approve
    @admin_required
    def reject_proposal(self, proposal_id: int) -> bool:
        """
        Reject (delete) a proposal by id.

        Returns True if deletion succeeded, False otherwise.
        This method is defensive about repository method names to preserve backward compatibility.
        """
        try:
            # preferred repo API
            if hasattr(self.proposal_repo, "delete_by_id"):
                return bool(self.proposal_repo.delete_by_id(proposal_id))

            # alternate common name
            if hasattr(self.proposal_repo, "delete"):
                return bool(self.proposal_repo.delete(proposal_id))

            # fallback: load entity and try repository delete_entity or session
            finder = getattr(self.proposal_repo, "find_by_id", None)
            if callable(finder):
                prop: Proposal = finder(proposal_id)
                if prop is None:
                    return False
                if hasattr(self.proposal_repo, "delete_entity"):
                    return bool(self.proposal_repo.delete_entity(prop))
                session = getattr(self.proposal_repo, "session", None)
                if session is not None:
                    session.delete(prop)
                    session.commit()
                    return True

            # no supported API found
            return False
        except Exception:
            return False