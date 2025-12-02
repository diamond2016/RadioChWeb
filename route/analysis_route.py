"""
Analysys route - Flask blueprint for handling stream analysis and submissions.
Implements spec 002: validate-and-add-radio-source (to be modified spec).
"""

from typing import List
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from model.entity.stream_analysis import StreamAnalysis
from model.dto.stream_analysis import StreamAnalysisResult
from model.repository.stream_analysis_repository import StreamAnalysisRepository
from model.repository.proposal_repository import ProposalRepository
from model.repository.radio_source_repository import RadioSourceRepository
from model.entity.proposal import Proposal
from model.repository.stream_type_repository import StreamTypeRepository
from service.stream_analysis_service import StreamAnalysisService
from service.stream_type_service import StreamTypeService


analysis_bp = Blueprint('analysis', __name__)

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

def get_stream_type_repo() -> StreamTypeRepository:
    from database import db
    from model.repository.stream_type_repository import StreamTypeRepository
    return StreamTypeRepository(db.session)

def get_stream_analysis_service() -> StreamAnalysisService:
    stream_type_service = get_stream_type_service()
    from service.stream_analysis_service import StreamAnalysisService
    return StreamAnalysisService(stream_type_service, get_proposal_repo(), get_analysis_repo())


def get_stream_type_service():
    stream_type_repo = get_stream_type_repo()
    from service.stream_type_service import StreamTypeService
    return StreamTypeService(stream_type_repo)


@analysis_bp.route('/', methods=['GET'])
def index():
    """Display the analysis page with all stream analyses."""
    analysis_repo = get_analysis_repo()

    # Get all analyses for display (pass entity objects so templates can access id)
    streams_from_db: List[StreamAnalysis] = analysis_repo.find_all()
    return render_template('analysis.html', streams=streams_from_db)


@analysis_bp.route('/analyze', methods=['POST'])
def analyze_url():
    """Analyze a stream URL and show results."""
    url = request.form.get('url')
    
    if not url:
        flash('URL is required', 'error')
        return redirect(url_for('analysis.index'))
    
    try:
        analysis_service: StreamAnalysisService = get_stream_analysis_service()
        result: StreamAnalysisResult = analysis_service.analyze_stream(url)

        # Show the result in a simple format
        flash(f'Analysis result: {result.stream_type_display_name if result.stream_type_display_name else "Unknown"}', 'info')

        # Save detail in repo
        analysis_repo = get_analysis_repo()
        analysis_entity = StreamAnalysis(
            stream_url=url,
            is_valid=result.is_valid,
            is_secure=result.is_secure,
            error_code=result.error_code.name if result.error_code else None,
            stream_type_id=result.stream_type_id, 
            detection_method=result.detection_method.name if result.detection_method else None,
            raw_content_type=result.raw_content_type,
            raw_ffmpeg_output=result.raw_ffmpeg_output,
            extracted_metadata=result.extracted_metadata
        )
        analysis_repo.save(analysis_entity)              
   
    except Exception as e:
        flash(f'Analysis failed: {str(e)}', 'error')
    
    return redirect(url_for('analysis.index'))


@analysis_bp.route('/approve/<int:id>', methods=['POST'])
def approve_analysis(id: int):
    """Approve an analysis and creates a proposal."""
    
    try:
        analysis_service: StreamAnalysisService = get_stream_analysis_service()
        success = analysis_service.save_analysis_as_proposal(id)
        if success:
            flash('ProposalAnalysis approved and added as proposal for radio source!', 'success')
        else:
            flash('Failed to approve stream analysis', 'error')
    except Exception as e:
        flash(f'Error approving stream analysis: {str(e)}', 'error')

    return redirect(url_for('proposal.index'))


@analysis_bp.route('/delete/<int:id>', methods=['POST'])
def delete_analysis(id: int):
    """Delete an analysis."""
    analysis_service: StreamAnalysisService = get_stream_analysis_service()
    
    try:
        success = analysis_service.delete_analysis(id)
        if success:
            flash('Stream analysis deleted successfully!', 'success')
        else:
            flash('Failed to delete stream analysis', 'error')
    except Exception as e:
        flash(f'Error deleting stream analysis: {str(e)}', 'error')
    return redirect(url_for('analysis.index'))