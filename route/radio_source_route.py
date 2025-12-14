"""
Radio source routes - Flask blueprint for managing radio sources.
Provides CRUD operations for radio sources.
"""

from typing import List
from flask import Blueprint, request,render_template, redirect, url_for, flash

from model.dto.radio_source import RadioSourceDTO
from model.entity.stream_type import StreamType
from model.repository.proposal_repository import ProposalRepository
from model.repository.stream_type_repository import StreamTypeRepository
from service.auth_service import AuthService
from service.proposal_service import ProposalService
from service.radio_source_service import RadioSourceService
from model.repository.radio_source_repository import RadioSourceRepository
from database import db
from service.stream_type_service import StreamTypeService

radio_source_bp = Blueprint('radio_source', __name__, url_prefix='/source')

# Repository and service initialization functions
def get_radio_source_repo() -> RadioSourceRepository:
    return RadioSourceRepository(db.session)

# Repository and service initialization functions
def get_proposal_repo() -> ProposalRepository:
    return ProposalRepository(db.session)

def get_stream_type_repo() -> StreamTypeRepository:
    return StreamTypeRepository(db.session)

def get_auth_service():
    from service.auth_service import AuthService
    return AuthService(None)  # Pass necessary dependencies if any

def get_stream_type_service() -> StreamTypeService:
    stream_type_repo: StreamTypeRepository = get_stream_type_repo()
    return StreamTypeService(stream_type_repo)  # Pass necessary dependencies if any

def gest_proposal_service() -> ProposalService:
    proposal_repo: ProposalRepository = get_proposal_repo()
    return ProposalService(proposal_repo)  # Pass necessary dependencies if any

def get_radio_source_service() -> RadioSourceService:
    proposal_repo: ProposalRepository = get_proposal_repo()
    radio_source_repo: RadioSourceRepository = get_radio_source_repo()
    proposal_service: ProposalService = gest_proposal_service()
    auth_service: AuthService = get_auth_service()
    stream_type_service: StreamTypeService = get_stream_type_service()
    
    return RadioSourceService(proposal_repo, radio_source_repo, proposal_service, auth_service, stream_type_service)  


@radio_source_bp.route('/<int:source_id>')
def source_detail(source_id: int):
    """Display radio source details."""
    
    radio_source_service: RadioSourceService = get_radio_source_service()
    source: RadioSourceDTO | None = radio_source_service.get_radio_source_by_id(source_id)

    if not source:
        flash('Radio source not found', 'error')
        return redirect(url_for('main.index'))

    return render_template('source_detail.html', source=source)


@radio_source_bp.route('/edit/<int:source_id>', methods=['GET', 'POST'])
def edit_source(source_id: int):
    """Edit radio source."""
    radio_source_service: RadioSourceService = get_radio_source_service()
    stream_type_repo: StreamTypeRepository = get_stream_type_repo()
    source: RadioSourceDTO | None = radio_source_service.get_radio_source_by_id(source_id)
    
    if not source:
        flash('Radio source not found', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        source.name = request.form.get('name')
        source.description = request.form.get('description', '')
        source.image_url = request.form.get('image_url', '')
        source.website_url = request.form.get('website_url', '')

        try:
            radio_source_service.update_radio_source(source)
            flash('Radio source updated successfully!', 'success')
            return redirect(url_for('main.index'))
        
        except Exception as e:
            flash(f'Error updating source: {str(e)}', 'error')

    # For GET request, show edit form

    return render_template('edit_source.html', source=source)


@radio_source_bp.route('/delete/<int:source_id>', methods=['POST'])
def delete_source(source_id: int):
    """Delete radio source."""
    radio_source_service: RadioSourceService = get_radio_source_service()
    
    if radio_source_service.delete_radio_source(source_id):
        flash('Radio source deleted successfully!', 'success')
    else:
        flash('Error deleting source', 'error')

    return redirect(url_for('main.index'))
