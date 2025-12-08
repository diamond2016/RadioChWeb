"""
ProposalRepository - Data access layer for Proposal entities.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from model.dto.proposal import ProposalDTO
from model.repository.stream_type_repository import StreamTypeRepository
from model.repository.user_repository import UserRepository
from model.entity.proposal import Proposal


class ProposalRepository:
    """Repository for Proposal data access operations."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.stream_type_repo = StreamTypeRepository(db_session)
        self.user_repo = UserRepository(db_session)
    
    def find_by_id(self, proposal_id: int) -> Optional[Proposal]:
        """Get Proposal by ID."""
        return self.db.query(Proposal).filter(Proposal.id == proposal_id).first()
    
    def find_by_url(self, url: str) -> Optional[Proposal]:
        """Get Proposal by URL."""
        return self.db.query(Proposal).filter(Proposal.stream_url == url).first()
    
    def find_all(self) -> List[Proposal]:
        """Get all Proposals."""
        return self.db.query(Proposal).all()
    
    def save(self, proposal: Proposal) -> Proposal:
        """Save (create or update) a Proposal."""
        if proposal.id is None:
            self.db.add(proposal)
        self.db.commit()
        self.db.refresh(proposal)
        return proposal
    
    def update(self, proposal: Proposal) -> Proposal:
        """Save (create or update) a Proposal."""
        if proposal.id is not None:
            self.db.add(proposal)
        self.db.commit()
        self.db.refresh(proposal)
        return proposal
    
    def delete(self, proposal_id: int) -> bool:
        """Delete a Proposal by ID."""
        proposal = self.find_by_id(proposal_id)
        if proposal:
            self.db.delete(proposal)
            self.db.commit()
            return True
        return False
    
    def count(self) -> int:
        """Count total Proposals."""
        return self.db.query(Proposal).count()
    
    def exists_by_stream_url(self, stream_url: str) -> bool:
        """Check if a Proposal with the given stream URL already exists."""
        return self.db.query(Proposal).filter(Proposal.stream_url == stream_url).first() is not None
    
    def get_all_proposals(self) -> List[Proposal]:
        """Retrieve all proposals from the database."""
        return self.db.query(Proposal).all()
    
    def get_proposals_by_user(self, user_id: int) -> List[Proposal]:
        """Retrieve all proposals submitted by a specific user."""
        return self.db.query(Proposal).filter(Proposal.created_by == user_id).all()
    