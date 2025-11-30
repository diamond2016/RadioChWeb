"""
ProposalRepository - Data access layer for Proposal entities.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from model.entity.proposal import Proposal


class ProposalRepository:
    """Repository for Proposal data access operations."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def find_by_id(self, proposal_id: int) -> Optional[Proposal]:
        """Get Proposal by ID."""
        return self.db.query(Proposal).filter(Proposal.id == proposal_id).first()
    
    def find_by_url(self, url: str) -> Optional[Proposal]:
        """Get Proposal by URL."""
        return self.db.query(Proposal).filter(Proposal.url == url).first()
    
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