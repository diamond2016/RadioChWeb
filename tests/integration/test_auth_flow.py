from route.main_route import main_bp
from route.auth_route import auth_bp
from route.database_route import database_bp
from route.analysis_route import analysis_bp
from route.proposal_route import proposal_bp
from route.radio_source_route import radio_source_bp
from route.listen_route import listen_bp
from service.auth_service import AuthService
from pathlib import Path


def register_blueprints_and_auth(app):
    # Ensure Flask finds the repository `templates/` folder when tests create app instances
    app.template_folder = str(Path(__file__).parents[2] / 'templates')
    # Register blueprints only if they are not already registered (idempotent)
    for bp in (main_bp, database_bp, analysis_bp, proposal_bp, radio_source_bp, listen_bp, auth_bp):
        if bp.name not in app.blueprints:
            app.register_blueprint(bp)
    AuthService(app)



def test_register_login_logout_flow(test_app):
    register_blueprints_and_auth(test_app)
    client = test_app.test_client()

    # Register
    resp = client.post('/auth/register', data={
        'email': 'tester@example.com',
        'password': 'Password123',
        'confirm': 'Password123'
    }, follow_redirects=True)
    assert b'Registration successful' in resp.data

    # Login
    resp = client.post('/auth/login', data={
        'email': 'tester@example.com',
        'password': 'Password123'
    }, follow_redirects=True)
    # After login index should show Logout link and email
    assert b'Logout' in resp.data
    assert b'tester@example.com' in resp.data

    # Logout
    resp = client.get('/auth/logout', follow_redirects=True)
    assert b'Login' in resp.data
