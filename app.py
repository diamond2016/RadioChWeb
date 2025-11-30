from flask import Flask
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key'  # Change in production
basedir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(basedir, 'instance')
os.makedirs(instance_dir, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_dir, "radio_sources.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import db from separate module
from database import db
db.init_app(app)

# Import and register blueprints
from route.database_routes import database_bp
from route.proposal_routes import proposal_bp
from route.radio_source_routes import radio_source_bp

app.register_blueprint(database_bp)
app.register_blueprint(proposal_bp, url_prefix='/proposal')
app.register_blueprint(radio_source_bp, url_prefix='/source')

# Db is created only by pyway migrations

if __name__ == '__main__':
    app.run(debug=True)