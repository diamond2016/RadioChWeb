"""
Proposal routes - Flask blueprint for handling proposal submissions and validation.
Implements spec 002: validate-and-add-radio-source.
"""

from typing import List
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required

from model.entity.radio_source import RadioSource
from model.repository.proposal_repository import ProposalRepository
from model.repository.radio_source_repository import RadioSourceRepository
from model.entity.proposal import Proposal
from model.dto.validation import ProposalUpdateRequest
from service.proposal_service import ProposalService
from service.authorization import admin_required


proposal_bp = Blueprint('proposal', __name__, url_prefix='/proposal')


def get_proposal_repo():
    from database import db
    return ProposalRepository(db.session)

def get_radio_source_repo():
    from database import db
    return RadioSourceRepository(db.session)

def get_validation_service():
    proposal_repo = get_proposal_repo()
    radio_source_repo = get_radio_source_repo()
    from service.proposal_validation_service import ProposalValidationService
    return ProposalValidationService(proposal_repo, radio_source_repo)

def get_radio_source_service():
    proposal_repo = get_proposal_repo()
    radio_source_repo = get_radio_source_repo()
    validation_service = get_validation_service()
    from service.radio_source_service import RadioSourceService
    return RadioSourceService(proposal_repo, radio_source_repo, validation_service)

def get_stream_type_service():
    stream_type_repo = get_stream_type_repo()
    from service.stream_type_service import StreamTypeService
    return StreamTypeService(stream_type_repo)


def get_proposal_service():
    proposal_repo = get_proposal_repo()
    from service.proposal_service import ProposalService
    return ProposalService(proposal_repo)


@proposal_bp.route('/', methods=['GET'])
def index():
    """Display the proposals page with all proposals"""
    proposal_repo: ProposalRepository = get_proposal_repo()

    # Get all proposals for display (pass entity objects so templates can access id)
    proposals_from_db: List[Proposal] = proposal_repo.find_all()
    return render_template('proposals.html', proposals=proposals_from_db)


# only a registered use can propose a new radio source
@login_required
@proposal_bp.route('/propose', methods=['GET', 'POST'])
def propose():
    """Handle proposal submission form."""
    proposal_repo = get_proposal_repo()
    validation_service = get_validation_service()

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
            result = validation_service.validate_proposal(proposal)
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


@login_required
@proposal_bp.route('/update/<int:proposal_id>', methods=['GET', 'POST'])
def proposal_detail(proposal_id):
    if request.method == 'POST':
        # Read form values and delegate update to ProposalService
        name = request.form.get('name')
        website_url = request.form.get('website_url')
        country = request.form.get('country')
        description = request.form.get('description')
        # Accept either 'image' (form) or 'image_url' (tests/clients)
        image = request.form.get('image_url') or request.form.get('image') or None  

        update_dto = ProposalUpdateRequest(
            name=name,
            website_url=website_url,
            country=country,
            description=description,
            image=image
        )

        proposal_service: ProposalService = get_proposal_service()
        try:
            proposal_service.update_proposal(proposal_id, update_dto)
            flash('Proposal updated successfully', 'success')
        except Exception as e:
            flash(f'Failed to update proposal: {str(e)}', 'error')

        return redirect(url_for('proposal.index'))

    """Display proposal details and validation status."""
    proposal_repo = get_proposal_repo()
    
    proposal = proposal_repo.find_by_id(proposal_id)
    if not proposal:
        flash('Proposal not found', 'error')
        return redirect(url_for('proposal.index'))

    return render_template('proposal_detail.html',proposal=proposal)


# only admin users can approve proposals
@admin_required
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
