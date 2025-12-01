"""
Proposal routes - Flask blueprint for handling proposal submissions and validation.
Implements spec 002: validate-and-add-radio-source.
"""

from typing import List
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from model.entity.stream_analysis import StreamAnalysis
from model.dto.stream_analysis import StreamAnalysisResult
from model.repository.stream_analysis_repository import StreamAnalysisRepository
from model.repository.proposal_repository import ProposalRepository
from model.repository.radio_source_repository import RadioSourceRepository
from model.entity.proposal import Proposal


proposal_bp = Blueprint('proposal', __name__)

# Repository and service initialization functions
def get_analysis_repo() -> StreamAnalysisRepository:
    from database import db
    return StreamAnalysisRepository(db.session)

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

def get_stream_analysis_service():
    stream_type_service = get_stream_type_service()
    from service.stream_analysis_service import StreamAnalysisService
    return StreamAnalysisService(stream_type_service)

def get_stream_type_repo():
    from database import db
    from model.repository.stream_type_repository import StreamTypeRepository
    return StreamTypeRepository(db.session)

def get_stream_type_service():
    stream_type_repo = get_stream_type_repo()
    from service.stream_type_service import StreamTypeService
    return StreamTypeService(stream_type_repo)


@proposal_bp.route('/propose', methods=['GET', 'POST'])
def propose():
    """Handle proposal submission form."""
    analysis_repo = get_analysis_repo()
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


    # Get all proposals for display
    streams_from_db: List[StreamAnalysis] = analysis_repo.find_all()
    streams: List[StreamAnalysisResult] = []
    for stream in streams_from_db:
        stream_validation = StreamAnalysisResult(
            is_valid=stream.is_valid,
            is_secure=stream.is_secure,
            stream_url=stream.stream_url,
            stream_type_id=stream.stream_type_id,
            error_code=stream.error_code,            
            detection_method=stream.detection_method,
            raw_content_type=stream.raw_content_type,
            raw_ffmpeg_output=stream.raw_ffmpeg_output
        )
        streams.append(stream_validation)
    return render_template('proposal.html', streams=streams)


@proposal_bp.route('/proposal_analyze', methods=['POST'])
def analyze_url():
    """Analyze a stream URL and show results."""
    url = request.form.get('url')
    
    if not url:
        flash('URL is required', 'error')
        return redirect(url_for('proposal.propose'))
    
    try:
        analysis_service = get_stream_analysis_service()
        result = analysis_service.analyze_stream(url)

        # Show the result in a simple format
        flash(f'Analysis result: {result.stream_type_display_name if result.stream_type_display_name else "Unknown"}', 'info')
        # Save detail in repo
        analysis_repo = get_analysis_repo()
        analysis_entity = StreamAnalysis(
            stream_url=result.url,
            is_valid=result.is_valid,
            is_secure=result.is_secure,
            error_code=result.error_code.name if result.error_code else None,
            stream_type_id=result.stream_type_id, 
            detection_method=result.detection_method.name if result.detection_method else None,
            raw_content_type=result.raw_content_type,
            raw_ffmpeg_output=result.raw_ffmpeg_output
        )
        analysis_repo.save(analysis_entity)              
   
    except Exception as e:
        flash(f'Analysis failed: {str(e)}', 'error')
    
    return redirect(url_for('proposal.propose'))


@proposal_bp.route('/proposal/<int:proposal_id>')
def proposal_detail(proposal_id):
    """Display proposal details and validation status."""
    proposal_repo = get_proposal_repo()
    validation_service = get_validation_service()
    
    proposal = proposal_repo.find_by_id(proposal_id)
    if not proposal:
        flash('Proposal not found', 'error')
        return redirect(url_for('database.list_sources'))

    # Get validation result
    validation_result = validation_service.validate_proposal(proposal)

    return render_template('proposal_detail.html',
                         proposal=proposal,
                         validation=validation_result)


@proposal_bp.route('/proposal/<int:proposal_id>/approve', methods=['POST'])
def approve_proposal(proposal_id):
    """Approve and convert proposal to radio source."""
    radio_source_service = get_radio_source_service()
    
    try:
        success = radio_source_service.convert_proposal_to_source(proposal_id)
        if success:
            flash('Proposal approved and added as radio source!', 'success')
        else:
            flash('Failed to approve proposal', 'error')
    except Exception as e:
        flash(f'Error approving proposal: {str(e)}', 'error')

    return redirect(url_for('proposal.proposal_detail', proposal_id=proposal_id))


@proposal_bp.route('/api/proposals', methods=['GET'])
def get_proposals():
    """API endpoint to get all proposals."""
    proposal_repo = get_proposal_repo()
    proposals = proposal_repo.find_all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'url': p.url,
        'description': p.description,
        'user_name': p.user_name,
        'created_at': p.created_at.isoformat() if p.created_at else None,
        'status': 'pending'
    } for p in proposals])


@proposal_bp.route('/api/proposal/<int:proposal_id>/validate', methods=['GET'])
def validate_proposal_api(proposal_id):
    """API endpoint to validate a proposal."""
    proposal_repo = get_proposal_repo()
    validation_service = get_validation_service()
    
    proposal = proposal_repo.find_by_id(proposal_id)
    if not proposal:
        return jsonify({'error': 'Proposal not found'}), 404

    result = validation_service.validate_proposal(proposal)
    return jsonify({
        'is_valid': result.is_valid,
        'message': result.message,
        'security_status': result.security_status.value if result.security_status else None
    })