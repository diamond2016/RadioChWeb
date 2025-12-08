"""
ProposalValidationService - Business logic for validating proposals.

This service implements validation rules for proposals before they are saved
as RadioSourceNodes, including duplicate detection and security checks.
"""

from typing import Optional
from urllib.parse import urlparse
from model.entity.proposal import Proposal
from model.repository.proposal_repository import ProposalRepository
from model.repository.radio_source_repository import RadioSourceRepository
from model.dto.validation import ValidationResult, SecurityStatus


class ProposalValidationService:
    """
    Service for validating proposals before saving to RadioSourceNode.
    
    Validates:
    - Required fields presence
    - URL format validity
    - Duplicate stream URLs
    - Security status
    """
    
    def __init__(
        self, 
        proposal_repo: ProposalRepository,
        radio_source_repo: RadioSourceRepository
    ):
        self.proposal_repo: ProposalRepository = proposal_repo
        self.radio_source_repo: RadioSourceRepository = radio_source_repo
    
    def validate_proposal(self, proposal_id: int) -> ValidationResult:
        """
        Validate a proposal before saving to RadioSourceNode.
        
        Checks:
        - Proposal exists
        - Required fields are present and non-empty
        - URLs are valid format
        - Stream URL is not duplicate
        
        Args:
            proposal_id: ID of the proposal to validate
            
        Returns:
            ValidationResult with is_valid flag and error/warning messages
        """
        result = ValidationResult(is_valid=True)
        
        # Check proposal exists
        proposal: Proposal | None = self.proposal_repo.find_by_id(proposal_id)
        if not proposal:
            result.add_error(f"Proposal with ID {proposal_id} not found")
            return result
        
        # Validate required fields (FR-006)
        if not str(proposal.stream_url) or not str(proposal.stream_url).strip():
            result.add_error("Stream URL is required and cannot be empty")
        
        if not str(proposal.name) or not str(proposal.name).strip():
            result.add_error("Name is required and cannot be empty")
        
        if not str(proposal.website_url) or not str(proposal.website_url).strip():
            result.add_error("Website URL is required and cannot be empty")

        # Ensure stream type is present: RadioSourceNode requires a stream_type_id
        # Proposals created from discovery (spec 001) may not have this yet; they
        # must be classified (spec 003) before being saved to the radio sources table.
        if proposal.stream_type_id is None:
            result.add_error("Stream type is required. Please classify the stream before saving.")
        
        # Validate URL formats
        if str(proposal.stream_url):
            if not self._is_valid_url(str(proposal.stream_url)):
                result.add_error(f"Invalid stream URL format: {proposal.stream_url}")
        
        if str(proposal.website_url):
            if not self._is_valid_url(str(proposal.website_url)):
                result.add_error(f"Invalid website URL format: {proposal.website_url}")
        
        # Check for duplicate stream URL (FR-005)
        if str(proposal.stream_url) and self.check_duplicate_stream_url(str(proposal.stream_url)):
            result.add_error("This stream URL already exists in the database")
        
        # Add security warning if HTTP stream
        if str(proposal.stream_url) and not bool(proposal.is_secure):
            result.add_warning("This stream uses HTTP (not secure)")
        
        return result
    

    def check_duplicate_stream_url(self, stream_url: str) -> bool:
        """
        Check if a stream URL already exists in RadioSourceNode table.
        
        Args:
            stream_url: The stream URL to check
            
        Returns:
            True if duplicate found, False otherwise
        """
        return self.radio_source_repo.find_by_url(stream_url) is not None
    

    def get_security_status(self, proposal_id: int) -> Optional[SecurityStatus]:
        """
        Get the security status of a proposal.
        
        Args:
            proposal_id: ID of the proposal
            
        Returns:
            SecurityStatus object with is_secure flag and warning message,
            or None if proposal not found
        """
        proposal: Proposal | None = self.proposal_repo.find_by_id(proposal_id)
        if not proposal:
            return None
        
        if not proposal.is_secure:
            return SecurityStatus(is_secure=False, warning_message="This stream uses HTTP (not secure)")
        return SecurityStatus(is_secure=True, warning_message=None)

    
    def _is_valid_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL string to validate
            
        Returns:
            True if URL has valid format, False otherwise
        """
        try:
            parsed = urlparse(url)
            # Must have scheme (http/https only) and netloc (domain)
            return bool(parsed.scheme in ['http', 'https'] and parsed.netloc)
        except Exception:
            return False
