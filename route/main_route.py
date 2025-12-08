
from flask import Blueprint, render_template

from model.repository.radio_source_repository import RadioSourceRepository
from database import db

main_bp = Blueprint('main', __name__, url_prefix='/')

# Repository initialization functions
def get_radio_source_repo() -> RadioSourceRepository:
    return RadioSourceRepository(db.session)


@main_bp.route('/')
def index():
    """Main index page - list all radio sources."""
    radio_source_repo: RadioSourceRepository = get_radio_source_repo()
    sources = radio_source_repo.find_all()
    return render_template('index.html', sources=sources)