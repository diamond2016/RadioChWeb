"""
Proposal routes - Flask blueprint for handling proposal submissions and validation.
Implements spec 003: propose-new-radio-source and spec 004: admin-approve-proposal."""

from typing import List
from flask import Blueprint, request, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from database import db, get_db_session
from model.dto.radio_source import RadioSourceDTO
from model.dto.validation import ValidationResult
from model.dto.proposal import ProposalDTO

from model.entity.proposal import Proposal

from model.repository.proposal_repository import ProposalRepository
from model.repository.radio_source_repository import RadioSourceRepository
from model.repository.stream_type_repository import StreamTypeRepository

from route.analysis_route import get_stream_type_repo

from service.auth_service import AuthService, admin_required
from service.proposal_service import ProposalService
from service.proposal_validation_service import ProposalValidationService
from service.proposal_service import ProposalService
from service.radio_source_service import RadioSourceService
from service.stream_type_service import StreamTypeService

proposal_bp = Blueprint('proposal', __name__, url_prefix='/proposal')


def get_proposal_repo() -> ProposalRepository:
    return ProposalRepository(get_db_session())

def get_radio_source_repo() -> RadioSourceRepository:
    return RadioSourceRepository(get_db_session())

def get_proposal_service() -> ProposalService:
    proposal_repo: ProposalRepository = get_proposal_repo()
    return ProposalService(proposal_repo)

def get_auth_service() -> AuthService:
    return AuthService()

def get_radio_source_service() -> RadioSourceService:
    proposal_repo: ProposalRepository = get_proposal_repo()
    radio_source_repo: RadioSourceRepository = get_radio_source_repo()
    proposal_service: ProposalService = get_proposal_service()
    auth_service: AuthService = get_auth_service()
    stream_type_service: StreamTypeService = get_stream_type_service()
    
    return RadioSourceService(proposal_repo, radio_source_repo, proposal_service, auth_service, stream_type_service)  


def get_stream_type_service() -> StreamTypeService:
    stream_type_repo: StreamTypeRepository = get_stream_type_repo()
    from service.stream_type_service import StreamTypeService
    return StreamTypeService(stream_type_repo)



@proposal_bp.route('/', methods=['GET'])
@login_required
def index():
    """Display the proposals page.

    Admins see all proposals; regular authenticated users see only their own proposals.
    """

    proposal_service: ProposalService = get_proposal_service()
    all_proposals: List[ProposalDTO] = proposal_service.get_all_proposals()

    if getattr(current_user, 'is_admin', False):
        proposals = all_proposals
    else:
        # Filter proposals to those created by the current user
        user_id = getattr(current_user, 'id', None)
        proposals = [p for p in all_proposals if (p.user and getattr(p.user, 'id', None) == user_id)]

    return render_template('proposals.html', proposals=proposals)


@proposal_bp.route('/propose', methods=['GET', 'POST'])
@login_required
def propose():
    """Handle proposal submission form."""
    proposal_repo: ProposalRepository = get_proposal_repo()
    validation_service: ProposalValidationService = get_validation_service()

    if request.method == 'POST':
        # Extract form data
        name = request.form.get('name')
        url = request.form.get('url')
        description = request.form.get('description', '')
        user_name = request.form.get('user_name', 'Anonymous')

        # Create proposal
        proposal = Proposal(
            name=name,
            url=url,
            description=description,
            user_name=user_name
        )

        # Validate and save
        try:
            result: ValidationResult = validation_service.validate_proposal(proposal)
            if result.is_valid:
                # Save proposal
                proposal_repo.save(proposal)
                flash('Proposal submitted successfully!', 'success')
                return redirect(url_for('proposal.proposal_detail', proposal_id=proposal.id))
            else:
                flash(f'Validation failed: {result.message}', 'error')
        except Exception as e:
            flash(f'Error submitting proposal: {str(e)}', 'error')

        # After proposing or when visiting this endpoint, show the proposals listing
        return redirect(url_for('proposal.index'))



@proposal_bp.route('/update/<int:proposal_id>', methods=['GET', 'POST'])
@login_required
def update_proposal(proposal_id):
    proposal_service = get_proposal_service()
    proposal: ProposalDTO = proposal_service.get_proposal(proposal_id)
    # Only the proposal owner or an admin may edit
    if not current_user.is_authenticated:
        abort(403)
    owner_id = getattr(getattr(proposal, 'user', None), 'id', None)
    if not (getattr(current_user, 'is_admin', False) or (owner_id is not None and owner_id == getattr(current_user, 'id', None))):
        abort(403)
    
    if request.method == 'POST':
        # Read form values and delegate update to ProposalService
        name: str | None = request.form.get('name')
        website_url: str | None = request.form.get('website_url')
        country: str | None = request.form.get('country')
        description: str | None = request.form.get('description')
        # Accept either 'image' (form) or 'image_url' (tests/clients)
        image_url: str | None = request.form.get('image_url') or request.form.get('image') or None  

        existing: ProposalDTO | None = proposal_service.get_proposal(proposal_id)    
        new = ProposalDTO(
            id=existing.id,
            stream_url=existing.stream_url,
            name=name if name is not None else existing.name,
            website_url=website_url if website_url is not None else existing.website_url,
            country=country if country is not None else existing.country,       
            description=description if description is not None else existing.description,   
            image_url=image_url if image_url is not None else existing.image_url,
            stream_type=existing.stream_type,
            is_secure=existing.is_secure
        )
        proposal_service: ProposalService = get_proposal_service()
        try:
            proposal_service.update_proposal(proposal_id, new)
            flash('Proposal updated successfully', 'success')

        except Exception as e:
            flash(f'Failed to update proposal: {str(e)}', 'error')

        return redirect(url_for('proposal.index'))

    return render_template('proposal_detail.html',proposal=proposal)


@proposal_bp.route('/approve/<int:proposal_id>', methods=['POST'])
@admin_required
def approve_proposal(proposal_id):
    """Approve and convert proposal to radio source."""
    radio_source_service = get_radio_source_service()
    
    try:
        success: RadioSourceDTO = radio_source_service.save_from_proposal(proposal_id)
        if success:
            flash('Proposal approved and added as radio source!', 'success')
        else:
            flash('Failed to approve proposal', 'error')
    except Exception as e:
        flash(f'Error approving proposal: {str(e)}', 'error')

    return redirect(url_for('proposal.index'))


@proposal_bp.route('/reject/<int:proposal_id>', methods=['POST'])
@admin_required
def reject_proposal(proposal_id):
    """Deletes(rejects) a proposal to radio source."""
    proposal_service: ProposalService = get_proposal_service()
    
    try:
        success: bool = proposal_service.reject_proposal(proposal_id)
        if success:
            flash('Proposal rejected successfully!', 'success')
        else:
            flash('Failed to reject proposal', 'error')
    except Exception as e:
        flash(f'Error rejecting proposal: {str(e)}', 'error')
        
    return redirect(url_for('proposal.index'))
