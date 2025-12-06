from unittest.mock import patch

from model.entity.stream_analysis import StreamAnalysis
from model.entity.proposal import Proposal



def test_delete_analysis_route_removes_row(test_app, test_db, test_user, login_helper):
    # Ensure session works for flashing
    test_app.secret_key = "test-secret"

    # Insert a StreamAnalysis row with required fields
    sa = StreamAnalysis(
        stream_url="http://test/delete",
        is_valid=True,
        is_secure=False,
        stream_type_id=1,
        stream_user=test_user # a user can delete analyze that have created
    )
    test_db.add(sa)
    test_db.commit()
    assert sa.id is not None
    
    # Ensure blueprint/extension registration happens before opening the client
    from route.analysis_route import analysis_bp
    if analysis_bp.name not in test_app.blueprints:
        test_app.register_blueprint(analysis_bp)

    
# Patch shutil.which so constructing StreamAnalysisService inside route doesn't raise
    with patch(
        "service.stream_analysis_service.shutil.which", return_value="/usr/bin/ffmpeg"
    ):

        with test_app.test_client() as client:
            login_helper(client)  # Log in as test_user
            resp = client.post(f"/analysis/delete/{sa.id}")
            print(resp.data)

            # view returns a redirect response object (or response)
            assert resp is not None

    # Verify the row was deleted
    found = test_db.query(StreamAnalysis).filter(StreamAnalysis.id == sa.id).first()
    assert found is None


def test_approve_analysis_route_creates_proposal(test_app, test_db, login_helper, test_user):
    # Ensure session works for flashing
    test_app.secret_key = "test-secret"

    # Insert a StreamAnalysis row with required fields
    sa = StreamAnalysis(
    stream_url="http://test/propose",
    is_valid=True,
    is_secure=True,
    stream_type_id=1,
    stream_user=test_user
    )

    test_db.add(sa)
    test_db.commit()
    assert sa.id is not None
    
    # Ensure blueprint/extension registration happens before opening the client
    from route.analysis_route import analysis_bp
    if analysis_bp.name not in test_app.blueprints:
        test_app.register_blueprint(analysis_bp)

    # Patch shutil.which so constructing StreamAnalysisService inside route doesn't raise
    with patch(
        "service.stream_analysis_service.shutil.which", return_value="/usr/bin/ffmpeg"
    ):
        with patch("route.analysis_route.url_for", return_value="/"):
            with test_app.test_client() as client:
                login_helper(client) # Log in as test_user
                resp = client.post(f"/analysis/approve/{sa.id}")
                assert resp is not None

    # Verify the StreamAnalysis row was removed after proposing
    found = (
        test_db.query(StreamAnalysis)
        .filter(StreamAnalysis.stream_url == sa.stream_url)
        .first()
    )
    assert found is None

    # Verify a Proposal was created for that stream_url
    proposal = (
        test_db.query(Proposal).filter(Proposal.stream_url == sa.stream_url).first()
    )
    assert proposal is not None
    assert proposal.stream_url == sa.stream_url
