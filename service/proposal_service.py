"""
ProposalService - business logic for updating Proposal entities.

Provides an isolated service for proposal-specific operations such as
updating user-editable fields. This keeps proposal domain logic
separate from the RadioSource service.
"""

from model.repository.proposal_repository import ProposalRepository
from model.dto.validation import ProposalUpdateRequest
from model.entity.proposal import Proposal


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

        # DTO field is 'image' but entity stores 'image_url'
        if updates.image is not None:
            proposal.image_url = updates.image

        return self.proposal_repo.save(proposal)
