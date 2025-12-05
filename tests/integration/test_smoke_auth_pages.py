from pathlib import Path


def register_blueprints(app):
    # Register the blueprints referenced by the index template so url_for() works
    from route.main_route import main_bp
    from route.database_route import database_bp
    from route.analysis_route import analysis_bp
    from route.proposal_route import proposal_bp
    from route.radio_source_route import radio_source_bp
    from route.listen_route import listen_bp
    from route.auth_route import auth_bp
    from service.auth_service import AuthService

    app.template_folder = str(Path(__file__).parents[2] / 'templates')
    # Register blueprints only if they are not already registered (idempotent)
    for bp in (main_bp, database_bp, analysis_bp, proposal_bp, radio_source_bp, listen_bp, auth_bp):
        if bp.name not in app.blueprints:
            app.register_blueprint(bp)


def test_smoke_auth_pages_render(test_app):
    register_blueprints(test_app)
    client = test_app.test_client()

    r = client.get('/auth/login')
    assert r.status_code == 200
    assert b'Login' in r.data

    r = client.get('/auth/register')
    assert r.status_code == 200
    assert b'Register' in r.data
