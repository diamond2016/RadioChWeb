"""
Proposal routes - Flask blueprint for handling proposal submissions and validation.
Implements spec 003: propose-new-radio-source and spec 004: admin-approve-proposal."""

from typing import List
from flask import Blueprint, request, render_template, redirect, url_for, flash

from model.dto.validation import ValidationResult
from model.entity.radio_source import RadioSource
from model.repository.proposal_repository import ProposalRepository
from model.repository.radio_source_repository import RadioSourceRepository
from model.entity.proposal import Proposal
from model.dto.proposal import ProposalDTO, ProposalUpdateRequest
from model.repository.stream_type_repository import StreamTypeRepository
from route.analysis_route import get_stream_type_repo
from service.proposal_service import ProposalService
from database import db
from service.proposal_validation_service import ProposalValidationService
from service.proposal_service import ProposalService
from service.radio_source_service import RadioSourceService
from service.stream_type_service import StreamTypeService

proposal_bp = Blueprint('proposal', __name__, url_prefix='/proposal')


def get_proposal_repo() -> ProposalRepository:
    return ProposalRepository(db.session)

def get_radio_source_repo() -> RadioSourceRepository:
    return RadioSourceRepository(db.session)

def get_validation_service() -> ProposalValidationService:
    proposal_repo: ProposalRepository = get_proposal_repo()
    radio_source_repo: RadioSourceRepository = get_radio_source_repo()
    from service.proposal_validation_service import ProposalValidationService
    return ProposalValidationService(proposal_repo, radio_source_repo)

def get_radio_source_service() -> RadioSourceService:
    proposal_repo: ProposalRepository = get_proposal_repo()
    radio_source_repo: RadioSourceRepository = get_radio_source_repo()
    validation_service: ProposalValidationService = get_validation_service()
    from service.radio_source_service import RadioSourceService
    return RadioSourceService(proposal_repo, radio_source_repo, validation_service)

def get_stream_type_service() -> StreamTypeService:
    stream_type_repo: StreamTypeRepository = get_stream_type_repo()
    from service.stream_type_service import StreamTypeService
    return StreamTypeService(stream_type_repo)

def get_proposal_service() -> ProposalService:
    proposal_repo: ProposalRepository = get_proposal_repo()
    from service.proposal_service import ProposalService
    return ProposalService(proposal_repo)


@proposal_bp.route('/', methods=['GET'])
def index():
    """Display the proposals page with all proposals"""

    # Get all proposals for display (pass entity objects so templates can access id)
    proposal_service: ProposalService = get_proposal_service()   
    proposals: List[ProposalDTO] = proposal_service.get_all_proposals()
    return render_template('proposals.html', proposals=proposals)


@proposal_bp.route('/propose', methods=['GET', 'POST'])
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
def update_proposal(proposal_id):
    proposal_service = get_proposal_service()
    proposal: ProposalDTO = proposal_service.get_proposal(proposal_id)
    
    if request.method == 'POST':
        # Read form values and delegate update to ProposalService
        name: str | None = request.form.get('name')
        website_url: str | None = request.form.get('website_url')
        country: str | None = request.form.get('country')
        description: str | None = request.form.get('description')
        # Accept either 'image' (form) or 'image_url' (tests/clients)
        image_url: str | None = request.form.get('image_url') or request.form.get('image') or None  

        update_dto = ProposalUpdateRequest(
            name=name,
            website_url=website_url,
            country=country,
            description=description,
            image_url=image_url
        )
        proposal_service: ProposalService = get_proposal_service()
        try:
            proposal_service.update_proposal(proposal_id, update_dto)
            flash('Proposal updated successfully', 'success')

        except Exception as e:
            flash(f'Failed to update proposal: {str(e)}', 'error')

        return redirect(url_for('proposal.index'))

    return render_template('proposal_detail.html',proposal=proposal)


@proposal_bp.route('/approve/<int:proposal_id>', methods=['POST'])
def approve_proposal(proposal_id):
    """Approve and convert proposal to radio source."""
    radio_source_service = get_radio_source_service()
    
    try:
        success: RadioSource = radio_source_service.save_from_proposal(proposal_id)
        if success:
            flash('Proposal approved and added as radio source!', 'success')
        else:
            flash('Failed to approve proposal', 'error')
    except Exception as e:
        flash(f'Error approving proposal: {str(e)}', 'error')

    return redirect(url_for('proposal.index'))


@proposal_bp.route('/reject/<int:proposal_id>', methods=['POST'])
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
