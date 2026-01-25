from model.entity.proposal import Proposal
from flask import session


def test_update_proposal_post(test_app, test_db, test_user):
    # Create a proposal in the test DB
    proposal = Proposal(
        stream_url='https://stream.example.com/test',
        name='Old Name',
        website_url='https://old.example.com',
        stream_type_id=1,
        is_secure=False,
        country='OldCountry',
        description='Old description',
        image_url='https://old.example.com/img.png'
    )
    # set the owner to the test user so the edit is allowed
    proposal.created_by = test_user.id
    test_db.add(proposal)
    test_db.commit()
    test_db.refresh(proposal)

    # Prepare updated data
    data = {
        'name': 'New Name',
        'website_url': 'https://new.example.com',
        'country': 'Italy',
        'description': 'New description',
        'image_url': 'https://new.example.com/img.png'
    }

    # Register blueprint so url_for('proposal.index') resolves during the view
    from route.proposal_route import proposal_bp
    

    # register only if not present to avoid "register_blueprint after first request" errors
    if proposal_bp.name not in test_app.blueprints:
        test_app.register_blueprint(proposal_bp)

    # Call the view function within a request context
    with test_app.test_request_context(f'/proposal/{proposal.id}', method='POST', data=data):
        # Simulate logged-in user session
        session['_user_id'] = str(test_user.id)
        session['_fresh'] = True
        from route.proposal_route import update_proposal
        resp = update_proposal(proposal.id)

        # Expect a redirect response to proposals index
        assert resp.status_code == 302

    # Reload from DB and assert changes
    updated = test_db.query(Proposal).filter(Proposal.id == proposal.id).first()
    assert updated is not None
    assert updated.name == 'New Name'
    assert updated.website_url == 'https://new.example.com'
    assert updated.country == 'Italy'
    assert updated.description == 'New description'
    assert updated.image_url == 'https://new.example.com/img.png'
