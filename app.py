from flask import Flask
# Import db from separate module
from database import DATABASE_URL, db

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key'  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Enable CSRF protection for forms
try:
    from flask_wtf import CSRFProtect
    csrf = CSRFProtect(app)
except Exception:
    # If flask-wtf is not installed in the environment, app will still run
    pass

# Import and register blueprints
from route.main_route import main_bp
from route.database_route import database_bp
from route.analysis_route import analysis_bp
from route.proposal_route import proposal_bp
from route.radio_source_route import radio_source_bp
from route.listen_route import listen_bp
from route.auth_route import auth_bp
from service.auth_service import AuthService

app.register_blueprint(blueprint=main_bp)
app.register_blueprint(blueprint=database_bp)
app.register_blueprint(blueprint=analysis_bp)
app.register_blueprint(blueprint=proposal_bp)
app.register_blueprint(blueprint=radio_source_bp)
app.register_blueprint(blueprint=listen_bp)
app.register_blueprint(blueprint=auth_bp)

# Initialize authentication (LoginManager)
AuthService(app)

# Db is created only by pyway migrations

if __name__ == '__main__':
    app.run(debug=True)