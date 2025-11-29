"""
Radio source routes - Flask blueprint for managing radio sources.
Provides CRUD operations for radio sources.
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from service.radio_source_service import RadioSourceService
from model.repository.proposal_repository import ProposalRepository
from model.repository.radio_source_repository import RadioSourceRepository
from model.entity.radio_source import RadioSource
from database import db

radio_source_bp = Blueprint('radio_source', __name__)

# Repository and service initialization functions
def get_radio_source_repo():
    from database import db
    return RadioSourceRepository(db.session)

def get_radio_source_service():
    radio_source_repo = get_radio_source_repo()
    from service.radio_source_service import RadioSourceService
    return RadioSourceService(None, radio_source_repo, None)  # Validation service will be injected if needed

def get_stream_type_repo():
    from database import db
    return StreamTypeRepository(db.session)


@radio_source_bp.route('/source/<int:source_id>')
def source_detail(source_id):
    """Display radio source details."""
    radio_source_repo = get_radio_source_repo()
    source = radio_source_repo.find_by_id(source_id)
    if not source:
        flash('Radio source not found', 'error')
        return redirect(url_for('database.list_sources'))

    return render_template('source_detail.html', source=source)


@radio_source_bp.route('/source/<int:source_id>/edit', methods=['GET', 'POST'])
def edit_source(source_id):
    """Edit radio source."""
    radio_source_repo = get_radio_source_repo()
    stream_type_repo = get_stream_type_repo()
    
    source = radio_source_repo.find_by_id(source_id)
    if not source:
        flash('Radio source not found', 'error')
        return redirect(url_for('database.list_sources'))

    if request.method == 'POST':
        source.name = request.form.get('name')
        source.url = request.form.get('url')
        source.description = request.form.get('description', '')
        source.stream_type_id = int(request.form.get('stream_type_id'))

        try:
            radio_source_repo.save(source)
            flash('Radio source updated successfully!', 'success')
            return redirect(url_for('radio_source.source_detail', source_id=source.id))
        except Exception as e:
            flash(f'Error updating source: {str(e)}', 'error')

    # For GET request, show edit form
    stream_types = stream_type_repo.find_all()

    return render_template('edit_source.html', source=source, stream_types=stream_types)


@radio_source_bp.route('/source/<int:source_id>/delete', methods=['POST'])
def delete_source(source_id):
    """Delete radio source."""
    radio_source_service = get_radio_source_service()
    
    try:
        radio_source_service.delete_source(source_id)
        flash('Radio source deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting source: {str(e)}', 'error')

    return redirect(url_for('database.list_sources'))


@radio_source_bp.route('/api/sources', methods=['GET'])
def get_sources():
    """API endpoint to get all radio sources."""
    radio_source_repo = get_radio_source_repo()
    sources = radio_source_repo.find_all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'url': s.url,
        'description': s.description,
        'stream_type': s.stream_type.name if s.stream_type else None,
        'created_at': s.created_at.isoformat() if s.created_at else None,
        'updated_at': s.updated_at.isoformat() if s.updated_at else None
    } for s in sources])


@radio_source_bp.route('/api/source/<int:source_id>', methods=['GET'])
def get_source(source_id):
    """API endpoint to get a specific radio source."""
    radio_source_repo = get_radio_source_repo()
    source = radio_source_repo.find_by_id(source_id)
    if not source:
        return jsonify({'error': 'Radio source not found'}), 404

    return jsonify({
        'id': source.id,
        'name': source.name,
        'url': source.url,
        'description': source.description,
        'stream_type': source.stream_type.name if source.stream_type else None,
        'created_at': source.created_at.isoformat() if source.created_at else None,
        'updated_at': source.updated_at.isoformat() if source.updated_at else None
    })