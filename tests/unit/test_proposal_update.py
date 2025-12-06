from model.entity.proposal import Proposal


def test_update_proposal_post(test_app, test_db, test_user, login_helper):
    # Create a proposal in DB
    proposal = Proposal(
        stream_url="https://stream.example.com/test",
        name="Old Name",
        website_url="https://old.example.com",
        stream_type_id=1,
        is_secure=False,
        country="OldCountry",
        description="Old description",
        image_url="https://old.example.com/img.png",
        proposal_user=test_user,
    )
    test_db.add(proposal)
    test_db.flush()
    test_db.refresh(proposal)

    data: dict[str, str] = {
        "name": "New Name",
        "website_url": "https://new.example.com",
        "country": "Italy",
        "description": "New description",
        "image_url": "https://new.example.com/img.png",
    }

    # Ensure blueprint/extension registration happens before opening the client
    from route.proposal_route import proposal_bp
    if proposal_bp.name not in test_app.blueprints:
        test_app.register_blueprint(proposal_bp)

    with test_app.test_client() as client:
        # Use the login helper to set the session (_user_id etc.) for this client
        login_helper(client)

        # POST via the client so Flask-Login loads current_user
        resp = client.post(f"/proposal/update/{proposal.id}", data=data, follow_redirects=False)
        assert resp.status_code == 302

    # Verify DB changes after the request
    updated = test_db.query(Proposal).filter(Proposal.id == proposal.id).first()
    assert updated.image_url == "https://new.example.com/img.png"
