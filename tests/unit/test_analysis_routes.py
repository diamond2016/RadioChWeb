import pytest
from unittest.mock import patch

from route.analysis_route import analysis_bp, delete_analysis, approve_analysis
from route.proposal_route import proposal_bp
from database import db
from model.entity.stream_analysis import StreamAnalysis
from model.entity.proposal import Proposal


def _register_blueprints(app):
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(proposal_bp, url_prefix='/proposal')


def test_delete_analysis_route_removes_row(test_app, test_db):
    # Ensure session works for flashing
    test_app.secret_key = 'test-secret'

    # Insert a StreamAnalysis row
    sa = StreamAnalysis(stream_url='http://test/delete', is_valid=True, is_secure=False, stream_type_id=1)
    test_db.add(sa)
    test_db.commit()

    assert sa.id is not None

    # Patch shutil.which so constructing StreamAnalysisService inside route doesn't raise
    with patch('service.stream_analysis_service.shutil.which', return_value='/usr/bin/ffmpeg'):
        # Patch url_for used inside the view to avoid needing registered endpoints
        with patch('route.analysis_route.url_for', return_value='/'):
            with test_app.test_request_context(f'/analysis/delete/{sa.id}', method='POST'):
                resp = delete_analysis(sa.id)
                # view returns a redirect response object (or response)
                assert resp is not None

    # Verify the row was deleted
    found = test_db.query(StreamAnalysis).filter(StreamAnalysis.id == sa.id).first()
    assert found is None


def test_approve_analysis_route_creates_proposal(test_app, test_db):
    # Ensure session works for flashing
    test_app.secret_key = 'test-secret'

    # Insert a StreamAnalysis row with required fields
    sa = StreamAnalysis(stream_url='http://test/propose', is_valid=True, is_secure=True, stream_type_id=1)
    test_db.add(sa)
    test_db.commit()
    assert sa.id is not None

    with patch('service.stream_analysis_service.shutil.which', return_value='/usr/bin/ffmpeg'):
        with patch('route.analysis_route.url_for', return_value='/'):
            with test_app.test_request_context(f'/analysis/approve/{sa.id}', method='POST'):
                resp = approve_analysis(sa.id)
                assert resp is not None

    # Verify a Proposal was created for that stream_url
    proposal = test_db.query(Proposal).filter(Proposal.stream_url == sa.stream_url).first()
    assert proposal is not None
    assert proposal.stream_url == sa.stream_url
